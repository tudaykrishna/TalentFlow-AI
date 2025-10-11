"""Resume Screening Service"""
import os
from dotenv import load_dotenv
try:
    from langchain_ollama import OllamaLLM
except ImportError:
    # Fallback to old import for compatibility
    from langchain_community.llms import Ollama as OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Literal
import logging
import PyPDF2
import io

# Force reload environment variables (override=True ensures we get latest .env)
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
    
    def __init__(self, model_name: str = None):
        """Initialize the Resume Screener with Ollama model"""
        try:
            # Use environment variable or default model
            model_name = model_name or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            self.llm = OllamaLLM(model=model_name, temperature=0.0, format="json")
            logger.info(f"✅ Resume Screener initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"❌ Error initializing Ollama model: {e}")
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
            
            return text.strip()
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
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            output = chain.invoke({"document_text": text})
            parsed_output = parser.parse(output['text'])
            return parsed_output
        except Exception as e:
            logger.error(f"❌ Error during data extraction: {e}")
            return None

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
            
            # Extract data from Job Description
            jd_data = self._extract_structured_data(jd_text, JobDescription)
            if not jd_data:
                raise ValueError("Failed to process Job Description")
            
            logger.info("✅ Job Description data extracted")

            # Extract data from Resume
            resume_data = self._extract_structured_data(resume_text, CandidateResume)
            if not resume_data:
                raise ValueError("Failed to process Resume")
            
            logger.info("✅ Resume data extracted")

            logger.info("Step 2: Comparing data and generating screening result")
            
            comparison_parser = PydanticOutputParser(pydantic_object=ScreeningResult)

            comparison_prompt = PromptTemplate(
                template="""
                You are an expert Senior Technical Recruiter with 15 years of experience.
                Analyze the candidate's resume against the job description based on the structured data provided.
                Provide a match score, a concise summary of your analysis, and a final status.
                
                Job Requirements:
                {jd_json}
                
                Candidate's Resume:
                {resume_json}
                
                {format_instructions}
                """,
                input_variables=["jd_json", "resume_json"],
                partial_variables={"format_instructions": comparison_parser.get_format_instructions()},
            )
            
            comparison_chain = LLMChain(llm=self.llm, prompt=comparison_prompt)
            
            result_output = comparison_chain.invoke({
                "jd_json": jd_data.model_dump_json(),
                "resume_json": resume_data.model_dump_json()
            })
            
            final_result = comparison_parser.parse(result_output['text'])
            
            logger.info("✅ Screening completed successfully")
            return final_result, resume_data
            
        except Exception as e:
            logger.error(f"❌ Error during resume screening: {e}")
            raise

# Global service instance
resume_screener_service = ResumeScreenerService()

