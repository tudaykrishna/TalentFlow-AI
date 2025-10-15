"""Test Azure OpenAI Connection"""
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Get credentials
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

print("=" * 60)
print("Testing Azure OpenAI Connection")
print("=" * 60)
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print(f"API Version: {api_version}")
print(f"API Key: {'*' * 8}...{api_key[-4:] if api_key else 'NOT SET'}")
print("=" * 60)

# Test connection
try:
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    print("\n✓ Client created successfully")
    
    # Test chat completion
    print("\nTesting chat completion...")
    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Connection successful!' if you can hear me."}
        ],
        max_tokens=50
    )
    
    print(f"\n✅ SUCCESS! Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"\nError type: {type(e).__name__}")
    
    # Check common issues
    print("\n" + "=" * 60)
    print("Troubleshooting Steps:")
    print("=" * 60)
    
    if "401" in str(e):
        print("❌ 401 Error - Authentication Failed")
        print("\nPossible causes:")
        print("1. Invalid API key")
        print("2. Wrong endpoint URL")
        print("3. Expired API key")
        print("4. Incorrect deployment name")
        print("\nChecking deployment name format...")
        if deployment:
            print(f"   Current: '{deployment}'")
            print(f"   Should NOT have quotes around it in .env file")
    
    elif "404" in str(e):
        print("❌ 404 Error - Resource Not Found")
        print("\nPossible causes:")
        print("1. Deployment name doesn't exist")
        print("2. Wrong endpoint URL")
        print(f"\nMake sure deployment '{deployment}' exists in Azure Portal")
    
    elif "429" in str(e):
        print("❌ 429 Error - Rate Limit")
        print("You've exceeded your quota. Check Azure Portal.")
    
    print("\n" + "=" * 60)
