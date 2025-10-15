"""Test LangChain AzureChatOpenAI Connection"""
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Load environment variables
load_dotenv()

# Get credentials
api_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

print("=" * 60)
print("Testing LangChain AzureChatOpenAI Connection")
print("=" * 60)
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print(f"API Version: {api_version}")
print(f"API Key: {'*' * 8}...{api_key[-4:] if api_key else 'NOT SET'}")
print("=" * 60)

# Test Method 1: Using deployment_name (as in current code)
print("\n[Test 1] Using deployment_name parameter...")
try:
    model1 = AzureChatOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
        deployment_name=deployment,
        temperature=0.3
    )
    
    response1 = model1.invoke("Say 'Test 1 works!'")
    print(f"✅ SUCCESS with deployment_name: {response1.content}")
    
except Exception as e:
    print(f"❌ FAILED with deployment_name: {e}")

# Test Method 2: Using azure_deployment parameter
print("\n[Test 2] Using azure_deployment parameter...")
try:
    model2 = AzureChatOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_deployment=deployment,
        temperature=0.3
    )
    
    response2 = model2.invoke("Say 'Test 2 works!'")
    print(f"✅ SUCCESS with azure_deployment: {response2.content}")
    
except Exception as e:
    print(f"❌ FAILED with azure_deployment: {e}")

# Test Method 3: Using openai_api_key
print("\n[Test 3] Using openai_api_key parameter...")
try:
    model3 = AzureChatOpenAI(
        openai_api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint,
        azure_deployment=deployment,
        temperature=0.3
    )
    
    response3 = model3.invoke("Say 'Test 3 works!'")
    print(f"✅ SUCCESS with openai_api_key: {response3.content}")
    
except Exception as e:
    print(f"❌ FAILED with openai_api_key: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
