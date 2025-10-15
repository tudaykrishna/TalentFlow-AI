"""Resume Screening Service (Chroma + Azure embeddings)

This service implements a top-K ranking system for resume screening:
1. Extracts text from PDF resumes
2. Generates embeddings using Azure OpenAI
3. Stores resume embeddings in ChromaDB vector store
4. Ranks all resumes by semantic similarity to job description
5. Returns top K most similar candidates

Uses Azure OpenAI for embeddings and ChromaDB for vector storage.
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

    def _extract_candidate_name(self, resume_text: str) -> str:
        """Extract candidate name from resume text using improved heuristics."""
        candidate_name = "Unknown"
        try:
            if not resume_text:
                return candidate_name
            
            # Get non-empty lines
            lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
            if not lines:
                return candidate_name
            
            # Try first few lines to find name
            for i, line in enumerate(lines[:5]):  # Check first 5 lines
                # Skip common header words
                skip_words = ['resume', 'curriculum', 'vitae', 'cv', 'profile', 'professional', 'summary']
                if any(word in line.lower() for word in skip_words):
                    continue
                
                # Check if line looks like a name
                words = line.split()
                # Name should be 1-4 words, less than 60 chars, and contain mostly alphabetic characters
                if 1 <= len(words) <= 4 and len(line) < 60:
                    # Check if mostly alphabetic (allows for middle initials, Jr., etc.)
                    alpha_ratio = sum(c.isalpha() or c.isspace() or c in '.-,' for c in line) / len(line)
                    if alpha_ratio > 0.7:
                        candidate_name = line
                        break
            
            # If still Unknown, just use first non-empty line as fallback
            if candidate_name == "Unknown" and lines:
                candidate_name = lines[0][:60]  # Limit length
                
        except Exception as e:
            logger.debug("Error extracting candidate name: %s", e)
        
        return candidate_name

    def _calculate_similarity_score(self, distance: float) -> float:
        """
        Convert distance to similarity score (0-100).
        
        ChromaDB uses L2 (Euclidean) distance by default for embeddings.
        For normalized embeddings, this is equivalent to cosine distance.
        Distance of 0 = identical vectors, higher values = more different.
        """
        # Convert distance to similarity percentage
        # Using exponential decay for better score distribution
        similarity = max(0.0, min(100.0, 100.0 * (1.0 - min(distance, 2.0) / 2.0)))
        return round(similarity, 2)

    async def process_resume(self, resume_text: str, resume_filename: str) -> Tuple[str, List[float], str, str]:
        """
        Process a single resume: extract name, generate embedding, create ID.
        Returns: (resume_id, embedding, candidate_name, resume_text)
        """
        try:
            # Extract candidate name
            candidate_name = self._extract_candidate_name(resume_text)
            
            # Generate embedding
            resume_embedding = self._get_embedding(resume_text or "")
            
            # Build deterministic resume id
            content_hash = hashlib.sha1((resume_text or "").encode("utf-8", errors="ignore")).hexdigest()[:8]
            resume_id = f"{candidate_name.replace(' ', '_')}_{content_hash}"
            
            logger.info(f"✅ Processed resume: {resume_filename} -> {candidate_name}")
            
            return resume_id, resume_embedding, candidate_name, resume_text
            
        except Exception as e:
            logger.error(f"❌ Error processing resume {resume_filename}: %s", e)
            raise

    async def rank_resumes(
        self, 
        jd_text: str, 
        resumes_data: List[Tuple[str, str, str]],  # List of (filename, content_bytes, resume_text)
        top_k: int = 5
    ) -> List[Dict]:
        """
        Rank all resumes against JD and return top K most similar ones.
        
        Args:
            jd_text: Job description text
            resumes_data: List of tuples (filename, content_bytes, resume_text)
            top_k: Number of top candidates to return (default: 5)
            
        Returns:
            List of dicts with resume info and similarity scores, sorted by similarity (highest first)
        
        Raises:
            ValueError: If inputs are invalid
            Exception: If ranking process fails
        """
        try:
            # Input validation
            if not jd_text or len(jd_text.strip()) < 20:
                raise ValueError("Job description must contain at least 20 characters")
            
            if not resumes_data:
                logger.warning("No resumes provided for ranking")
                return []
            
            if top_k < 1:
                raise ValueError("top_k must be at least 1")
            
            logger.info(f"🔍 Ranking {len(resumes_data)} resumes against JD (returning top {top_k})")
            
            # Generate JD embedding once
            jd_embedding = self._get_embedding(jd_text or "")
            
            # Process all resumes and collect data
            processed_resumes = []
            for filename, content_bytes, resume_text in resumes_data:
                try:
                    resume_id, resume_embedding, candidate_name, resume_text_clean = await self.process_resume(
                        resume_text, filename
                    )
                    
                    # Store in ChromaDB
                    self._chroma_upsert_resume(
                        resume_id=resume_id,
                        resume_text=resume_text_clean,
                        embedding=resume_embedding
                    )
                    
                    processed_resumes.append({
                        "filename": filename,
                        "content_bytes": content_bytes,
                        "resume_id": resume_id,
                        "resume_text": resume_text_clean,
                        "embedding": resume_embedding,
                        "candidate_name": candidate_name
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process resume {filename}: %s", e)
                    # Continue with other resumes
                    continue
            
            if not processed_resumes:
                logger.warning("No resumes were successfully processed")
                return []
            
            # Calculate similarity for all resumes
            similarities = []
            for resume_data in processed_resumes:
                try:
                    # Calculate cosine similarity using ChromaDB query
                    results = self._chroma_query(query_embedding=jd_embedding, top_k=len(processed_resumes))
                    
                    # Find this resume's distance in the results
                    distance = None
                    if results and results.get("ids") and results.get("distances"):
                        for i, result_id in enumerate(results["ids"][0]):
                            if result_id == resume_data["resume_id"]:
                                distance = results["distances"][0][i]
                                break
                    
                    if distance is not None:
                        similarity_score = self._calculate_similarity_score(distance)
                    else:
                        # Fallback: calculate similarity manually if not in results
                        similarity_score = 50.0  # Default middle score
                        logger.warning(f"Could not find distance for {resume_data['resume_id']}, using default")
                    
                    similarities.append({
                        "filename": resume_data["filename"],
                        "content_bytes": resume_data["content_bytes"],
                        "resume_id": resume_data["resume_id"],
                        "resume_text": resume_data["resume_text"],
                        "candidate_name": resume_data["candidate_name"],
                        "similarity_score": similarity_score,
                        "distance": distance if distance is not None else 1.0
                    })
                    
                except Exception as e:
                    logger.error(f"❌ Error calculating similarity for {resume_data['candidate_name']}: %s", e)
                    continue
            
            # Sort by similarity score (highest first)
            similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Return top K
            top_candidates = similarities[:top_k]
            
            logger.info(f"✅ Top {len(top_candidates)} candidates selected from {len(similarities)} total")
            
            # Add ranking
            for rank, candidate in enumerate(top_candidates, 1):
                candidate["rank"] = rank
                # Determine status based on similarity
                if candidate["similarity_score"] >= 80:
                    candidate["status"] = "Strong Match"
                elif candidate["similarity_score"] >= 60:
                    candidate["status"] = "Potential Fit"
                else:
                    candidate["status"] = "Possible Match"
                
                # Generate summary
                candidate["summary"] = (
                    f"Ranked #{rank} out of {len(similarities)} candidates. "
                    f"Semantic similarity score: {candidate['similarity_score']:.1f}%. "
                    f"This candidate shows {candidate['status'].lower()} with the job requirements."
                )
            
            return top_candidates

        except Exception as e:
            logger.error("❌ Error in rank_resumes: %s", e)
            raise

# Export a global instance (routes import this)
resume_screener_service = ResumeScreenerService()
