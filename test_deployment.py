"""
Simple test script to verify your Streamlit Cloud deployment setup.
Run this to check if all dependencies work correctly.
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported."""
    print("🧪 Testing imports...")
    
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
        from langchain_openai import ChatOpenAI
        print("✅ LangChain OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ LangChain OpenAI import failed: {e}")
        return False
    
    try:
        import pypdf
        print("✅ PyPDF imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF import failed: {e}")
        return False
    
    return True

def test_api_key():
    """Test if OpenAI API key is available."""
    print("\n🔑 Testing API key access...")
    
    # Try environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OpenAI API key found in environment")
        return True
    
    # Try streamlit secrets (this will only work in Streamlit context)
    try:
        import streamlit as st
        api_key = st.secrets["OPENAI_API_KEY"]
        if api_key:
            print("✅ OpenAI API key found in Streamlit secrets")
            return True
    except:
        pass
    
    print("❌ OpenAI API key not found")
    print("   Add OPENAI_API_KEY to your Streamlit Cloud secrets")
    return False

def test_openai_connection():
    """Test basic OpenAI connection."""
    print("\n🌐 Testing OpenAI connection...")
    
    try:
        from langchain_openai import ChatOpenAI
        
        # Try to initialize (don't call API yet)
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )
        print("✅ OpenAI client initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Chronology Agent Deployment Test\n")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("API Key Access", test_api_key),
        ("OpenAI Connection", test_openai_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your deployment should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("   Common solutions:")
        print("   - Add OPENAI_API_KEY to Streamlit Cloud secrets")
        print("   - Check requirements.txt has all dependencies")
        print("   - Restart your Streamlit Cloud app")

if __name__ == "__main__":
    main()
