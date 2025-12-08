#!/usr/bin/env python3
"""
Setup Verification Script
Checks that all components are properly configured before running the app
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Verify Python version is 3.9+"""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.9+)")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    print("\n✓ Checking Python dependencies...")
    
    required_packages = {
        "streamlit": "streamlit",
        "snowflake.connector": "snowflake-connector-python",
        "tiktoken": "tiktoken"
    }
    
    all_installed = True
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"  ✅ {package} installed")
        except ImportError:
            print(f"  ❌ {package} NOT installed")
            all_installed = False
    
    if not all_installed:
        print("\n  Run: pip install -r requirements.txt")
    
    return all_installed


def check_files():
    """Check that all required files exist"""
    print("\n✓ Checking project files...")
    
    required_files = [
        "app.py",
        "orchestrator.py",
        "cost_tracker.py",
        "rcm_terminology.py",
        "config.py",
        "requirements.txt",
        ".streamlit/config.toml"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} NOT FOUND")
            all_exist = False
    
    return all_exist


def check_secrets():
    """Check if Snowflake secrets are configured"""
    print("\n✓ Checking Snowflake credentials...")
    
    secrets_path = Path(".streamlit/secrets.toml")
    if secrets_path.exists():
        print(f"  ✅ secrets.toml exists")
        
        # Check if it's not the example file
        content = secrets_path.read_text()
        if "your_snowflake_user" in content:
            print("  ⚠️  WARNING: secrets.toml contains placeholder values")
            print("     Please edit .streamlit/secrets.toml with your actual credentials")
            return False
        else:
            print("  ✅ secrets.toml appears configured")
            return True
    else:
        print(f"  ❌ secrets.toml NOT FOUND")
        print("     Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml")
        print("     Then edit with your Snowflake credentials")
        return False


def check_snowflake_setup():
    """Provide guidance on Snowflake prerequisites"""
    print("\n✓ Snowflake Prerequisites...")
    print("  ℹ️  Ensure you have completed these steps in Snowflake:")
    print("     1. Executed all 6 SQL setup scripts (01-06)")
    print("     2. Database RCM_AI_DEMO exists")
    print("     3. Schema RCM_SCHEMA exists")
    print("     4. Warehouse RCM_INTELLIGENCE_WH exists")
    print("     5. Role SF_INTELLIGENCE_DEMO has permissions")
    print("     6. Cortex Search services created")
    print("     7. Semantic views created")
    print("\n  Run this in Snowflake to verify:")
    print("     SHOW DATABASES LIKE 'RCM_AI_DEMO';")
    print("     SHOW WAREHOUSES LIKE 'RCM_INTELLIGENCE_WH';")
    print("     SHOW CORTEX SEARCH SERVICES IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;")
    print("     SHOW SEMANTIC VIEWS IN SCHEMA RCM_AI_DEMO.RCM_SCHEMA;")


def main():
    """Run all verification checks"""
    print("=" * 70)
    print("RCM Intelligence Hub - Setup Verification")
    print("=" * 70)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_files(),
        check_secrets()
    ]
    
    check_snowflake_setup()
    
    print("\n" + "=" * 70)
    if all(checks):
        print("✅ ALL CHECKS PASSED!")
        print("\nYou're ready to run the application:")
        print("  streamlit run app.py")
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the application.")
        print("Refer to QUICKSTART.md for detailed setup instructions.")
    print("=" * 70)
    
    return all(checks)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

