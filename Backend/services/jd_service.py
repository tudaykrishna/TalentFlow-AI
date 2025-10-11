"""Job Description Generator Service"""
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from fpdf import FPDF
import logging
from datetime import datetime

# Force reload environment variables (override=True ensures we get latest .env)
load_dotenv(override=True)
logger = logging.getLogger(__name__)

class JDGeneratorService:
    """Service for generating Job Descriptions using Azure OpenAI"""
    
    def __init__(self):
        """Initialize Azure OpenAI GPT-4"""
        try:
            # Get environment variables
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
            
            # Debug logging
            logger.info(f"Initializing JD Generator with:")
            logger.info(f"  Endpoint: {azure_endpoint}")
            logger.info(f"  Deployment: {deployment_name}")
            logger.info(f"  API Version: {api_version}")
            logger.info(f"  API Key: {'*' * 8}...{api_key[-4:] if api_key else 'NOT SET'}")
            
            # Validate required configs
            if not all([api_key, api_version, azure_endpoint, deployment_name]):
                missing = []
                if not api_key: missing.append("AZURE_OPENAI_API_KEY")
                if not api_version: missing.append("AZURE_OPENAI_API_VERSION")
                if not azure_endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
                if not deployment_name: missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
                raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
            self.model = AzureChatOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=azure_endpoint,
                deployment_name=deployment_name,
                temperature=0.3
            )
            
            self.template = """
You are an expert HR copywriter with experience in the tech industry. Your task is to write a clear, engaging, and comprehensive job description based on the provided keywords.

**Job Title:** {job_title}

**Company Tone:** {company_tone}

**Key Responsibilities:**
{responsibilities}

**Core Skills Required:**
{skills}

**Years of Experience:** {experience} years

Based on the information above, please generate a full job description. The description must include the following sections in Markdown format:
- ## About the Role
- ## Key Responsibilities
- ## Required Qualifications
- ## Preferred Qualifications (You can infer these based on the role)
- ## Why You'll Love Working With Us

Ensure the language and tone match the specified company tone. Do not invent benefits or company details unless they are general and positive (e.g., "collaborative environment").
"""
            self.prompt = PromptTemplate(
                input_variables=["job_title", "company_tone", "responsibilities", "skills", "experience"],
                template=self.template
            )
            
            self.chain = self.prompt | self.model
            
            logger.info("✅ JD Generator Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize JD Generator: {e}")
            raise
    
    async def generate_jd(self, job_title: str, company_tone: str, 
                         responsibilities: str, skills: str, experience: str) -> str:
        """
        Generate a job description based on provided parameters
        
        Returns:
            str: Generated job description in markdown format
        """
        try:
            logger.info(f"Generating JD for: {job_title}")
            
            user_input = {
                "job_title": job_title,
                "company_tone": company_tone,
                "responsibilities": responsibilities,
                "skills": skills,
                "experience": experience
            }
            
            response = self.chain.invoke(user_input)
            jd_content = response.content
            
            logger.info("✅ JD generated successfully")
            return jd_content
            
        except Exception as e:
            logger.error(f"❌ Error generating JD: {e}")
            raise
    
    def save_jd_to_pdf(self, markdown_text: str, filename: str = None) -> str:
        """
        Save generated JD to PDF file
        
        Args:
            markdown_text: JD content in markdown format
            filename: Optional custom filename
            
        Returns:
            str: Path to saved PDF file
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"jd_{timestamp}.pdf"
            
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads/jds", exist_ok=True)
            filepath = os.path.join("uploads/jds", filename)
            
            # Clean text to remove Unicode characters that can't be encoded
            def clean_text(text):
                """Replace common Unicode characters with ASCII equivalents"""
                replacements = {
                    '\u2019': "'",  # Right single quotation mark
                    '\u2018': "'",  # Left single quotation mark
                    '\u201c': '"',  # Left double quotation mark
                    '\u201d': '"',  # Right double quotation mark
                    '\u2013': '-',  # En dash
                    '\u2014': '-',  # Em dash
                    '\u2026': '...',  # Horizontal ellipsis
                    '\u00a0': ' ',  # Non-breaking space
                }
                for old, new in replacements.items():
                    text = text.replace(old, new)
                # Remove any remaining non-ASCII characters
                return text.encode('ascii', 'ignore').decode('ascii')
            
            markdown_text = clean_text(markdown_text)
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)

            lines = markdown_text.split('\n')

            for line in lines:
                line = line.strip()
                if line.startswith('## '):
                    # H2 Main Title
                    pdf.set_font("Arial", 'B', 20)
                    pdf.multi_cell(0, 12, line[3:], align='C')
                    pdf.ln(10)
                elif line.startswith('### '):
                    # H3 Subtitle
                    pdf.set_font("Arial", 'B', 16)
                    pdf.multi_cell(0, 10, line[4:])
                    pdf.ln(4)
                elif line.startswith('* ') or line.startswith('- '):
                    # Bullet point
                    pdf.set_font("Arial", '', 12)
                    pdf.multi_cell(0, 6, f"  - {line[2:]}")
                    pdf.ln(1)
                elif line:
                    # Regular paragraph
                    pdf.set_font("Arial", '', 12)
                    pdf.multi_cell(0, 6, line)
                    pdf.ln(3)

            pdf.output(filepath)
            logger.info(f"✅ PDF saved successfully: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Error saving PDF: {e}")
            raise

# Global service instance
jd_service = JDGeneratorService()

