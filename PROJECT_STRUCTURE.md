# 📁 Project Structure

## Optimal Directory Tree

```
hut_monitoring/
├── .github/
│   └── workflows/
│       └── check_hut.yml          GitHub Actions workflow
│
├── src/
│   └── check_hut.py               Main application script
│
├── config/
│   └── huts.yaml                  Hut configuration (user-editable)
│
├── docs/
│   ├── README.md                  Documentation index
│   ├── LOCAL_DEVELOPMENT.md       Setup guide for local development
│   ├── DEVELOPMENT_LOGGING.md     Logging and debugging reference
│   ├── VISUAL_DEBUG_GUIDE.md      Console output examples
│   ├── QUICK_REFERENCE.md         Quick command lookup
│   └── DOCUMENTATION_INDEX.md     Detailed documentation navigation
│
├── .env.local                     Local credentials (⚠️ git-ignored)
├── .gitignore                     Git exclusions
├── pyproject.toml                 Project dependencies and configuration
├── README.md                       Main project README
├── INSTALL.md                     Installation guide
│
├── venvHut/                        Virtual environment (git-ignored)
└── log/                            Runtime logs (created at first run, git-ignored)
    ├── hut_checker.log
    └── screenshots/
```

## Organization Principles

### 1. **Source Code** (`src/`)
- Contains only the main Python application
- Clean separation from configuration and documentation
- Easy to package and distribute

### 2. **Configuration** (`config/`)
- User-editable YAML file for hut targets
- Separate from code for flexibility
- Can be updated without touching the application

### 3. **Documentation** (`docs/`)
- All user-facing documentation centralized
- Easy to discover and maintain
- Organized by use case (setup, debugging, reference)

### 4. **CI/CD** (`.github/`)
- GitHub Actions workflow isolated
- Clear separation from application code
- Easy to maintain and update

### 5. **Project Root**
- Only essential files
- Configuration files (pyproject.toml, .gitignore)
- Main README and INSTALL guide
- Environment variables (.env.local)

## Git-Ignored Directories/Files

```
.env.local             Your local credentials
log/                   Runtime logs and screenshots
venvHut/              Python virtual environment
```

## Development Workflow

```
Developer clones repo
  ↓
Creates .env.local with credentials
  ↓
Installs: pip install -e .
  ↓
Runs: python src/check_hut.py
  ↓
Checks: log/hut_checker.log & log/screenshots/
  ↓
Debugs using docs/ guides if needed
```

## File Responsibilities

| File/Directory | Purpose | Editable |
|---|---|---|
| `src/check_hut.py` | Main logic with logging | ❌ (unless extending) |
| `config/huts.yaml` | Hut targets and dates | ✅ Yes |
| `.env.local` | Local credentials | ✅ Yes |
| `pyproject.toml` | Dependencies | ❌ (unless adding deps) |
| `.github/workflows/check_hut.yml` | CI/CD pipeline | ❌ (unless configuring) |
| `docs/` | All documentation | ✅ (keep updated) |
| `log/` | Runtime output | 🗑️ (can be deleted) |
| `venvHut/` | Virtual environment | 🗑️ (can be recreated) |

## Commands Reference

```bash
# Install dependencies
pip install -e .

# Run the application
python src/check_hut.py

# View logs
cat log/hut_checker.log

# View screenshots
ls log/screenshots/

# Clean up logs
rm -rf log/

# Recreate venv
rm -rf venvHut/
python -m venv venvHut/
source venvHut/bin/activate  # Linux/Mac
# or
venvHut\Scripts\activate      # Windows
pip install -e .
```

## Why This Structure?

✅ **Scalable** - Easy to add more scripts or modules to `src/`
✅ **Clear** - Each directory has a single responsibility
✅ **Professional** - Follows Python packaging conventions
✅ **Maintainable** - Easy to find and update any file
✅ **Documented** - Docs are centralized and discoverable
✅ **Safe** - Git-ignored sensitive and runtime files
✅ **Testable** - Source code isolated for easy testing

## Alternative Structures Considered

### Monolithic (Not chosen)
```
hut_monitoring/
├── check_hut.py
├── README.md
└── docs/
```
❌ Everything at root level, hard to scale

### Over-engineered (Not chosen)
```
hut_monitoring/
├── src/
│   ├── hut_monitoring/
│   │   ├── __init__.py
│   │   ├── checker.py
│   │   └── telegram.py
│   └── cli.py
├── tests/
├── docs/
└── setup.cfg
```
❌ Too complex for current project size

### Chosen Structure ✅
Balances **simplicity** with **scalability**

## Future Improvements

If the project grows, you can:
- Move `src/check_hut.py` → `src/hut_monitoring/main.py`
- Create `src/hut_monitoring/__init__.py`
- Add `tests/` directory
- Add `src/hut_monitoring/` submodules for different concerns

The current structure supports this growth seamlessly.
