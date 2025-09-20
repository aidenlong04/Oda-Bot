#!/usr/bin/env python3
"""
Oda Bot Deployment Verification Script
Run this script to verify your bot setup before deployment.
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is 3.8+"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is too old. Python 3.8+ required.")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    required_packages = ['discord', 'dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📥 Install missing packages with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Checking environment configuration...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Load and check for DISCORD_TOKEN
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            token = os.getenv('DISCORD_TOKEN')
            if token and token != 'your_token_here':
                print("✅ DISCORD_TOKEN is configured")
                if len(token) > 50:  # Discord tokens are typically ~59 characters
                    print("✅ DISCORD_TOKEN appears to be valid length")
                else:
                    print("⚠️  DISCORD_TOKEN seems too short - verify it's correct")
                return True
            else:
                print("❌ DISCORD_TOKEN not set or still using placeholder")
                return False
        except Exception as e:
            print(f"❌ Error loading .env file: {e}")
            return False
    else:
        print("❌ .env file not found")
        print("📝 Copy .env.example to .env and configure your bot token")
        return False

def check_bot_import():
    """Check if bot.py can be imported"""
    print("\n🤖 Checking bot import...")
    
    try:
        # Set a dummy token for import test
        os.environ['DISCORD_TOKEN'] = 'dummy_token_for_testing'
        
        spec = importlib.util.spec_from_file_location("bot", "bot.py")
        bot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot_module)
        
        print("✅ Bot imports successfully")
        return True
    except Exception as e:
        print(f"❌ Error importing bot: {e}")
        return False

def check_permissions():
    """Check file permissions"""
    print("\n🔒 Checking file permissions...")
    
    required_files = ['bot.py', 'requirements.txt', '.env']
    
    for file in required_files:
        if os.path.exists(file):
            if os.access(file, os.R_OK):
                print(f"✅ {file} is readable")
            else:
                print(f"❌ {file} is not readable")
                return False
        elif file != '.env':  # .env is checked separately
            print(f"❌ {file} not found")
            return False
    
    return True

def main():
    """Main verification function"""
    print("🔍 Oda Bot Deployment Verification")
    print("=" * 40)
    
    checks = [
        check_python_version,
        check_dependencies,
        check_environment,
        check_bot_import,
        check_permissions
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    print("\n" + "=" * 40)
    print("📊 Verification Summary:")
    
    if all(results):
        print("🎉 All checks passed! Your bot is ready for deployment.")
        print("\n🚀 Deployment options:")
        print("   • Docker: docker-compose up -d")
        print("   • Local: python3 bot.py")
        print("   • Linux service: ./setup-linux.sh")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())