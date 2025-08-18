"""
Test DeepSeek Reasoner model specifically
"""
import sys
sys.path.append('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading')

from src.models import model_factory

def test_deepseek_models():
    print("🧪 Testing DeepSeek Models")
    print("=" * 50)
    
    # Test deepseek-chat first (we know this works)
    print("\n1️⃣ Testing deepseek-chat:")
    try:
        chat_model = model_factory.get_model("deepseek", "deepseek-chat")
        if chat_model:
            print("✅ deepseek-chat model obtained successfully")
            response = chat_model.generate_response(
                "You are a test assistant",
                "Say 'Hello from DeepSeek Chat!'",
                temperature=0.1,
                max_tokens=50
            )
            print(f"📝 Response: {response.content}")
        else:
            print("❌ Failed to get deepseek-chat model")
    except Exception as e:
        print(f"❌ Error with deepseek-chat: {e}")
    
    # Test deepseek-reasoner (the problematic one)
    print("\n2️⃣ Testing deepseek-reasoner:")
    try:
        reasoner_model = model_factory.get_model("deepseek", "deepseek-reasoner")
        if reasoner_model:
            print("✅ deepseek-reasoner model obtained successfully")
            response = reasoner_model.generate_response(
                "You are a test assistant",
                "Say 'Hello from DeepSeek Reasoner!'",
                temperature=0.1,
                max_tokens=50
            )
            print(f"📝 Response: {response.content}")
        else:
            print("❌ Failed to get deepseek-reasoner model")
    except Exception as e:
        print(f"❌ Error with deepseek-reasoner: {e}")
        import traceback
        print(f"🔍 Full traceback:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_deepseek_models()