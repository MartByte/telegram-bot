from groq import Groq

# Your specific API Key
client = Groq(api_key="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")

try:
    print("Connecting to Groq...")
    
    # Testing with the high-reasoning model
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Hello! I am a Computer Science student testing an API connection. Say 'Connection Successful' if you can hear me.",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    print("\n--- Groq Response ---")
    print(chat_completion.choices[0].message.content)
    print("----------------------")
    print("✅ TEST PASSED: Your API key is active and the model is responding.")

except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check if 'pip install groq' was successful.")
    print("2. Ensure your internet connection is stable.")
    print("3. Verify that your API key hasn't been revoked.")