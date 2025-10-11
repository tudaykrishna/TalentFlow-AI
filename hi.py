import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, TypedDict, Optional, Literal

from langgraph.graph import StateGraph, END

# Load environment variables from .env file
load_dotenv()

# --- 1. Define the State for our Graph ---
# This TypedDict will be the "memory" of our interview agent.

class InterviewState(TypedDict):
    job_description: str
    interview_plan: Optional[List[str]]
    conversation_history: List[Dict[str, str]]
    evaluations: List[Dict]
    current_question: Optional[str]
    final_summary: Optional[str]
    max_questions: int

# --- 2. Define Pydantic Models for Structured Output ---

class InterviewPlan(BaseModel):
    topics: List[str] = Field(description="A list of 3-5 key technical and behavioral topics to cover in an interview.")

class Question(BaseModel):
    question: str = Field(description="The next question to ask the candidate.")

class Evaluation(BaseModel):
    rating: int = Field(description="A rating of the candidate's answer from 1 (poor) to 5 (excellent).")
    feedback: str = Field(description="A brief justification for the rating, explaining what was good or could be improved.")

class Summary(BaseModel):
    recommendation: Literal["Proceed", "Hold", "Reject"] = Field(description="The final hiring recommendation.")
    summary_text: str = Field(description="A comprehensive summary of the candidate's performance during the interview.")


# --- 3. The AI Core Logic (Nodes of the Graph) ---

class InterviewerAI:
    def __init__(self):
        # Initialize the Azure Chat OpenAI model
        try:
            self.llm = AzureChatOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
                temperature=0.1,
                model_kwargs={
                    "response_format": {"type": "json_object"},
                }
            )
            print("✅ Azure OpenAI model initialized successfully.")
        except Exception as e:
            print(f"❌ Failed to initialize Azure OpenAI model. Please check your .env file and credentials.")
            print(f"Error: {e}")
            raise

    def generate_interview_plan(self, state: InterviewState):
        print("--- Node: Generating Interview Plan ---")
        jd = state['job_description']
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
        plan = chain.invoke({"jd": jd})
        return {"interview_plan": plan.topics}

    def generate_question(self, state: InterviewState):
        print("--- Node: Generating Question ---")
        history = state['conversation_history']
        plan = state['interview_plan']
        evals = state['evaluations']
        
        instruction = "You are an expert interviewer. "
        if evals and evals[-1]['rating'] < 3:
             instruction += f"The candidate's previous answer was weak. Ask a follow-up question to probe deeper into the topic of: '{history[-1]['question']}'."
        else:
            next_topic = plan[len(evals)] if len(evals) < len(plan) else "a final concluding question"
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
        question_obj = chain.invoke({"instruction": instruction, "history": history})
        return {"current_question": question_obj.question}

    def evaluate_answer(self, state: InterviewState):
        print("--- Node: Evaluating Answer ---")
        question = state['current_question']
        
        candidate_answer = input(f"🤖 AI: {question}\n👤 You: ")

        history = state['conversation_history']
        history.append({"question": question, "answer": candidate_answer})
        
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
        evaluation = chain.invoke({"question": question, "answer": candidate_answer})

        evals = state['evaluations']
        evals.append(evaluation.model_dump())
        
        return {"conversation_history": history, "evaluations": evals}

    def summarize_interview(self, state: InterviewState):
        print("--- Node: Summarizing Interview ---")
        history = state['conversation_history']
        evals = state['evaluations']
        
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
        summary = chain.invoke({"history": history, "evals": evals})
        return {"final_summary": summary.model_dump_json(indent=2)}

# --- 4. The Routing Logic (Edges) ---

def route_after_evaluation(state: InterviewState):
    print("--- Edge: Routing after evaluation ---")
    evals = state['evaluations']
    if len(evals) >= state['max_questions']:
        print("Decision: End of interview. Moving to summarize.")
        return "summarize"
    else:
        print("Decision: Continue interview. Moving to generate next question.")
        return "generate_question"

# --- 5. Build and Run the Graph ---

if __name__ == "__main__":
    SAMPLE_JOB_DESCRIPTION = """
    Job Title: Senior Python Developer
    We are looking for a Senior Python Developer with at least 5 years of experience.
    The ideal candidate must be proficient in Python, FastAPI, and PostgreSQL.
    Experience with Docker and AWS is highly preferred. Key responsibilities include
    developing backend services and mentoring junior engineers. The role requires strong
    problem-solving skills and excellent team collaboration.
    """
    
    ai_interviewer = InterviewerAI()

    # Define the graph
    workflow = StateGraph(InterviewState)

    # Add the nodes
    workflow.add_node("generate_plan", ai_interviewer.generate_interview_plan)
    workflow.add_node("generate_question", ai_interviewer.generate_question)
    workflow.add_node("evaluate_answer", ai_interviewer.evaluate_answer)
    workflow.add_node("summarize", ai_interviewer.summarize_interview)

    # Set the entry point
    workflow.set_entry_point("generate_plan")

    # Add the edges
    workflow.add_edge("generate_plan", "generate_question")
    workflow.add_edge("generate_question", "evaluate_answer")
    workflow.add_conditional_edges(
        "evaluate_answer",
        route_after_evaluation,
        {
            "summarize": "summarize",
            "generate_question": "generate_question"
        }
    )
    workflow.add_edge("summarize", END)

    # Compile the graph
    app = workflow.compile()

    # Run the interview
    print("\n--- Starting AI Interview ---")
    initial_state = {
        "job_description": SAMPLE_JOB_DESCRIPTION,
        "conversation_history": [],
        "evaluations": [],
        "max_questions": 4 # Let's do a 4-question interview
    }

    # Use stream to see the output of each step
    final_state_value = None
    for output in app.stream(initial_state):
        # The key is the name of the node that just ran
        for key, value in output.items():
            print(f"\nOutput from node '{key}':")
            print("---")
            final_state_value = value # Continuously update to get the last valid state

    # Access the final summary from the last known state
    if final_state_value:
        final_summary = final_state_value.get('final_summary')
        print("\n\n--- 🚀 Final Interview Summary ---")
        print("---------------------------------")
        print(final_summary)
    else:
        print("\n--- Interview could not be completed. ---")