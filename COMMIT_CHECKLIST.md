# 🛡️ COMMIT SAFETY CHECKLIST

## ⚠️ BEFORE EVERY COMMIT - NO EXCEPTIONS!

### ✅ Step 1: Verify Project Integrity
```bash
python3 verify_project.py
```
**Must show:** `✅ PROJECT INTEGRITY VERIFIED!`

### ✅ Step 2: Use Safe Git Commands ONLY
```bash
./safe_git.sh status     # Check status
./safe_git.sh add        # Add files  
./safe_git.sh commit "message"  # Commit safely
./safe_git.sh push       # Push safely
```

### ✅ Step 3: Check No Critical Files Being Deleted
```bash
git diff --cached --name-only --diff-filter=D
```
**Must be empty** or show only non-critical files

## 🔥 CRITICAL FILES - NEVER DELETE
- `manage.py`
- `coophive/settings.py`
- `coophive/urls.py`
- `user_account_manager/models.py`
- `core/models.py`
- `app_settings/models.py`
- `twitter/models.py`
- `requirements.txt`

## 🚨 RED FLAGS - STOP IMMEDIATELY
- ❌ `verify_project.py` shows missing files
- ❌ Pre-commit hook blocks commit
- ❌ `python manage.py check` fails

## 📞 EMERGENCY
If files deleted: `git checkout HEAD~1 -- path/to/file`

**Read full guide:** `docs/SAFE_COMMIT_GUIDE.md`
