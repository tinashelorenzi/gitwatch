# AutoPull: Automated GitHub Repository Watcher & Deployment Tool

**AutoPull** is a Python script that automatically monitors a GitHub repository for new commits and keeps your local copy up to date. It can also run custom post-pull commands (like build or deployment scripts) after updates. Perfect for developers, sysadmins, and anyone who needs continuous deployment or automated GitHub repo syncing.

---

## 🚀 Features

- **Automated Git Pull**: Monitors your chosen GitHub repository and branch for new commits and pulls changes automatically.
- **Auto-Sync Local Repo**: Keeps your local directory in sync with the remote GitHub repository.
- **Post-Pull Automation**: Optionally run any command (e.g., build, deploy) after pulling updates.
- **Easy Setup**: Interactive configuration wizard for first-time setup.
- **Service Mode**: Runs as a background service, checking for updates at regular intervals.
- **Secure**: Stores your GitHub token securely and uses it for private/public repo access.
- **Cross-Platform**: Works on Linux, macOS, and Windows (Python 3 required).
- **Action Logging**: All actions and events are logged to `gitwatch.log` for compliance and debugging.

---

## 🔍 Use Cases & Keywords
- Automated git pull script
- GitHub repository auto-sync
- Auto-update local repo from GitHub
- Post-pull deployment/build automation
- Python git watcher/monitor
- Continuous deployment from GitHub
- GitHub webhook alternative

---

## 🛠️ Installation

1. **Clone this repository or download `gitwatch.py`:**
   ```bash
   git clone https://github.com/tinashelorenzi/gitwatch
   cd gitwatch
   # or just download gitwatch.py
   ```
2. **Install Python 3** (if not already installed).
3. **Install required Python packages:**
   ```bash
   pip install requests
   ```

---

## ⚡ Usage

### 1. Setup Mode (First Run)
Run the script to configure your repository, branch, local path, and post-pull command:
```bash
python gitwatch.py
```
- Enter your GitHub Personal Access Token ([create one here](https://github.com/settings/tokens)).
- Enter the repository URL (e.g., `https://github.com/user/repo`).
- Choose the branch to monitor (default: `main`).
- Set the local path for the repo (default: current directory).
- Optionally, specify a post-pull command (e.g., `npm run build`).

### 2. Testing Mode (Verify Setup)
Before running as a service, you can verify your configuration and environment:
```bash
python gitwatch.py --mode testing
```
- This mode checks your configuration, verifies GitHub access, fetches the latest commit, simulates a git pull (dry-run), and simulates the post-pull command (without executing it).
- All results and any errors are printed and logged to `gitwatch.log`.
- Use this mode to ensure everything is set up correctly before relying on AutoPull as a service.

### 3. Service Mode (Continuous Monitoring)
After setup and testing, start the watcher in service mode:
```bash
python gitwatch.py --mode service
```
- The script will check for new commits every 60 seconds and auto-pull changes.
- All actions and events are logged to `gitwatch.log` in the script directory for compliance and debugging.
- If a post-pull command is set, it will run after each update.

---

## ⚙️ Configuration
- All settings are saved in `.autopull-config` in the script directory.
- To reconfigure, simply run the script again and choose to reconfigure when prompted.

---

## 📦 Requirements
- Python 3.6+
- `requests` Python package
- `git` command-line tool installed and available in your PATH

---

## 🐞 Troubleshooting
- **Permission denied or token errors:** Ensure your GitHub token has the correct permissions (`repo` for private, `public_repo` for public repos).
- **Not a git repository:** The script will attempt to clone if the local path is not a git repo.
- **Post-pull command fails:** Check your command syntax and environment.
- **Check logs:** Review `gitwatch.log` for a detailed record of actions and errors.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.

---

## 🙋‍♂️ Contributing & Support
Pull requests and issues are welcome! For questions, open an issue or contact the maintainer.

---

**Keywords:** automated git pull, github repo sync, auto-update local repo, post-pull deployment, python git watcher, continuous deployment, git monitor, github webhook alternative 