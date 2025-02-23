from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from typing import Any, Dict, List
import os

class LLMHandler:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=api_key,
            temperature=0.7
        )
        
    def analyze_resume(self, resume_content: str) -> str:
        """Analyze the base resume"""
        template = self.get_analyze_resume_template()
        prompt = PromptTemplate(
            input_variables=["resume_content"],
            template=template
        )
        response = self.llm.invoke(prompt.format(resume_content=resume_content))
        return str(response.content) if hasattr(response, 'content') else str(response)

    @staticmethod
    def get_analyze_resume_template() -> str:
        return """
        Analyze the following LaTeX resume and extract key information including:
        1. Skills
        2. Experience
        3. Projects
        4. Education
        5. Achievements

        Resume Content:
        {resume_content}

        Provide a structured analysis of the current resume content.
        """
    
    # Add other template getters and analysis methods... 