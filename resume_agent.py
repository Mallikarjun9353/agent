from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import streamlit as st
import os
from datetime import datetime
import re
import subprocess
from pathlib import Path
from typing import Dict, List
import json

# Initialize Gemini Pro
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key="AIzaSyC97ccNamC-m65jCqJop6QeoDi2BEhvJRI",
    temperature=0.7
)

# Configure page settings
st.set_page_config(
    page_title="Resume Tailoring Assistant",
    page_icon="📄",
    layout="wide"
)

def read_base_resume():
    """Read the base LaTeX resume"""
    with open('resume.tex', 'r') as file:
        return file.read()

# These should be variables, not function definitions
analyze_resume_template = """
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

analyze_jd_template = """
Analyze the following job description and extract:
1. Required skills
2. Required experience
3. Key responsibilities
4. Nice-to-have qualifications

Job Description:
{job_description}

Company Name: {company_name}

Compare these requirements with the candidate's current resume:
{resume_content}

Provide:
1. A list of matching qualifications
2. A list of missing or areas needing enhancement
3. Specific suggestions for resume modifications in LaTeX format
4. Sections that should be prioritized or reordered based on the job requirements
"""

generate_latex_modifications_template = """
You are a LaTeX expert. I will provide you with a base LaTeX resume and job requirements. Your task is to:

1. Keep the EXACT same LaTeX structure and formatting
2. DO NOT remove or change any existing LaTeX commands or structure
3. Only ADD or MODIFY content within existing sections
4. Return the COMPLETE LaTeX resume with your modifications

Base LaTeX Resume:
{resume_content}

Job Requirements:
{job_description}

Instructions:
- Analyze the job requirements
- Identify necessary modifications
- Return the COMPLETE modified LaTeX code
- Preserve ALL existing LaTeX commands and structure
- Make sure all LaTeX commands remain intact
- Keep all existing packages and formatting

Return the complete LaTeX resume code with your modifications.
"""

def analyze_resume(resume_content):
    """Analyze the base resume"""
    prompt = PromptTemplate(
        input_variables=["resume_content"],
        template=analyze_resume_template
    )
    response = llm.invoke(prompt.format(resume_content=resume_content))
    return response

def analyze_job_description(resume_content, job_description, company_name):
    """Analyze JD and compare with resume"""
    prompt = PromptTemplate(
        input_variables=["resume_content", "job_description", "company_name"],
        template=analyze_jd_template
    )
    response = llm.invoke(prompt.format(
        resume_content=resume_content,
        job_description=job_description,
        company_name=company_name
    ))
    return response

def generate_latex_modifications(resume_content, job_description):
    """Generate LaTeX modifications"""
    prompt = PromptTemplate(
        input_variables=["resume_content", "job_description"],
        template=generate_latex_modifications_template
    )
    response = llm.invoke(prompt.format(
        resume_content=resume_content,
        job_description=job_description
    ))
    # Convert AIMessage to string
    return str(response.content) if hasattr(response, 'content') else str(response)

def compare_sections(base_resume: str, modified_latex: str) -> List[str]:
    """Compare original and modified resume sections"""
    try:
        # Split both resumes into sections
        def extract_sections(text):
            sections = []
            for line in text.split('\n'):
                if '\\section*{' in line:
                    section_name = line.split('{')[1].split('}')[0]
                    sections.append(section_name)
            return sections

        original_sections = extract_sections(base_resume)
        modified_sections = extract_sections(modified_latex)

        # Find modified sections
        modified = []
        for section in modified_sections:
            if section in original_sections:
                orig_idx = base_resume.find(f"\\section*{{{section}}}")
                mod_idx = modified_latex.find(f"\\section*{{{section}}}")
                
                orig_content = base_resume[orig_idx:base_resume.find("\\section", orig_idx + 1) if base_resume.find("\\section", orig_idx + 1) != -1 else len(base_resume)]
                mod_content = modified_latex[mod_idx:modified_latex.find("\\section", mod_idx + 1) if modified_latex.find("\\section", mod_idx + 1) != -1 else len(modified_latex)]
                
                if orig_content != mod_content:
                    modified.append(section)
            else:
                modified.append(section)

        return modified
    except Exception as e:
        return [f"Error comparing sections: {str(e)}"]

def convert_to_pdf(tex_file: str) -> str:
    """Convert LaTeX file to PDF"""
    try:
        # Get the file name without extension
        pdf_name = Path(tex_file).stem + '.pdf'
        
        # Run pdflatex twice to ensure proper compilation
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"PDF conversion failed: {result.stderr}")
        
        # Clean up auxiliary files
        for ext in ['.aux', '.log', '.out']:
            aux_file = Path(tex_file).stem + ext
            if os.path.exists(aux_file):
                os.remove(aux_file)
                
        return pdf_name
    except Exception as e:
        raise Exception(f"Error converting to PDF: {str(e)}")

def format_changes_summary(modifications: str) -> str:
    """Format the proposed changes in a readable markdown format"""
    return f"""
### Proposed Changes Summary:

The following modifications will be made to your resume:

{modifications}

Please review these changes carefully before accepting.
    """

def apply_latex_modifications(base_resume: str, modifications: str) -> str:
    """Apply the modifications to the base resume"""
    try:
        # Since we're now getting the complete LaTeX code from the LLM,
        # we can directly use the modifications as they include the full resume
        return modifications.strip()
    except Exception as e:
        raise Exception(f"Error applying modifications: {str(e)}")

def create_modified_resume(base_resume: str, modifications: str, company_name: str) -> Dict[str, str]:
    """Create a new version of the resume with modifications"""
    try:
        date_str = datetime.now().strftime("%Y%m%d")
        tex_filename = f"{company_name}_{date_str}_resume.tex"
        
        # Ensure the modifications are properly formatted
        modified_content = modifications.strip()
        
        # Write the new TEX file
        with open(tex_filename, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        # Convert to PDF
        pdf_filename = convert_to_pdf(tex_filename)
        
        # Verify files were created
        if not os.path.exists(tex_filename):
            raise Exception("Failed to create LaTeX file")
        if not os.path.exists(pdf_filename):
            raise Exception("Failed to create PDF file")
            
        return {
            'tex_file': tex_filename,
            'pdf_file': pdf_filename
        }
    except Exception as e:
        raise Exception(f"Error creating modified resume: {str(e)}")

# Modify the Streamlit UI section
def main():
    st.title("🎯 Smart Resume Tailoring Assistant")
    st.write("Let's optimize your resume for the job you're targeting!")

    # Initialize session states
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'modified_latex' not in st.session_state:
        st.session_state.modified_latex = None
    if 'analysis_attempt' not in st.session_state:
        st.session_state.analysis_attempt = 0

    try:
        # Read base resume
        base_resume = read_base_resume()

        # Company name input
        company_name = st.text_input("Enter the company name:")

        # Job description input
        job_description = st.text_area("Enter the job description:", height=200)

        # Analysis button
        if st.button("Analyze and Suggest Modifications"):
            if job_description and company_name:
                with st.spinner("Analyzing your resume and job requirements..."):
                    try:
                        # First, show the current resume analysis
                        st.subheader("Current Resume Analysis")
                        resume_analysis = analyze_resume(base_resume)
                        st.write(resume_analysis)
                        
                        # Then, show the job description analysis and comparison
                        st.subheader("Job Requirements Analysis & Comparison")
                        jd_analysis = analyze_job_description(base_resume, job_description, company_name)
                        st.write(jd_analysis)
                        
                        # Get the complete modified LaTeX code
                        modified_latex = generate_latex_modifications(base_resume, job_description)
                        st.session_state.modified_latex = modified_latex
                        st.session_state.analysis_complete = True
                        st.session_state.company_name = company_name
                        
                        # Show a diff of the changes
                        st.subheader("Summary of Changes")
                        st.markdown("The following sections have been modified:")
                        
                        # Get modified sections
                        modified_sections = compare_sections(base_resume, modified_latex)
                        
                        # Display modified sections
                        if modified_sections:
                            for section in modified_sections:
                                st.markdown(f"- Modified section: `{section}`")
                        else:
                            st.markdown("No significant changes detected in sections.")
                        
                        # Show the complete modified LaTeX code
                        st.subheader("Complete Modified Resume")
                        st.code(modified_latex, language='latex')
                        
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
            else:
                st.warning("Please enter both company name and job description.")

        # Only show accept/reject buttons if analysis is complete
        if st.session_state.analysis_complete:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Accept Modifications", key="accept"):
                    try:
                        with st.spinner("Creating your customized resume..."):
                            files = create_modified_resume(
                                base_resume,
                                st.session_state.modified_latex,
                                st.session_state.company_name
                            )
                            
                            # Create download buttons for both files
                            with open(files['tex_file'], 'r', encoding='utf-8') as tex_file:
                                tex_content = tex_file.read()
                                st.download_button(
                                    label="Download LaTeX File",
                                    data=tex_content,
                                    file_name=files['tex_file'],
                                    mime='text/plain'
                                )
                            
                            if os.path.exists(files['pdf_file']):
                                with open(files['pdf_file'], 'rb') as pdf_file:
                                    pdf_content = pdf_file.read()
                                    st.download_button(
                                        label="Download PDF File",
                                        data=pdf_content,
                                        file_name=files['pdf_file'],
                                        mime='application/pdf'
                                    )
                            
                            st.success(f"""
                            Resume created successfully!
                            Files created:
                            - LaTeX file: {files['tex_file']}
                            - PDF file: {files['pdf_file']}
                            """)
                    except Exception as e:
                        st.error(f"Error creating resume: {str(e)}")
            
            with col2:
                if st.button("Reject & Regenerate", key="reject"):
                    st.session_state.analysis_attempt += 1
                    st.session_state.analysis_complete = False
                    st.session_state.modified_latex = None
                    st.experimental_rerun()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    # Add footer
    st.markdown("---")
    st.markdown("Built with Streamlit and Google Gemini")
#Testing

if __name__ == "__main__":
    main() 
