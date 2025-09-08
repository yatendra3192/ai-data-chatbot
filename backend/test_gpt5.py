import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_gpt5():
    """Test if GPT-5 is available and working"""
    
    print("Testing GPT-5 availability...")
    print("-" * 50)
    
    try:
        # Try GPT-5 with reasoning_effort parameter
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "developer", "content": "You are a helpful assistant that answers concisely."},
                {"role": "user", "content": "What is 2+2? Answer with just the number."}
            ],
            reasoning_effort="low",  # Low effort for simple task
            max_completion_tokens=100
        )
        
        print("[SUCCESS] GPT-5 is available!")
        print(f"Response: {response.choices[0].message.content}")
        print(f"Model used: {response.model}")
        
        # Test with different reasoning efforts
        print("\nTesting different reasoning efforts...")
        
        for effort in ["minimal", "low", "medium", "high"]:
            try:
                response = client.chat.completions.create(
                    model="gpt-5",
                    messages=[
                        {"role": "developer", "content": "You are a data analyst."},
                        {"role": "user", "content": f"Calculate 10 * {effort[0]}"}
                    ],
                    reasoning_effort=effort,
                    max_completion_tokens=100
                )
                print(f"  {effort}: [OK] Working")
            except Exception as e:
                print(f"  {effort}: [FAIL] Error - {str(e)[:50]}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] GPT-5 is not available")
        print(f"Error: {e}")
        
        # Try fallback to GPT-4o
        print("\nTrying GPT-4o as fallback...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 2+2?"}
                ],
                temperature=0.1,
                max_tokens=100
            )
            print("[SUCCESS] GPT-4o is working as fallback")
            print(f"Response: {response.choices[0].message.content}")
            return False
            
        except Exception as e2:
            print(f"[FAIL] GPT-4o also failed: {e2}")
            return False

if __name__ == "__main__":
    test_gpt5()