import os
import chromadb
from chromadb.config import Settings
from openai import AzureOpenAI
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
# ===============================
# 🔹 Azure OpenAI Setup
# ===============================
client = AzureOpenAI(
   azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
   api_key=os.getenv("AZURE_OPENAI_API_KEY"),
   api_version="2024-02-01"
)
EMBED_MODEL = os.getenv("AZURE_EMBEDDING_MODEL", "text-embedding-3-large")

# ===============================
# 🔹 Chroma DB Setup
# ===============================
chroma_client = chromadb.Client(Settings(
   persist_directory="./resume_db"  # local persistent folder
))
collection = chroma_client.get_or_create_collection(name="resumes")

# ===============================
# 🧩 Helper: Extract text from PDF
# ===============================
def extract_text_from_pdf(pdf_path: str) -> str:
   reader = PdfReader(pdf_path)
   text = ""
   for page in reader.pages:
       text += page.extract_text() or ""
   return text.strip()

# ===============================
# 🧩 Helper: Generate Embedding
# ===============================
def get_embedding(text: str):
   response = client.embeddings.create(
       input=text,
       model=EMBED_MODEL
   )
   return response.data[0].embedding

# ===============================
# 🧩 Step 1: Upload & Store Resume
# ===============================
def add_resume_to_db(resume_path: str):
   text = extract_text_from_pdf(resume_path)
   if not text:
       print(f"⚠ No text found in {resume_path}")
       return

   embedding = get_embedding(text)
   resume_id = os.path.basename(resume_path)

   collection.add(
       ids=[resume_id],
       embeddings=[embedding],
       documents=[text],
       metadatas=[{"filename": resume_id}]
   )
   print(f"✅ Stored: {resume_id}")

# ===============================
# 🧩 Step 2: Search for Matching Resumes
# ===============================
def search_resumes(jd_text: str, top_k: int = 5):
   jd_embedding = get_embedding(jd_text)
   results = collection.query(
       query_embeddings=[jd_embedding],
       n_results=top_k
   )
   matches = []
   for i, doc in enumerate(results['documents'][0]):
       matches.append({
           "rank": i + 1,
           "filename": results["metadatas"][0][i]["filename"],
           "score": results["distances"][0][i],
       })
   return matches

# ===============================
# 🚀 Example Usage
# ===============================
if __name__ == "__main__":
   # ---- Step 1: Add all resumes in a folder ----
   resume_folder = "./resumes"
   for file in os.listdir(resume_folder):
       if file.lower().endswith(".pdf"):
           add_resume_to_db(os.path.join(resume_folder, file))

   # ---- Step 2: Search resumes for a given JD ----
   jd_text = """
   We are looking for a Data Scientist with experience in Python, SQL, 
   and Machine Learning. Experience in Azure and NLP is a plus.
   """
   print("\n🔍 Matching Resumes:")
   matches = search_resumes(jd_text, top_k=5)
   for m in matches:
       print(f"{m['rank']}. {m['filename']}  (Score: {m['score']:.4f})")