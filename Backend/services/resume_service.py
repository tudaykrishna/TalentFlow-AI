"""Resume Screening Service (Chroma + Azure embeddings)
This version follows hi4.py's Chroma + AzureOpenAI embedding setup but keeps
the higher-level screening flow (extract -> embed -> upsert/query).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import io
import hashlib
from typing import List, Dict, Tuple

# Try to prefer pypdf PdfReader (more modern); fallback to PyPDF2
try:
    from pypdf import PdfReader as PypdfReader
except Exception:
    PypdfReader = None

try:
    import PyPDF2
    PyPDF2_available = True
except Exception:
    PyPDF2_available = False

# Azure OpenAI embeddings client (same as hi4.py)
from openai import AzureOpenAI
import chromadb
from chromadb.config import Settings

# Lightweight LLM extraction is kept but optional; if not available, extraction falls back to heuristics.
# To avoid a hard dependency we wrap usage and provide fallbacks.
try:
    from langchain_openai import AzureChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field
    from typing import Literal
    LLM_AVAILABLE = True
except Exception:
    AzureChatOpenAI = None
    PromptTemplate = None
    PydanticOutputParser = None
    BaseModel = object
    Field = lambda *a, **k: None
    Literal = None
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOGLEVEL", "INFO"))

# --- load .env from sensible defaults: current working dir or package root ---
# This is robust whether you run uvicorn from project root or as a module
load_dotenv()

# Determine project root (if running as installed module it may be different)
_project_root = Path.cwd()

# Embedding model default (matches hi4.py)
EMBED_MODEL = os.getenv("AZURE_EMBEDDING_MODEL", "text-embedding-3-large")

class ResumeScreenerService:
    def __init__(self):
        """Initialize clients (Azure OpenAI embeddings + Chroma)"""
        try:
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
            # chat/deployment name (optional if not doing complex LLM extraction)
            chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")

            if not all([azure_endpoint, api_key]):
                missing = []
                if not azure_endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
                if not api_key: missing.append("AZURE_OPENAI_API_KEY")
                raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

            # Azure embeddings client (same usage as hi4.py)
            self.embedding_client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version
            )
            self.embedding_model = EMBED_MODEL
            logger.info("✅ AzureOpenAI embedding client initialized")

            # Initialize Chroma client (persist directory similar to hi4.py)
            persist_dir = str((_project_root / "resume_db").resolve())
            os.makedirs(persist_dir, exist_ok=True)

            persistent_client_cls = getattr(chromadb, "PersistentClient", None)
            if persistent_client_cls is not None:
                # Newer chromadb API
                try:
                    self.chroma_client = persistent_client_cls(path=persist_dir)
                    logger.info("ℹ Using chromadb.PersistentClient with path=%s", persist_dir)
                except Exception as e:
                    # fallback to older Client API
                    self.chroma_client = chromadb.Client(Settings(persist_directory=persist_dir))
                    logger.warning("⚠ PersistentClient init failed, falling back to chromadb.Client: %s", e)
            else:
                self.chroma_client = chromadb.Client(Settings(persist_directory=persist_dir))
                logger.info("ℹ Using chromadb.Client with persist_directory=%s", persist_dir)

            self.resume_collection = self.chroma_client.get_or_create_collection(name="resumes")
            logger.info("✅ Chroma DB initialized with collection 'resumes'")

            # Optional LLM (if available). Keep it read-only: used for structured extraction when present.
            if LLM_AVAILABLE and chat_deployment:
                try:
                    self.llm = AzureChatOpenAI(
                        api_key=api_key,
                        api_version=api_version,
                        azure_endpoint=azure_endpoint,
                        deployment_name=chat_deployment,
                        temperature=0.0,
                        model_kwargs={"response_format": {"type": "json_object"}}
                    )
                    logger.info("✅ AzureChatOpenAI (langchain) initialized for optional extraction")
                except Exception as e:
                    self.llm = None
                    logger.warning("⚠ Failed to initialize AzureChatOpenAI: %s", e)
            else:
                self.llm = None
                logger.info("ℹ LLM extraction disabled (langchain not available or deployment not set)")
        except Exception as e:
            logger.error("❌ Error initializing ResumeScreenerService: %s", e)
            raise

    def extract_text_from_pdf(self, pdf_bytes_or_file) -> str:
        """Extract text from PDF bytes or file-like. Prefer pypdf, fallback to PyPDF2."""
        try:
            # If given bytes convert to BytesIO
            if isinstance(pdf_bytes_or_file, (bytes, bytearray)):
                stream = io.BytesIO(pdf_bytes_or_file)
            else:
                stream = pdf_bytes_or_file  # assume file-like / path-like

            text = ""
            # Try pypdf first
            if PypdfReader is not None:
                try:
                    reader = PypdfReader(stream)
                    for page in reader.pages:
                        page_text = page.extract_text() or ""
                        text += page_text
                    text = text.strip()
                    if text:
                        return text
                except Exception as e:
                    logger.debug("pypdf extraction failed: %s", e)
                    # reset stream if possible
                    try:
                        stream.seek(0)
                    except Exception:
                        pass

            # Fallback to PyPDF2 if available
            if PyPDF2_available:
                try:
                    if isinstance(stream, io.BytesIO):
                        reader = PyPDF2.PdfReader(stream)
                    else:
                        # if a file path (str/Path) was passed
                        reader = PyPDF2.PdfReader(stream)
                    for page in reader.pages:
                        page_text = page.extract_text() or ""
                        text += page_text
                    return (text or "").strip()
                except Exception as e:
                    logger.warning("PyPDF2 extraction failed: %s", e)
                    return ""
            else:
                logger.warning("No PDF extraction library available (pypdf or PyPDF2)")
                return ""
        except Exception as e:
            logger.error("Error extracting text from PDF: %s", e)
            return ""

    def _get_embedding(self, text: str) -> List[float]:
        """Return embedding using AzureOpenAI client (consistent with hi4.py)."""
        if not text:
            return []
        try:
            resp = self.embedding_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return resp.data[0].embedding
        except Exception as e:
            logger.error("❌ Error generating embedding: %s", e)
            raise

    def _chroma_upsert_resume(self, resume_id: str, resume_text: str, embedding: List[float]):
        if not embedding:
            logger.warning("⚠ Empty embedding for %s; skipping upsert", resume_id)
            return
        try:
            # Chroma's collection.add semantics differ across versions; this matches hi4.py usage
            self.resume_collection.add(
                ids=[resume_id],
                embeddings=[embedding],
                documents=[resume_text],
                metadatas=[{"filename": resume_id}],
            )
            logger.info("✅ Stored resume vector in Chroma: %s", resume_id)
        except Exception as e:
            logger.error("❌ Error upserting to Chroma: %s", e)
            raise

    def _chroma_query(self, query_embedding: List[float], top_k: int = 1):
        if not query_embedding:
            return None
        try:
            results = self.resume_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["distances", "metadatas", "documents", "embeddings"],
            )
            return results
        except Exception as e:
            logger.error("❌ Error querying Chroma: %s", e)
            raise

    async def screen_resume(self, jd_text: str, resume_text: str) -> Tuple[Dict, Dict]:
        """
        Main screening: compute embeddings for resume & JD, upsert resume, query with JD to derive match score.
        Returns: (screening_result_dict, candidate_data_like_dict)
        """
        try:
            # Simple heuristic extraction for candidate name if no LLM available
            candidate_name = "Unknown"
            # Quick attempt: look for lines with capitalized words (very naive)
            sometimes_name = None
            try:
                first_lines = [l.strip() for l in (resume_text or "").splitlines() if l.strip()]
                if first_lines:
                    sometimes_name = first_lines[0]
                    # if first line is short and likely a name, use it
                    if 1 <= len(sometimes_name.split()) <= 5 and len(sometimes_name) < 60:
                        candidate_name = sometimes_name
            except Exception:
                pass

            # Embeddings
            jd_embedding = self._get_embedding(jd_text or "")
            resume_embedding = self._get_embedding(resume_text or "")

            # Build deterministic resume id (name + short hash)
            content_hash = hashlib.sha1((resume_text or "").encode("utf-8", errors="ignore")).hexdigest()[:8]
            resume_id = f"{(candidate_name or 'resume')}_{content_hash}"

            # Upsert into chroma
            self._chroma_upsert_resume(resume_id=resume_id, resume_text=resume_text or "", embedding=resume_embedding)

            # Query chroma with JD embedding
            results = self._chroma_query(query_embedding=jd_embedding, top_k=1)

            match_score = 0
            if results and results.get("distances"):
                try:
                    distances = results["distances"][0]
                    if distances:
                        distance = float(distances[0])
                        similarity = max(0.0, min(1.0, 1.0 - distance))
                        match_score = int(round(similarity * 100))
                except Exception:
                    match_score = 0

            # Status buckets
            if match_score >= 80:
                status = "Strong Match"
            elif match_score >= 60:
                status = "Potential Fit"
            else:
                status = "Not a Fit"

            # Build summary
            summary = (
                "Semantic similarity between job description and resume computed via embeddings. "
                f"Top match distance converted to score: {match_score}. "
            )

            screening_result = {
                "match_score": match_score,
                "summary": summary,
                "status": status,
            }

            candidate_data = {
                "name": candidate_name,
                "extracted_lines_sample": (first_lines[:5] if 'first_lines' in locals() else [])
            }

            return screening_result, candidate_data

        except Exception as e:
            logger.error("❌ Error in screen_resume: %s", e)
            raise

# Export a global instance (routes import this)
resume_screener_service = ResumeScreenerService()
