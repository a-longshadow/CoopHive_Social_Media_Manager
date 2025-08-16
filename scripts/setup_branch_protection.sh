#!/bin/bash

# This script sets up branch protection rules for main and develop branches
# Requires GitHub CLI (gh) to be installed and authenticated

# Function to set up branch protection
setup_branch_protection() {
    local branch=$1
    
    echo "Setting up protection rules for $branch branch..."
    
    # Enable branch protection
    gh api \
      --method PUT \
      -H "Accept: application/vnd.github+json" \
      "/repos/a-longshadow/CoopHive_Social_Media_Manager/branches/$branch/protection" \
      -f required_status_checks='{"strict":true,"contexts":["test","lint"]}' \
      -f enforce_admins=true \
      -f required_pull_request_reviews='{"dismissal_restrictions":{},"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
      -f restrictions=null
}

# Set up protection for main branch
setup_branch_protection "main"

# Set up protection for develop branch
setup_branch_protection "develop"

echo "Branch protection rules have been set up successfully!"
