#!/bin/bash

# CoopHive Safe Git Operations Script
# Prevents accidental file deletion during git operations

set -e  # Exit on any error

echo "🔒 CoopHive Safe Git Operations"
echo "================================"

# Function to verify project integrity
verify_integrity() {
    echo "🔍 Verifying project integrity..."
    python3 verify_project.py
    if [ $? -ne 0 ]; then
        echo "🚨 Project integrity check failed!"
        echo "❌ Aborting git operation to prevent data loss"
        exit 1
    fi
    echo "✅ Project integrity verified"
}

# Function to show git status safely
safe_status() {
    echo "📊 Current git status:"
    git status
}

# Function to safely add files
safe_add() {
    echo "📁 Adding files to git..."
    verify_integrity
    git add .
    echo "✅ Files added successfully"
}

# Function to safely commit
safe_commit() {
    if [ -z "$1" ]; then
        echo "❌ Error: Commit message required"
        echo "Usage: $0 commit \"Your commit message\""
        exit 1
    fi
    
    echo "💾 Preparing to commit: $1"
    verify_integrity
    git commit -m "$1"
    echo "✅ Commit successful"
}

# Function to safely push
safe_push() {
    echo "🚀 Preparing to push..."
    verify_integrity
    git push
    echo "✅ Push successful"
}

# Function to initialize repository
safe_init() {
    echo "🎯 Initializing git repository..."
    verify_integrity
    
    if [ ! -d ".git" ]; then
        git init
        echo "✅ Git repository initialized"
    else
        echo "ℹ️  Git repository already exists"
    fi
    
    # Add remote if provided
    if [ ! -z "$1" ]; then
        echo "🔗 Adding remote origin: $1"
        git remote add origin "$1" 2>/dev/null || git remote set-url origin "$1"
        echo "✅ Remote origin configured"
    fi
}

# Function to show help
show_help() {
    echo "CoopHive Safe Git Operations"
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  status          - Show git status"
    echo "  verify          - Verify project integrity"
    echo "  add             - Safely add files"
    echo "  commit \"msg\"    - Safely commit with message"
    echo "  push            - Safely push to remote"
    echo "  init [remote]   - Initialize repo with optional remote"
    echo "  help            - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 status"
    echo "  $0 add"
    echo "  $0 commit \"Initial commit\""
    echo "  $0 push"
    echo "  $0 init https://github.com/user/repo.git"
}

# Main script logic
case "$1" in
    "status")
        safe_status
        ;;
    "verify")
        verify_integrity
        ;;
    "add")
        safe_add
        ;;
    "commit")
        safe_commit "$2"
        ;;
    "push")
        safe_push
        ;;
    "init")
        safe_init "$2"
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

echo ""
echo "🎉 Operation completed successfully!"
