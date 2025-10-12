import os
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("AZURE_OPENAI_ENDPOINT"))
print(os.getenv("AZURE_OPENAI_API_KEY"))