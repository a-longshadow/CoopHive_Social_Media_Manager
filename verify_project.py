#!/usr/bin/env python3
"""
CoopHive Project Integrity Verification Script
Ensures all critical files exist before git operations
"""

import os
import sys
from pathlib import Path

# Critical files that MUST exist for the Django project to work
CRITICAL_FILES = [
    'manage.py',
    'coophive/settings.py',
    'coophive/urls.py',
    'coophive/wsgi.py',
    'coophive/asgi.py',
    'coophive/__init__.py',
    'user_account_manager/models.py',
    'user_account_manager/views.py',
    'user_account_manager/urls.py',
    'user_account_manager/apps.py',
    'user_account_manager/__init__.py',
    'core/models.py',
    'core/urls.py',
    'core/views.py',
    'core/__init__.py',
    'app_settings/models.py',
    'app_settings/__init__.py',
    'twitter/models.py',
    'twitter/views.py',
    'twitter/urls.py',
    'twitter/__init__.py',
    'requirements.txt',
    'templates/base.html',
]

# Critical directories that must exist
CRITICAL_DIRS = [
    'user_account_manager/',
    'core/',
    'app_settings/',
    'twitter/',
    'linkedin/',
    'farcaster/',
    'bluesky/',
    'templates/',
    'static/',
    'docs/',
]

def check_project_integrity():
    """Check if all critical files and directories exist."""
    print("🔍 CoopHive Project Integrity Check")
    print("=" * 50)
    
    missing_files = []
    missing_dirs = []
    
    # Check critical files
    print("\n📄 Checking critical files...")
    for file_path in CRITICAL_FILES:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"   ❌ MISSING: {file_path}")
        else:
            print(f"   ✅ OK: {file_path}")
    
    # Check critical directories
    print("\n📁 Checking critical directories...")
    for dir_path in CRITICAL_DIRS:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
            print(f"   ❌ MISSING: {dir_path}")
        else:
            print(f"   ✅ OK: {dir_path}")
    
    # Report results
    print("\n" + "=" * 50)
    if missing_files or missing_dirs:
        print("🚨 PROJECT INTEGRITY FAILED!")
        print(f"   Missing files: {len(missing_files)}")
        print(f"   Missing directories: {len(missing_dirs)}")
        print("\n💡 DO NOT COMMIT UNTIL ALL FILES ARE RESTORED!")
        return False
    else:
        print("✅ PROJECT INTEGRITY VERIFIED!")
        print("   All critical files and directories are present.")
        print("   Safe to proceed with git operations.")
        return True

def main():
    """Main function."""
    if not check_project_integrity():
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
