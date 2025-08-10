#!/usr/bin/env python3
"""
Simple test script that doesn't require external dependencies.
Tests basic Python functionality and file operations.
"""

import os
import sys

def test_basic_python():
    """Test basic Python functionality."""
    print("✓ Python version:", sys.version)
    print("✓ Python executable:", sys.executable)
    return True

def test_file_operations():
    """Test file operations."""
    try:
        # Test reading the main file
        with open("mini_chat_all_in_one.py", "r") as f:
            content = f.read()
            if "class ModelWrapper" in content:
                print("✓ Main application file readable")
                return True
            else:
                print("✗ Main application file missing expected content")
                return False
    except Exception as e:
        print(f"✗ File operations failed: {e}")
        return False

def test_syntax():
    """Test that the main file has valid Python syntax."""
    try:
        with open("mini_chat_all_in_one.py", "r") as f:
            content = f.read()
            compile(content, "mini_chat_all_in_one.py", "exec")
            print("✓ Main application file has valid Python syntax")
            return True
    except SyntaxError as e:
        print(f"✗ Syntax error in main file: {e}")
        return False
    except Exception as e:
        print(f"✗ Failed to check syntax: {e}")
        return False

def test_requirements():
    """Test that requirements.txt exists and is readable."""
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
            if "torch" in requirements and "transformers" in requirements:
                print("✓ Requirements file contains expected packages")
                return True
            else:
                print("✗ Requirements file missing expected packages")
                return False
    except Exception as e:
        print(f"✗ Requirements file test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing MiniChat setup (basic tests)...\n")
    
    tests = [
        ("Basic Python", test_basic_python),
        ("File operations", test_file_operations),
        ("Python syntax", test_syntax),
        ("Requirements file", test_requirements),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✓ {test_name} passed\n")
        else:
            print(f"✗ {test_name} failed\n")
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Basic tests passed! MiniChat code is ready.")
        print("\nNext steps:")
        print("  1. Install system dependencies:")
        print("     sudo apt install python3.13-venv python3-pip")
        print("  2. Create virtual environment:")
        print("     python3 -m venv venv")
        print("  3. Activate and install requirements:")
        print("     source venv/bin/activate")
        print("     pip install -r requirements.txt")
        print("  4. Run the application:")
        print("     python3 mini_chat_all_in_one.py --cli")
        return 0
    else:
        print("❌ Some basic tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())