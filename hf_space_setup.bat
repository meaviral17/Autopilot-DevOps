@echo off
REM Setup script for Hugging Face Spaces deployment (Windows)

echo 🚀 Setting up AutoPilot DevOps for Hugging Face Spaces
echo ==================================================

REM Check if git is initialized
if not exist ".git" (
    echo 📦 Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit for Hugging Face Spaces"
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ❌ Error: requirements.txt not found!
    exit /b 1
)

REM Create .gitignore if it doesn't exist
if not exist ".gitignore" (
    echo 📝 Creating .gitignore...
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo env/
        echo venv/
        echo ENV/
        echo .venv
        echo.
        echo # Environment variables
        echo .env
        echo .env.local
        echo.
        echo # Logs
        echo *.log
        echo autopilot_devops.log
        echo.
        echo # Data files
        echo *.json
        echo !requirements.txt
        echo devops_preferences.json
        echo directory_structure.json
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo.
        echo # OS
        echo .DS_Store
        echo Thumbs.db
        echo.
        echo # Test
        echo .pytest_cache/
        echo .coverage
        echo htmlcov/
        echo.
        echo # Hugging Face
        echo .hf/
    ) > .gitignore
)

echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo 1. Create a Space on Hugging Face: https://huggingface.co/spaces
echo 2. Add remote: git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
echo 3. Push: git push huggingface main
echo 4. Set environment variables in Space settings
echo.
echo 📚 See DEPLOYMENT.md for detailed instructions

pause

