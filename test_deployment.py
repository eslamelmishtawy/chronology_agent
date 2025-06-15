#!/usr/bin/env python3
"""
Simple deployment test for Chronology Agent.
Tests core dependencies and Ollama connectivity.
"""

import os
import sys


def test_imports():
    """Test core imports."""
    print("📦 Testing core imports...")

    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

    try:
        import langchain
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False

    try:
        from langchain_ollama import ChatOllama
        print("✅ LangChain Ollama imported successfully")
    except ImportError as e:
        print(f"❌ LangChain Ollama import failed: {e}")
        return False

    return True


def test_ollama_connection():
    """Test Ollama connection."""
    print("\n🤖 Testing Ollama connection...")

    try:
        from langchain_ollama import ChatOllama

        # Try to initialize Ollama client
        llm = ChatOllama(
            model="qwen2.5:7b",
            temperature=0,
            num_ctx=4000,
        )
        print("✅ Ollama client initialized successfully")

        # Test basic query
        try:
            response = llm.invoke("Hello, respond with just 'OK'")
            response_text = response.content if hasattr(response, 'content') else str(response)
            print(f"✅ Ollama responded: {response_text}")
            return True
        except Exception as e:
            print(f"⚠️  Ollama connection issue: {e}")
            print("   Make sure Ollama is running and qwen2.5:7b model is available")
            return False

    except Exception as e:
        print(f"❌ Ollama initialization failed: {e}")
        return False


def test_app_modules():
    """Test app modules can be imported."""
    print("\n🔧 Testing app modules...")

    modules = [
        "document_reader",
        "document_analyzer",
        "document_formatter",
        "document_models",
        "reflection_agent"
    ]

    success = True
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} imported successfully")
        except ImportError as e:
            print(f"❌ {module} import failed: {e}")
            success = False

    return success


def main():
    """Run all tests."""
    print("🚀 Chronology Agent - Deployment Test (Ollama Only)")
    print("=" * 50)

    tests = [
        ("Core Imports", test_imports),
        ("App Modules", test_app_modules),
        ("Ollama Connection", test_ollama_connection),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All tests passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
