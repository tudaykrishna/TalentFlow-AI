"""AI Interview Service"""
import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, TypedDict, Optional, Literal
import logging

# Force reload environment variables (override=True ensures we get latest .env)
load_dotenv(override=True)
logger = logging.getLogger(__name__)

# Pydantic Models for Structured Output
class InterviewPlan(BaseModel):
    topics: List[str] = Field(description="A list of 3-5 key technical and behavioral topics to cover in an interview")

class Question(BaseModel):
    question: str = Field(description="The next question to ask the candidate")

class Evaluation(BaseModel):
    rating: int = Field(description="A rating of the candidate's answer from 1 (poor) to 5 (excellent)", ge=1, le=5)
    feedback: str = Field(description="A brief justification for the rating, explaining what was good or could be improved")

class Summary(BaseModel):
    recommendation: Literal["Proceed", "Hold", "Reject"] = Field(description="The final hiring recommendation")
    summary_text: str = Field(description="A comprehensive summary of the candidate's performance during the interview")


class InterviewerService:
    """AI-Powered Interview Service"""
    
    def __init__(self):
        """Initialize the Azure Chat OpenAI model"""
        try:
            # Get environment variables
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
            
            # Debug logging
            logger.info(f"Initializing Interview Service with:")
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
                temperature=0.1,
                model_kwargs={
                    "response_format": {"type": "json_object"},
                }
            )
            logger.info("✅ Interview Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Interview Service: {e}")
            raise

    async def generate_interview_plan(self, job_description: str) -> List[str]:
        """
        Generate interview plan based on job description
        
        Args:
            job_description: The job description text
            
        Returns:
            List of topics to cover in the interview
        """
        try:
            logger.info("Generating interview plan")
            parser = PydanticOutputParser(pydantic_object=InterviewPlan)

            template = """
            You are a senior hiring manager. Read the job description and generate a list of 5 key topics to discuss.

            You MUST format your output as a JSON object with a single key "topics".

            Example Format:
            {{
              "topics": ["Python fundamentals", "FastAPI experience", "Database knowledge", "Team collaboration", "Problem-solving skills"]
            }}

            Job Description:
            {jd}
            """
            prompt = PromptTemplate(template=template, input_variables=["jd"])
            chain = prompt | self.llm | parser
            plan = chain.invoke({"jd": job_description})
            
            logger.info(f"✅ Interview plan generated with {len(plan.topics)} topics")
            return plan.topics
            
        except Exception as e:
            logger.error(f"❌ Error generating interview plan: {e}")
            raise

    async def generate_question(self, 
                               interview_plan: List[str],
                               conversation_history: List[Dict],
                               evaluations: List[Dict]) -> str:
        """
        Generate the next interview question
        
        Args:
            interview_plan: List of topics to cover
            conversation_history: Previous Q&A pairs
            evaluations: Previous evaluations
            
        Returns:
            The next question to ask
        """
        try:
            logger.info("Generating next question")
            
            instruction = "You are an expert interviewer. "
            if evaluations and evaluations[-1]['rating'] < 3:
                instruction += f"The candidate's previous answer was weak. Ask a follow-up question to probe deeper into the topic of: '{conversation_history[-1]['question']}'."
            else:
                next_topic = interview_plan[len(evaluations)] if len(evaluations) < len(interview_plan) else "a final concluding question"
                instruction += f"Based on the interview plan, ask the next question about the topic: '{next_topic}'."
                
            parser = PydanticOutputParser(pydantic_object=Question)
            template = """
            {instruction}

            You MUST format your output as a JSON object with a single key "question".

            Example Format:
            {{
                "question": "Can you describe a challenging project you worked on using FastAPI?"
            }}

            Conversation History:
            {history}
            """
            prompt = PromptTemplate(template=template, input_variables=["instruction", "history"])
            chain = prompt | self.llm | parser
            question_obj = chain.invoke({"instruction": instruction, "history": conversation_history})
            
            logger.info("✅ Question generated successfully")
            return question_obj.question
            
        except Exception as e:
            logger.error(f"❌ Error generating question: {e}")
            raise

    async def evaluate_answer(self, question: str, answer: str) -> Dict:
        """
        Evaluate candidate's answer
        
        Args:
            question: The question that was asked
            answer: The candidate's answer
            
        Returns:
            Evaluation with rating and feedback
        """
        try:
            logger.info("Evaluating answer")
            
            parser = PydanticOutputParser(pydantic_object=Evaluation)
            template = """
            You are an expert interview evaluator. Evaluate the candidate's answer based on the question asked.

            You MUST format your output as a JSON object with the keys "rating" and "feedback".

            Example Format:
            {{
                "rating": 4,
                "feedback": "The candidate provided a solid, real-world example and clearly explained the technical challenges."
            }}

            Question:
            {question}
            
            Candidate's Answer:
            {answer}
            """
            prompt = PromptTemplate(template=template, input_variables=["question", "answer"])
            chain = prompt | self.llm | parser
            evaluation = chain.invoke({"question": question, "answer": answer})
            
            logger.info(f"✅ Answer evaluated with rating: {evaluation.rating}")
            return evaluation.model_dump()
            
        except Exception as e:
            logger.error(f"❌ Error evaluating answer: {e}")
            raise

    async def summarize_interview(self, 
                                  conversation_history: List[Dict],
                                  evaluations: List[Dict]) -> Dict:
        """
        Generate final interview summary and recommendation
        
        Args:
            conversation_history: All Q&A pairs from the interview
            evaluations: All evaluations
            
        Returns:
            Summary with recommendation and summary text
        """
        try:
            logger.info("Generating interview summary")
            
            parser = PydanticOutputParser(pydantic_object=Summary)
            template = """
            You are a senior hiring manager. Based on the entire interview, write a final summary and provide a hiring recommendation.

            You MUST format your output as a JSON object with the keys "recommendation" and "summary_text".
            The "recommendation" value MUST be one of the following exact strings: "Proceed", "Hold", or "Reject".

            Example Format:
            {{
                "recommendation": "Proceed",
                "summary_text": "The candidate demonstrated strong technical skills in Python and FastAPI. They communicated effectively and showed good problem-solving abilities. Recommend proceeding to the next round."
            }}

            Interview Transcript:
            {history}

            Evaluations:
            {evals}
            """
            prompt = PromptTemplate(template=template, input_variables=["history", "evals"])
            chain = prompt | self.llm | parser
            summary = chain.invoke({"history": conversation_history, "evals": evaluations})
            
            logger.info(f"✅ Interview summarized with recommendation: {summary.recommendation}")
            return summary.model_dump()
            
        except Exception as e:
            logger.error(f"❌ Error summarizing interview: {e}")
            raise

# Global service instance
interview_service = InterviewerService()

