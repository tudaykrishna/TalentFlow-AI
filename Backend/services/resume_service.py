"""Resume Screening Service"""
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from openai import AzureOpenAI  # Azure Embeddings client (see hi4.py)
import chromadb  # Vector DB
from chromadb.config import Settings
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Literal
import logging
import PyPDF2
import io
import json
try:
    import pypdf as pypdf_lib  # optional fallback for PDF text extraction
except Exception:  # pragma: no cover
    pypdf_lib = None

# Load .env from project root
project_root = Path(__file__).resolve().parent.parent.parent
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)

logger = logging.getLogger(__name__)

# Pydantic Models for Structured Data
class JobDescription(BaseModel):
    """Structured data extracted from a job description"""
    required_skills: List[str] = Field(description="A list of essential skills required for the job")
    preferred_skills: List[str] = Field(description="A list of preferred but not mandatory skills")
    years_of_experience: int = Field(description="The minimum number of years of experience required")

class CandidateResume(BaseModel):
    """Structured data extracted from a candidate's resume"""
    name: str = Field(description="The full name of the candidate")
    skills: List[str] = Field(description="A list of skills possessed by the candidate")
    work_experience: List[Dict] = Field(description="A list of previous work experiences, including job title, company, and duration in years")
    total_experience_years: int = Field(description="The total number of years of professional experience")

class ScreeningResult(BaseModel):
    """The final output of the screening process"""
    match_score: int = Field(description="A score from 0 to 100 representing the candidate's suitability", ge=0, le=100)
    summary: str = Field(description="A concise summary explaining the reasoning behind the score, highlighting strengths and weaknesses")
    status: Literal["Strong Match", "Potential Fit", "Not a Fit"] = Field(description="The final recommendation status")


class ResumeScreenerService:
    """AI-powered Resume Screening Service"""
    
    def __init__(self):
        """Initialize the Resume Screener with Azure OpenAI model"""
        try:
            # Get environment variables
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
            embedding_model = os.getenv("AZURE_EMBEDDING_MODEL", "text-embedding-3-large")
            
            # Debug logging
            logger.info(f"Initializing Resume Screener with:")
            logger.info(f"  Endpoint: {azure_endpoint}")
            logger.info(f"  Deployment: {deployment_name}")
            logger.info(f"  API Version: {api_version}")
            
            # Validate required configs
            if not all([api_key, api_version, azure_endpoint, deployment_name]):
                missing = []
                if not api_key: missing.append("AZURE_OPENAI_API_KEY")
                if not api_version: missing.append("AZURE_OPENAI_API_VERSION")
                if not azure_endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
                if not deployment_name: missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
                raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
            self.llm = AzureChatOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                deployment_name=deployment_name,
                temperature=0.0,
                model_kwargs={
                    "response_format": {"type": "json_object"},
                }
            )
            logger.info("✅ Resume Screener chat model initialized successfully with Azure OpenAI")

            # --- Chroma + Embeddings initialization (inspired by hi4.py) ---
            # Keep env usage consistent; do not change .env keys.
            # Create Azure embeddings client
            self.embedding_client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=api_key,
                api_version=api_version or "2024-02-01",  # fallback to hi4.py default if unset
            )
            self.embedding_model = embedding_model

            # Initialize (and persist) Chroma collection for resumes
            persist_dir = str((project_root / "resume_db").resolve())
            try:
                os.makedirs(persist_dir, exist_ok=True)
            except Exception as e:
                logger.warning("⚠ Could not create Chroma persist directory %s: %s", persist_dir, e)

            # Prefer PersistentClient if available (newer chromadb versions)
            persistent_client_cls = getattr(chromadb, "PersistentClient", None)
            if persistent_client_cls is not None:
                self.chroma_client = persistent_client_cls(path=persist_dir)
                logger.info("ℹ Using chromadb.PersistentClient with path=%s", persist_dir)
            else:
                self.chroma_client = chromadb.Client(Settings(persist_directory=persist_dir))
                logger.info("ℹ Using chromadb.Client with persist_directory=%s", persist_dir)

            self.resume_collection = self.chroma_client.get_or_create_collection(name="resumes")

            logger.info("✅ Chroma DB initialized with collection 'resumes'")
            logger.info("✅ Embeddings model: %s", self.embedding_model)
        except Exception as e:
            logger.error(f"❌ Error initializing Azure OpenAI model: {e}")
            raise

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            if isinstance(pdf_file, bytes):
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
            else:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            text = (text or "").strip()
            # Fallback to pypdf if text is empty and pypdf is available
            if not text and pypdf_lib is not None:
                try:
                    if isinstance(pdf_file, bytes):
                        reader = pypdf_lib.PdfReader(io.BytesIO(pdf_file))
                    else:
                        reader = pypdf_lib.PdfReader(pdf_file)
                    alt_text = ""
                    for page in reader.pages:
                        alt_text += page.extract_text() or ""
                    text = alt_text.strip()
                    if text:
                        logger.info("ℹ Extracted text via pypdf fallback")
                except Exception as fallback_err:
                    logger.warning("⚠ pypdf fallback failed: %s", fallback_err)
            return text
        except Exception as e:
            logger.error(f"❌ Error extracting text from PDF: {e}")
            raise

    def _extract_structured_data(self, text: str, pydantic_model):
        """Generic function to extract structured data from text using a Pydantic model"""
        parser = PydanticOutputParser(pydantic_object=pydantic_model)
        
        prompt = PromptTemplate(
            template="You are an expert HR data analyst. Extract the relevant information from the document below and format it according to the provided JSON schema.\n{format_instructions}\nDocument:\n{document_text}",
            input_variables=["document_text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        chain = prompt | self.llm
        
        try:
            output = chain.invoke({"document_text": text})
            # Parse the JSON response from Azure OpenAI
            parsed_output = parser.parse(output.content)
            return parsed_output
        except Exception as e:
            logger.error(f"❌ Error during data extraction: {e}")
            logger.error(f"Response content: {output.content if 'output' in locals() else 'N/A'}")
            return None

    # --- Embeddings helpers (Chroma integration) ---
    def _get_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text using Azure embeddings (see hi4.py)."""
        if not text:
            return []
        try:
            response = self.embedding_client.embeddings.create(
                input=text,
                model=self.embedding_model,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("❌ Error generating embedding: %s", e)
            raise

    def _chroma_upsert_resume(self, resume_id: str, resume_text: str, embedding: List[float]):
        """Store or update the resume vector into Chroma (mirrors add flow in hi4.py)."""
        try:
            if not embedding:
                logger.warning("⚠ Skipping Chroma upsert for %s due to empty embedding", resume_id)
                return
            self.resume_collection.add(
                ids=[resume_id],
                embeddings=[embedding],
                documents=[resume_text],
                metadatas=[{"filename": resume_id}],
            )
            logger.info("✅ Stored resume vector in Chroma: %s", resume_id)
        except Exception as e:
            logger.error("❌ Error upserting resume into Chroma: %s", e)
            raise

    def _chroma_query(self, query_embedding: List[float], top_k: int = 1):
        """Query Chroma for nearest resumes given a query embedding (see search_resumes in hi4.py)."""
        try:
            if not query_embedding:
                return None
            results = self.resume_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["distances", "metadatas", "documents", "embeddings"],
            )
            return results
        except Exception as e:
            logger.error("❌ Error querying Chroma: %s", e)
            raise

    async def screen_resume(self, jd_text: str, resume_text: str) -> ScreeningResult:
        """
        Perform the two-step screening process: extraction and comparison
        
        Args:
            jd_text: Job description text
            resume_text: Resume text
            
        Returns:
            ScreeningResult: Screening result with match score and status
        """
        try:
            logger.info("Step 1: Extracting structured data from documents")

            # Extract data from Job Description via LLM (kept for backward compatibility of shapes)
            jd_data = self._extract_structured_data(jd_text or "", JobDescription)
            if not jd_data:
                # Graceful fallback to defaults to avoid dropping candidates
                jd_data = JobDescription(required_skills=[], preferred_skills=[], years_of_experience=0)
                logger.warning("⚠ Falling back to default JD data due to extraction failure")
            logger.info("✅ Job Description data extracted")

            # Extract data from Resume via LLM (kept for downstream compatibility)
            resume_data = self._extract_structured_data(resume_text or "", CandidateResume)
            if not resume_data:
                # Graceful fallback with minimal candidate info
                resume_data = CandidateResume(name="Unknown", skills=[], work_experience=[], total_experience_years=0)
                logger.warning("⚠ Falling back to default Resume data due to extraction failure")
            logger.info("✅ Resume data extracted")

            # --- Step 2 (Refactored): Chroma-based semantic comparison (replaces heavy LLM comparison) ---
            # Inspired by hi4.py: compute embeddings, store resume vector, query with JD vector
            logger.info("Step 2: Semantic comparison via Chroma (embedding similarity)")

            jd_embedding = self._get_embedding(jd_text or "")
            resume_embedding = self._get_embedding(resume_text or "")

            # Upsert resume vector into Chroma using a deterministic ID (name + short hash fallback)
            try:
                base_id = resume_data.name if getattr(resume_data, "name", None) else "resume"
            except Exception:
                base_id = "resume"
            import hashlib
            content_hash = hashlib.sha1(resume_text.encode("utf-8", errors="ignore")).hexdigest()[:8]
            resume_id = f"{base_id}_{content_hash}"
            self._chroma_upsert_resume(resume_id=resume_id, resume_text=resume_text, embedding=resume_embedding)

            # Query the most similar resume for the given JD
            results = self._chroma_query(query_embedding=jd_embedding, top_k=1)

            # Derive a match score from distance (Chroma returns smaller distance => more similar)
            match_score = 0
            if results and results.get("distances") and results["distances"] and results["distances"][0]:
                distance = results["distances"][0][0]
                # Convert cosine distance to similarity percentage
                try:
                    similarity = max(0.0, min(1.0, 1.0 - float(distance)))
                    match_score = int(round(similarity * 100))
                except Exception:
                    match_score = 0

            # Simple status bucketing based on match score
            if match_score >= 80:
                status: Literal["Strong Match", "Potential Fit", "Not a Fit"] = "Strong Match"
            elif match_score >= 60:
                status = "Potential Fit"
            else:
                status = "Not a Fit"

            # Build a concise summary noting the Chroma-based evaluation
            summary = (
                "Semantic similarity between job description and resume computed via embeddings. "
                f"Top match distance converted to score: {match_score}. "
                "This replaces the previous LLM comparison step (see hi4.py)."
            )

            final_result = ScreeningResult(
                match_score=match_score,
                summary=summary,
                status=status,
            )

            logger.info("✅ Screening completed successfully (Chroma-based)")
            return final_result, resume_data
            
        except Exception as e:
            logger.error(f"❌ Error during resume screening: {e}")
            raise

# Global service instance
resume_screener_service = ResumeScreenerService()

