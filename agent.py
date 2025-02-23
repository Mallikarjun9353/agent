from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
# load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="CV Generator",
    page_icon="📄",
    layout="wide"
)

# Initialize Gemini Pro
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key="AIzaSyC97ccNamC-m65jCqJop6QeoDi2BEhvJRI",
    temperature=0.7
)

# System prompt template
cv_template = """
You are a professional CV writer. Based on the following job description, create a tailored CV that highlights relevant skills and experience.

Job Description:
{job_description}

Please create a CV in markdown format that includes:
1. Personal Information (use placeholder data)
2. Professional Summary
3. Key Skills relevant to the job
4. Work Experience (create relevant experience based on the job requirements)
5. Education (create relevant education based on the job requirements)
6. Certifications (if applicable)

Make sure the CV is well-structured, professional, and specifically tailored to the job description.
"""

# Create prompt template
prompt = PromptTemplate(
    input_variables=["job_description"],
    template=cv_template
)

# Create LLM chain
cv_chain = LLMChain(llm=llm, prompt=prompt)

def generate_cv(job_description):
    """Generate CV based on job description"""
    try:
        response = cv_chain.run(job_description=job_description)
        return response
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Streamlit UI
st.title("🤖 AI CV Generator")
st.write("Enter a job description, and I'll generate a tailored CV for you!")

# Job description input
job_description = st.text_area("Enter the job description:", height=200)

if st.button("Generate CV"):
    if job_description:
        with st.spinner("Generating your CV..."):
            cv_content = generate_cv(job_description)
            st.markdown(cv_content)
    else:
        st.warning("Please enter a job description.")

# Add footer
st.markdown("---")
st.markdown("Built with Langchain, Google Gemini, and Streamlit")
