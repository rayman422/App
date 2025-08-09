#!/usr/bin/env python3
"""
Simple test script for mini_chat_all_in_one.py
Tests basic functionality without loading the full model.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    try:
        import torch
        print("✓ PyTorch imported successfully")
        print(f"  - Version: {torch.__version__}")
        print(f"  - CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  - CUDA version: {torch.version.cuda}")
    except ImportError as e:
        print(f"✗ PyTorch import failed: {e}")
        return False

    try:
        import transformers
        print("✓ Transformers imported successfully")
        print(f"  - Version: {transformers.__version__}")
    except ImportError as e:
        print(f"✗ Transformers import failed: {e}")
        return False

    try:
        import fastapi
        print("✓ FastAPI imported successfully")
        print(f"  - Version: {fastapi.__version__}")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False

    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
        print(f"  - Version: {uvicorn.__version__}")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False

    return True

def test_mini_chat_import():
    """Test that the mini_chat module can be imported."""
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Test importing specific components
        from mini_chat_all_in_one import safe_check, write_client_html, get_device
        
        print("✓ MiniChat components imported successfully")
        
        # Test utility functions
        assert safe_check("Hello world") == True
        assert safe_check("bomb") == False
        print("✓ Content filtering works")
        
        # Test device detection
        device = get_device()
        print(f"✓ Device detection: {device}")
        
        return True
        
    except Exception as e:
        print(f"✗ MiniChat import failed: {e}")
        return False

def test_html_generation():
    """Test HTML client generation."""
    try:
        from mini_chat_all_in_one import write_client_html
        
        # Test HTML generation
        test_path = "test_client.html"
        write_client_html(test_path)
        
        if os.path.exists(test_path):
            print("✓ HTML client generation works")
            os.remove(test_path)  # Clean up
            return True
        else:
            print("✗ HTML client generation failed")
            return False
            
    except Exception as e:
        print(f"✗ HTML generation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing MiniChat setup...\n")
    
    tests = [
        ("Module imports", test_imports),
        ("MiniChat import", test_mini_chat_import),
        ("HTML generation", test_html_generation),
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
        print("🎉 All tests passed! MiniChat is ready to use.")
        print("\nNext steps:")
        print("  python mini_chat_all_in_one.py --cli     # Run CLI mode")
        print("  python mini_chat_all_in_one.py --web     # Run web server")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())