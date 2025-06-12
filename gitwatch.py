#!/usr/bin/env python3
"""
AutoPull - Automated Git Repository Monitoring and Deployment Tool

Usage:
    ./autopull.py              # Setup mode
    ./autopull.py --mode service    # Service mode
    ./autopull.py --help           # Show help
"""

import os
import sys
import time
import json
import subprocess
import argparse
import signal
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

CONFIG_FILE = ".autopull-config"
GITWATCH_LOG = "gitwatch.log"
CHECK_INTERVAL = 60  # seconds

class AutoPull:
    def __init__(self):
        self.config = {}
        self.running = True
        
    def log(self, message):
        """Print timestamped log message and append to log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        try:
            with open(GITWATCH_LOG, 'a', encoding='utf-8') as logf:
                logf.write(log_message + '\n')
        except Exception as e:
            print(f"[WARN] Failed to write to log file: {e}")
        
    def load_config(self):
        """Load configuration from file"""
        if not os.path.exists(CONFIG_FILE):
            return False
            
        try:
            with open(CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
            return True
        except Exception as e:
            self.log(f"Error loading config: {e}")
            return False
            
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
            os.chmod(CONFIG_FILE, 0o600)  # Secure permissions
            return True
        except Exception as e:
            self.log(f"Error saving config: {e}")
            return False
            
    def setup_mode(self):
        """Interactive setup mode"""
        self.log("AutoPull Setup Mode")
        print("=" * 50)
        
        # Check for existing configuration
        if self.load_config():
            self.log("Found existing configuration")
            print(f"Repository: {self.config.get('repo_owner', 'N/A')}/{self.config.get('repo_name', 'N/A')}")
            print(f"Branch: {self.config.get('branch', 'N/A')}")
            print(f"Local path: {self.config.get('local_path', 'N/A')}")
            print(f"Post-command: {self.config.get('post_command', 'None')}")
            
            reconfigure = input("\nReconfigure? (y/n): ").lower()
            if reconfigure != 'y':
                self.log("Using existing configuration")
                return True
            
            # Clear existing config for reconfiguration
            self.config = {}
        
        # Get GitHub token
        print("\nGitHub Personal Access Token is required.")
        print("Create one at: https://github.com/settings/tokens")
        print("Required permissions: 'repo' (for private repos) or 'public_repo' (for public repos)")
        
        while True:
            token = input("\nEnter your GitHub Personal Access Token: ").strip()
            if token:
                self.config['github_token'] = token
                break
            print("Token cannot be empty!")
            print("\nGitHub Personal Access Token is required.")
            print("Create one at: https://github.com/settings/tokens")
            print("Required permissions: 'repo' (for private repos) or 'public_repo' (for public repos)")
            
            while True:
                token = input("\nEnter your GitHub Personal Access Token: ").strip()
                if token:
                    self.config['github_token'] = token
                    break
                print("Token cannot be empty!")
        
        # Get repository URL
        while True:
            repo_url = input("\nEnter GitHub repository URL (https://github.com/user/repo): ").strip()
            if repo_url:
                # Extract owner/repo from URL
                try:
                    if 'github.com/' in repo_url:
                        parts = repo_url.rstrip('/').split('/')
                        if len(parts) >= 2:
                            owner = parts[-2]
                            repo = parts[-1].replace('.git', '')
                            self.config['repo_owner'] = owner
                            self.config['repo_name'] = repo
                            self.config['repo_url'] = repo_url
                            break
                except:
                    pass
            print("Please enter a valid GitHub repository URL!")
        
        # Get local repository path
        current_dir = os.getcwd()
        default_path = input(f"\nLocal repository path (default: {current_dir}): ").strip()
        self.config['local_path'] = default_path if default_path else current_dir
        
        # Get post-pull command
        post_command = input("\nPost-pull command (e.g., 'npm run build', leave empty for none): ").strip()
        self.config['post_command'] = post_command if post_command else None
        
        # Get branch to monitor
        branch = input("\nBranch to monitor (default: main): ").strip()
        self.config['branch'] = branch if branch else 'main'
        
        # Verify repository exists and is accessible
        if self.verify_repository():
            if self.save_config():
                self.log("Configuration saved successfully!")
                print(f"\nSetup complete! Run '{sys.argv[0]} --mode service' to start monitoring.")
            else:
                self.log("Error: Failed to save configuration")
                return False
        else:
            self.log("Error: Could not access repository. Please check your settings.")
            return False
            
        return True
        
    def verify_repository(self):
        """Verify that the repository is accessible"""
        try:
            headers = {'Authorization': f'token {self.config["github_token"]}'}
            url = f"https://api.github.com/repos/{self.config['repo_owner']}/{self.config['repo_name']}"
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                self.log("Repository access verified ✓")
                return True
            elif response.status_code == 404:
                self.log("Error: Repository not found or access denied")
            else:
                self.log(f"Error: GitHub API returned status {response.status_code}")
                
        except Exception as e:
            self.log(f"Error verifying repository: {e}")
            
        return False
        
    def get_latest_commit_sha(self):
        """Get the latest commit SHA from GitHub"""
        try:
            headers = {'Authorization': f'token {self.config["github_token"]}'}
            url = f"https://api.github.com/repos/{self.config['repo_owner']}/{self.config['repo_name']}/commits/{self.config['branch']}"
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                commit_data = response.json()
                return commit_data['sha']
            else:
                self.log(f"Error fetching commit: HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"Error getting latest commit: {e}")
            
        return None
        
    def run_command(self, command, cwd=None):
        """Run a shell command and return success status"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd or self.config['local_path'],
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except Exception as e:
            return False, str(e)
            
    def pull_repository(self):
        """Pull latest changes from repository"""
        self.log("Pulling latest changes...")
        
        # Ensure we're in a git repository
        if not os.path.exists(os.path.join(self.config['local_path'], '.git')):
            self.log("Not a git repository. Cloning...")
            success, output = self.run_command(f"git clone {self.config['repo_url']} .", cwd=self.config['local_path'])
            if not success:
                self.log(f"Clone failed: {output}")
                return False
        
        # Pull changes
        success, output = self.run_command(f"git pull origin {self.config['branch']}")
        if success:
            self.log("Pull successful ✓")
            
            # Run post-pull command if specified
            if self.config.get('post_command'):
                self.log(f"Running post-pull command: {self.config['post_command']}")
                success, output = self.run_command(self.config['post_command'])
                if success:
                    self.log("Post-pull command completed ✓")
                else:
                    self.log(f"Post-pull command failed: {output}")
            
            return True
        else:
            self.log(f"Pull failed: {output}")
            return False
            
    def service_mode(self):
        """Run in service mode - continuously monitor for changes"""
        if not self.load_config():
            self.log("Error: No configuration found. Run setup first.")
            return False
            
        self.log("Starting AutoPull service mode")
        self.log(f"Monitoring: {self.config['repo_owner']}/{self.config['repo_name']} ({self.config['branch']})")
        self.log(f"Check interval: {CHECK_INTERVAL} seconds")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        last_commit_sha = None
        
        while self.running:
            try:
                current_commit_sha = self.get_latest_commit_sha()
                
                if current_commit_sha:
                    if last_commit_sha is None:
                        # First run - just record the current commit
                        last_commit_sha = current_commit_sha
                        self.log(f"Initial commit: {current_commit_sha[:8]}")
                    elif current_commit_sha != last_commit_sha:
                        # New commit detected
                        self.log(f"New commit detected: {current_commit_sha[:8]}")
                        if self.pull_repository():
                            last_commit_sha = current_commit_sha
                            self.log("Update completed successfully ✓")
                        else:
                            self.log("Update failed ✗")
                    # else: no changes
                else:
                    self.log("Failed to check for updates")
                
                # Wait before next check
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"Unexpected error: {e}")
                time.sleep(CHECK_INTERVAL)
        
        self.log("AutoPull service stopped")
        return True
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.log("Received shutdown signal, stopping...")
        self.running = False

def main():
    parser = argparse.ArgumentParser(
        description="AutoPull - Automated Git Repository Monitoring Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./autopull.py              # Run setup mode
  ./autopull.py --mode service    # Start service mode
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['service'], 
        help='Run mode (default: setup if no config exists)'
    )
    
    args = parser.parse_args()
    
    autopull = AutoPull()
    
    if args.mode == 'service':
        if not autopull.service_mode():
            sys.exit(1)
    else:
        # Setup mode (default)
        if not autopull.setup_mode():
            sys.exit(1)

if __name__ == "__main__":
    main()