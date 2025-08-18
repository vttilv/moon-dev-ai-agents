"""
Test the chat agent without AI - only 777 responses
"""

import sys
from pathlib import Path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.agents.chat_agent import ChatAgent

def test_777_response():
    """Test that 777 gets a quote/verse response"""
    agent = ChatAgent()
    
    # Test 777 response
    response = agent.process_question("TestUser", "777")
    print(f"777 Response: {response}")
    assert response and response.startswith("777"), "Should get 777 response"
    
    # Test normal message
    response = agent.process_question("TestUser", "Hello everyone!")
    print(f"Normal message response: {response}")
    assert response == True, "Normal messages should return True"
    
    # Test another 777
    response = agent.process_question("AnotherUser", "777")
    print(f"Another 777 Response: {response}")
    assert response and response.startswith("777"), "Should get 777 response"
    
    print("\n✅ All tests passed! Chat agent works without AI.")

if __name__ == "__main__":
    test_777_response()