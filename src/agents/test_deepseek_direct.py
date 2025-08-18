"""
Direct test of DeepSeek reasoner model
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_direct():
    print("🧪 Testing DeepSeek Models Directly")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("DEEPSEEK_KEY")
    if not api_key:
        print("❌ DEEPSEEK_KEY not found in environment")
        return
    
    print(f"✅ Found DEEPSEEK_KEY ({len(api_key)} chars)")
    
    # Initialize client
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    
    # Test deepseek-chat first
    print("\n1️⃣ Testing deepseek-chat:")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from DeepSeek Chat!'"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        print(f"✅ Success: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test deepseek-reasoner
    print("\n2️⃣ Testing deepseek-reasoner:")
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from DeepSeek Reasoner!'"}
            ],
            max_tokens=50,
            temperature=0.1
        )
        print(f"✅ Success: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"🔍 Error type: {type(e).__name__}")

if __name__ == "__main__":
    test_deepseek_direct()