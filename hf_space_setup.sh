#!/bin/bash
# Setup script for Hugging Face Spaces deployment

echo "🚀 Setting up AutoPilot DevOps for Hugging Face Spaces"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit for Hugging Face Spaces"
fi

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Environment variables
.env
.env.local

# Logs
*.log
autopilot_devops.log

# Data files
*.json
!requirements.txt
devops_preferences.json
directory_structure.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test
.pytest_cache/
.coverage
htmlcov/

# Hugging Face
.hf/
EOF
fi

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a Space on Hugging Face: https://huggingface.co/spaces"
echo "2. Add remote: git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME"
echo "3. Push: git push huggingface main"
echo "4. Set environment variables in Space settings"
echo ""
echo "📚 See DEPLOYMENT.md for detailed instructions"

