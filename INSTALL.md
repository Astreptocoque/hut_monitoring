# Installation Guide

This guide provides instructions for setting up the Hut Monitoring project using Python's `venv` virtual environment manager.

## Prerequisites

- **Python 3.8+** installed on your system
- **pip** package manager (usually comes with Python)
- **git** (optional, for cloning the repository)

To check if Python is installed, run:
```bash
python --version
```

---

## Setup Instructions

### Step 1: Clone or Download the Project

**Using Git**
```bash
git clone https://github.com/astreptocoque/hut_monitoring.git
cd hut-monitoring
```

---

### Step 2: Create a Virtual Environment

Navigate to the project directory and run:

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

After activation, your terminal prompt should show `(venv)` at the beginning.

---

### Step 3: Upgrade pip

Ensure you have the latest version of pip:

**On macOS/Linux:**
```bash
python -m pip install --upgrade pip
```

**On Windows:**
```cmd
python -m pip install --upgrade pip
```

---

### Step 4: Install Requirements

Install all project dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or, if you want to use the `pyproject.toml` configuration:

```bash
pip install -e .
```

For development dependencies (testing, formatting, type checking):

```bash
pip install -e ".[dev]"
```

---

### Step 5: Run the Project

Once the virtual environment is activated and dependencies are installed, you can run the project:

```bash
python src/server/check_hut.py
```

---

## Deactivating the Virtual Environment

When you're done working on the project, deactivate the virtual environment:

```bash
deactivate
```

Your terminal prompt will return to normal.

---

## Troubleshooting

### "Python not found" or "command not found"
- Ensure Python is installed and added to your system PATH
- Try using `python3` instead of `python` on macOS/Linux
- Restart your terminal after installing Python

### Virtual environment not activating
- Make sure you're in the project directory
- Check that the `venv` folder exists
- Try running the activate command with the full path

### pip permission denied
- On Windows: try running Command Prompt as Administrator
- On macOS/Linux: use `pip install --user` or ensure venv is properly activated

### Import errors when running the project
- Ensure the virtual environment is activated (you should see `(venv)` in your prompt)
- Verify all dependencies were installed: `pip list`
- Reinstall requirements: `pip install --upgrade -r requirements.txt`

---

## Additional Information

### Project Structure
```
hut-monitoring/
├── INSTALL.md              # This file
├── README.md               # Project overview
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
├── src/
│   └── server/
│       ├── check_hut.py    # Main script
│       └── check_hut.yml   # GitHub Actions workflow config
└── venv/                   # Virtual environment (created in Step 2)
```

### Reinstalling from Scratch

If you want to start over:

```bash
# Remove the old virtual environment
rm -rf venv  # macOS/Linux
rmdir /s venv  # Windows

# Then repeat Steps 2-4
```

---

## Next Steps

1. Set up your Telegram Bot (see README.md)
2. Configure GitHub Actions with your credentials
3. Run the script locally to test before deploying to GitHub Actions

For more details, see the main [README.md](README.md).
