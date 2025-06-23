#!/bin/bash

# Noah Eco System Deployment Script
echo "🚀 Noah Eco System Deployment Script"
echo "====================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Get commit message from user or use default
    if [ -z "$1" ]; then
        COMMIT_MSG="Deploy to Render with SQLite - $(date)"
    else
        COMMIT_MSG="$1"
    fi
    
    echo "💾 Committing changes..."
    git commit -m "$COMMIT_MSG"
    echo "✅ Changes committed with message: $COMMIT_MSG"
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "🔗 Please add your GitHub repository as remote origin:"
    echo "   git remote add origin <your-github-repo-url>"
    echo ""
    echo "📋 Then run: git push -u origin main"
else
    echo "🚀 Pushing to GitHub..."
    git push origin main
    echo "✅ Code pushed to GitHub!"
    echo ""
    echo "🎉 Next steps:"
    echo "1. Go to https://dashboard.render.com"
    echo "2. Click 'New +' → 'Blueprint'"
    echo "3. Connect your GitHub repository"
    echo "4. Render will automatically detect render.yaml"
    echo "5. Click 'Apply' to deploy"
    echo ""
    echo "💡 Note: This app uses SQLite database (no external database needed)"
fi

echo ""
echo "📚 For manual deployment instructions, see README.md" 