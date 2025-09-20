#!/bin/bash
# Validation script for Oda-Bot Docker setup

echo "🔍 Validating Oda-Bot Docker Setup"
echo "=================================="

# Check if all required files exist
echo "📁 Checking required files..."
required_files=("Dockerfile" "docker-compose.yml" "docker-compose.prod.yml" ".dockerignore" ".env.example" "bot.py" "requirements.txt" "deploy.sh")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        exit 1
    fi
done

# Check if deploy.sh is executable
if [ -x "deploy.sh" ]; then
    echo "✅ deploy.sh is executable"
else
    echo "❌ deploy.sh is not executable"
    exit 1
fi

# Validate Python syntax
echo ""
echo "🐍 Validating Python syntax..."
if python -m py_compile bot.py; then
    echo "✅ bot.py syntax is valid"
else
    echo "❌ bot.py has syntax errors"
    exit 1
fi

# Check Docker syntax
echo ""
echo "🐳 Validating Docker configuration..."
if docker version > /dev/null 2>&1; then
    echo "✅ Docker is available"
    
    # Validate Dockerfile syntax (basic check)
    if grep -q "FROM python:" Dockerfile && grep -q "CMD.*python.*bot.py" Dockerfile; then
        echo "✅ Dockerfile looks valid"
    else
        echo "❌ Dockerfile may have issues"
        exit 1
    fi
    
    # Validate docker-compose syntax
    if command -v docker-compose > /dev/null 2>&1; then
        if docker-compose -f docker-compose.yml config > /dev/null 2>&1; then
            echo "✅ docker-compose.yml is valid"
        else
            echo "❌ docker-compose.yml has syntax errors"
            exit 1
        fi
        
        if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
            echo "✅ docker-compose.prod.yml is valid"
        else
            echo "❌ docker-compose.prod.yml has syntax errors"
            exit 1
        fi
    else
        echo "⚠️  docker-compose not available, skipping compose file validation"
    fi
else
    echo "⚠️  Docker not available, skipping Docker validation"
fi

# Check .env.example
echo ""
echo "🔐 Validating environment configuration..."
if grep -q "DISCORD_TOKEN=your_discord_bot_token_here" .env.example; then
    echo "✅ .env.example has placeholder token (secure)"
else
    echo "❌ .env.example may contain real token (security risk)"
    exit 1
fi

echo ""
echo "🎉 All validations passed!"
echo "🚀 Your Oda-Bot Docker setup is ready for deployment!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Add your Discord bot token to .env"
echo "3. Run ./deploy.sh to start the bot"