# 🛡️ Safe Commit Guide - NEVER DELETE CRITICAL FILES

## ⚠️ CRITICAL WARNING

This project has experienced **accidental file deletion** during git operations. This guide ensures **100% protection** against data loss during commits.

## 🔒 MANDATORY PRE-COMMIT CHECKLIST

**BEFORE ANY GIT OPERATION, VERIFY:**

### ✅ Step 1: Run Project Integrity Check
```bash
# ALWAYS run this first - it checks all critical files exist
python3 verify_project.py
```

**Expected Output:**
```
✅ PROJECT INTEGRITY VERIFIED!
   All critical files and directories are present.
   Safe to proceed with git operations.
```

**If you see ANY ❌ marks, STOP and restore missing files before proceeding.**

### ✅ Step 2: Use Safe Git Commands ONLY
```bash
# Use these protected commands instead of raw git:
./safe_git.sh status    # Check status safely
./safe_git.sh add       # Add files with verification
./safe_git.sh commit "Your message"  # Commit with protection
./safe_git.sh push      # Push with verification
```

### ✅ Step 3: Verify Critical Files Exist
**These files MUST NEVER be deleted:**

#### 🔥 CRITICAL DJANGO FILES
- `manage.py` - **Project will not run without this**
- `coophive/settings.py` - **Core Django configuration**
- `coophive/urls.py` - **URL routing**
- `coophive/wsgi.py` - **WSGI application**
- `coophive/asgi.py` - **ASGI application**
- `coophive/__init__.py` - **Python package marker**

#### 🔥 CRITICAL APP FILES
**user_account_manager/** (Authentication System)
- `user_account_manager/models.py` - **User models and auth**
- `user_account_manager/views.py` - **Authentication views**
- `user_account_manager/urls.py` - **Auth URL patterns**
- `user_account_manager/apps.py` - **App configuration**
- `user_account_manager/__init__.py` - **Package marker**

**core/** (Core Functionality)
- `core/models.py` - **Base models (Post, Campaign, etc.)**
- `core/urls.py` - **Core URL patterns**
- `core/views.py` - **Core views**
- `core/__init__.py` - **Package marker**

**app_settings/** (Configuration System)
- `app_settings/models.py` - **Database-first settings**
- `app_settings/__init__.py` - **Package marker**

**twitter/** (Primary Platform Integration)
- `twitter/models.py` - **Twitter models and n8n integration**
- `twitter/views.py` - **Twitter views and API endpoints**
- `twitter/urls.py` - **Twitter URL patterns**
- `twitter/__init__.py` - **Package marker**

#### 🔥 CRITICAL PROJECT FILES
- `requirements.txt` - **Python dependencies**
- `templates/base.html` - **Base template**

### ✅ Step 4: Check for Accidental Deletions
```bash
# Check if any files are staged for deletion
git diff --cached --name-only --diff-filter=D

# If this shows ANY critical files, ABORT and restore them
```

## 🚨 PROTECTION SYSTEMS IN PLACE

### 1. Pre-Commit Hook
**Location:** `.git/hooks/pre-commit`
- **Automatically runs before EVERY commit**
- **Blocks commits that delete critical files**
- **Cannot be bypassed**

### 2. Project Integrity Verification
**Location:** `verify_project.py`
- **Checks all critical files exist**
- **Comprehensive file and directory validation**
- **Must pass before any git operation**

### 3. Safe Git Wrapper
**Location:** `safe_git.sh`
- **Wraps all git operations with safety checks**
- **Verifies integrity before every command**
- **User-friendly interface with built-in protection**

## 🚫 NEVER DO THESE THINGS

### ❌ NEVER use raw git commands:
```bash
# DON'T DO THIS:
git add .
git commit -m "message"
git push

# DO THIS INSTEAD:
./safe_git.sh add
./safe_git.sh commit "message"  
./safe_git.sh push
```

### ❌ NEVER bypass the pre-commit hook:
```bash
# DON'T DO THIS:
git commit --no-verify

# The hook exists to protect you!
```

### ❌ NEVER ignore integrity check failures:
```bash
# If verify_project.py shows ❌ marks, DON'T PROCEED
# Fix the missing files first!
```

## 🔧 EMERGENCY RECOVERY

### If Files Are Accidentally Deleted:

#### 1. Check Git History
```bash
# See what files were deleted in last commit
git show --name-only --diff-filter=D HEAD

# Restore from previous commit
git checkout HEAD~1 -- path/to/deleted/file
```

#### 2. Check Backup
```bash
# Look for backup directories
ls -la /Users/joe/Documents/CoopHive_Social_Media_Manager_BACKUP_*
```

#### 3. Use File Recovery
The following files contain the complete project structure and can be used for recovery:
- `docs/cursor_familiarize_with_the_django_proj.md` (if it exists)
- Previous git commits
- Backup directories

## 📋 COMMIT WORKFLOW

### Safe Commit Process:
```bash
# 1. Verify project integrity
python3 verify_project.py
# Must show: ✅ PROJECT INTEGRITY VERIFIED!

# 2. Check current status
./safe_git.sh status

# 3. Add files safely
./safe_git.sh add

# 4. Commit with protection
./safe_git.sh commit "Your descriptive commit message"

# 5. Push safely
./safe_git.sh push
```

### What Happens During Safe Commit:
1. **Project integrity check** - Verifies all critical files exist
2. **Pre-commit hook runs** - Blocks deletion of critical files
3. **Commit proceeds** - Only if all checks pass
4. **Success confirmation** - All files protected

## 🎯 COMMIT MESSAGE GUIDELINES

### Good Commit Messages:
```bash
./safe_git.sh commit "Add Twitter n8n integration API endpoints"
./safe_git.sh commit "Fix Google OAuth domain restriction handling"
./safe_git.sh commit "Update documentation for safe git workflow"
```

### Bad Commit Messages:
```bash
./safe_git.sh commit "fix stuff"
./safe_git.sh commit "update"
./safe_git.sh commit "changes"
```

## 📊 VERIFICATION COMMANDS

### Before Any Git Operation:
```bash
# Check project integrity
python3 verify_project.py

# Verify Django can start
python manage.py check

# Test critical imports
python manage.py shell -c "
from user_account_manager.models import User
from core.models import Post
from twitter.models import TwitterPost
print('✅ All critical models import successfully')
"
```

## 🚨 RED FLAGS - STOP IMMEDIATELY

**If you see ANY of these, STOP and investigate:**

- ❌ `verify_project.py` shows missing files
- ❌ Pre-commit hook shows deletion warnings
- ❌ `python manage.py check` fails
- ❌ Import errors in Django shell
- ❌ Server won't start after commit

## 📞 TROUBLESHOOTING

### Problem: Pre-commit hook blocks commit
**Solution:** This is working correctly! Check what files are being deleted and restore them.

### Problem: verify_project.py shows missing files
**Solution:** Restore the missing files from git history or backup before proceeding.

### Problem: Django won't start after commit
**Solution:** Roll back the commit and restore missing files.

## 🎉 SUCCESS INDICATORS

**You know it's safe when:**
- ✅ `verify_project.py` shows all files present
- ✅ Pre-commit hook allows the commit
- ✅ `python manage.py check` passes
- ✅ Django server starts successfully
- ✅ All imports work in Django shell

## 📝 FINAL REMINDER

**The protection systems are there for a reason!**

- **Trust the verification scripts** - they prevent data loss
- **Use safe git commands** - they include built-in protection
- **Never bypass the hooks** - they catch dangerous operations
- **When in doubt, check twice** - better safe than sorry

**This guide exists because files HAVE been accidentally deleted before. Following these procedures ensures it will NEVER happen again.**

---

**🛡️ Remember: Better to be paranoid and keep your files than to be careless and lose your work!**
