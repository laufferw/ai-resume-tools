#!/usr/bin/env python3
"""
AI Resume Tools

This application uses AI to generate customized cover letters and adapt resumes
based on job descriptions, using OpenAI APIs via LangChain.
"""

import os
import sys
import argparse
import json
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
import docx
import tkinter as tk
from tkinter import filedialog

# Import LangChain and OpenAI components
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain.schema.runnable import RunnableSequence
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if API key is available
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY not found in environment variables.")
    print("Please add your OpenAI API key to the .env file.")
    sys.exit(1)

# Initialize OpenAI model
llm = ChatOpenAI(
    model_name="gpt-4o",  # Using the most capable model, change to gpt-3.5-turbo for cost savings
    temperature=0.7,
)

# Define output models
class ResumeAnalysis(BaseModel):
    """Analysis of a resume."""
    skills: list[str] = Field(description="List of skills extracted from the resume")
    experience: list[Dict[str, Any]] = Field(description="List of work experiences")
    education: list[Dict[str, Any]] = Field(description="Educational background")
    summary: str = Field(description="Brief summary of the candidate's profile")

class JobAnalysis(BaseModel):
    """Analysis of a job description."""
    required_skills: list[str] = Field(description="Skills required for the job")
    preferred_skills: list[str] = Field(description="Skills that are preferred but not required")
    responsibilities: list[str] = Field(description="Key job responsibilities")
    company_values: list[str] = Field(description="Company values extracted from the description")
    keywords: list[str] = Field(description="Important keywords from the job description")

class JobMatch(BaseModel):
    """Analysis of how well a resume matches a job description."""
    match_score: int = Field(description="Percentage (0-100) representing overall match")
    matching_skills: list[str] = Field(description="List of skills that match job requirements")
    missing_skills: list[str] = Field(description="List of required skills missing from resume")
    experience_alignment: str = Field(description="Description of how experience aligns with job")
    recommendations: list[str] = Field(description="List of specific recommendations to improve match")
    strengths: list[str] = Field(description="List of candidate's strengths for this position")
    weaknesses: list[str] = Field(description="List of areas where the candidate may fall short")

class ResumeCustomization(BaseModel):
    """Customization suggestions for a resume."""
    highlighted_skills: list[str] = Field(description="Skills to highlight based on job match")
    experience_emphasize: Dict[str, list[str]] = Field(description="Aspects of experience to emphasize")
    suggested_additions: list[str] = Field(description="Suggested additions to the resume")
    suggested_removals: list[str] = Field(description="Content that could be removed or de-emphasized")

def load_document(file_path: str) -> str:
    """Load a document from a file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File {file_path} not found")
    
    # Check file extension to determine how to load the document
    if path.suffix.lower() == '.docx':
        # Handle .docx files using python-docx
        doc = docx.Document(path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    else:
        # Handle text files and other formats
        return path.read_text()

def analyze_resume(resume_text: str) -> ResumeAnalysis:
    """Analyze a resume and extract structured information."""
    resume_parser = PydanticOutputParser(pydantic_object=ResumeAnalysis)
    
    resume_prompt = PromptTemplate(
        template="Analyze the following resume and extract key information:\n\n{resume}\n\n{format_instructions}",
        input_variables=["resume"],
        partial_variables={"format_instructions": resume_parser.get_format_instructions()},
    )
    
    chain = resume_prompt | llm
    result = chain.invoke({"resume": resume_text})
    
    try:
        # Check if result is an AIMessage object and extract content if needed
        from langchain_core.messages import AIMessage
        if isinstance(result, AIMessage):
            # Extract the content from AIMessage
            result_text = result.content
        else:
            result_text = result
            
        return resume_parser.parse(result_text)
    except Exception as e:
        print(f"Error parsing resume analysis: {e}")
        print("Raw output:", result)
        raise

def analyze_job_description(job_text: str) -> JobAnalysis:
    """Analyze a job description and extract structured information."""
    job_parser = PydanticOutputParser(pydantic_object=JobAnalysis)
    
    job_prompt = PromptTemplate(
        template="Analyze the following job description and extract key information:\n\n{job}\n\n{format_instructions}",
        input_variables=["job"],
        partial_variables={"format_instructions": job_parser.get_format_instructions()},
    )
    
    chain = job_prompt | llm
    result = chain.invoke({"job": job_text})
    
    try:
        # Check if result is an AIMessage object and extract content if needed
        from langchain_core.messages import AIMessage
        if isinstance(result, AIMessage):
            # Extract the content from AIMessage
            result_text = result.content
        else:
            result_text = result
            
        return job_parser.parse(result_text)
    except Exception as e:
        print(f"Error parsing job analysis: {e}")
        print("Raw output:", result)
        raise

def customize_resume(resume_analysis: ResumeAnalysis, job_analysis: JobAnalysis) -> ResumeCustomization:
    """Generate resume customization suggestions based on job description."""
    customization_parser = PydanticOutputParser(pydantic_object=ResumeCustomization)
    
    customization_prompt = PromptTemplate(
        template="""Given a resume analysis and job description analysis, suggest ways to customize the resume:
        
Resume Analysis:
{resume_analysis}

Job Analysis:
{job_analysis}

{format_instructions}
        """,
        input_variables=["resume_analysis", "job_analysis"],
        partial_variables={"format_instructions": customization_parser.get_format_instructions()},
    )
    
    chain = customization_prompt | llm
    result = chain.invoke({"resume_analysis": resume_analysis.model_dump_json(), "job_analysis": job_analysis.model_dump_json()})
    
    try:
        # Check if result is an AIMessage object and extract content if needed
        from langchain_core.messages import AIMessage
        if isinstance(result, AIMessage):
            # Extract the content from AIMessage
            result_text = result.content
        else:
            result_text = result
            
        return customization_parser.parse(result_text)
    except Exception as e:
        print(f"Error parsing customization suggestions: {e}")
        print("Raw output:", result)
        raise

def generate_cover_letter(resume_analysis: ResumeAnalysis, job_analysis: JobAnalysis, 
                         candidate_name: str, company_name: str) -> str:
    """Generate a cover letter based on resume and job description analysis."""
    cover_letter_prompt = ChatPromptTemplate.from_template("""
You are a professional cover letter writer. Create a compelling cover letter for {candidate_name} applying to {company_name}.
The cover letter should be professional, engaging, and tailored to the specific job.

Resume Information:
{resume_info}

Job Information:
{job_info}

Important guidelines:
1. Keep the length to one page (approximately 400 words)
2. Address how the candidate's experience aligns with job requirements
3. Highlight relevant skills and achievements
4. Demonstrate understanding of the company values
5. Include a strong opening and closing
6. Use a professional, confident tone
7. Format as a formal business letter

Create the full cover letter text now:
""")
    
    chain = cover_letter_prompt | llm
    
    result = chain.invoke({
        "candidate_name": candidate_name,
        "company_name": company_name,
        "resume_info": resume_analysis.model_dump_json(),
        "job_info": job_analysis.model_dump_json()
    })
    
    # Check if result is an AIMessage object and extract content if needed
    from langchain_core.messages import AIMessage
    if isinstance(result, AIMessage):
        # Extract the content from AIMessage
        return result.content
    else:
        return result

def generate_customized_resume(resume_text: str, customization: ResumeCustomization) -> str:
    """Generate a customized resume based on original resume and customization suggestions."""
    resume_prompt = ChatPromptTemplate.from_template("""
You are a professional resume writer. Create a customized version of the following resume based on the customization suggestions.
Keep the same general format, but implement the suggested changes to better target the specific job opportunity.

Original Resume:
{resume}

Customization Suggestions:
{customization}

Important guidelines:
1. Highlight the skills that match the job requirements
2. Emphasize relevant experience aspects
3. Add suggested content where appropriate
4. Remove or de-emphasize less relevant content
5. Keep professional formatting
6. Maintain approximately the same length as the original

Create the full customized resume now:
""")
    
    chain = resume_prompt | llm
    
    return chain.invoke({
        "resume": resume_text,
        "customization": customization.model_dump_json()
    })

def save_document(content: str, file_path: str) -> None:
    """Save content to a file."""
    path = Path(file_path)
    path.write_text(content)
    print(f"Document saved to {file_path}")

def main():
    parser = argparse.ArgumentParser(description="AI Resume Tools - Generate cover letters and customize resumes")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Cover letter generation command
    cover_letter_parser = subparsers.add_parser("cover-letter", help="Generate a cover letter")
    cover_letter_parser.add_argument("--resume", required=True, help="Path to resume file")
    cover_letter_parser.add_argument("--job", required=True, help="Path to job description file")
    cover_letter_parser.add_argument("--name", required=True, help="Candidate's name")
    cover_letter_parser.add_argument("--company", required=True, help="Company name")
    cover_letter_parser.add_argument("--output", required=False, help="Output file path")
    
    # Resume customization command
    resume_parser = subparsers.add_parser("customize-resume", help="Customize a resume for a job")
    resume_parser.add_argument("--resume", required=True, help="Path to resume file")
    resume_parser.add_argument("--job", required=True, help="Path to job description file")
    resume_parser.add_argument("--output", default="customized_resume.txt", help="Output file path")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a resume or job description")
    analyze_parser.add_argument("--type", choices=["resume", "job"], required=True, help="Type of document to analyze")
    analyze_parser.add_argument("--file", required=True, help="Path to file")
    analyze_parser.add_argument("--output", help="Output JSON file path")
    
    args = parser.parse_args()
    
    if args.command == "cover-letter":
        # Load documents
        resume_text = load_document(args.resume)
        job_text = load_document(args.job)
        
        # Analyze documents
        print("Analyzing resume...")
        resume_analysis = analyze_resume(resume_text)
        print("Analyzing job description...")
        job_analysis = analyze_job_description(job_text)
        
        # Generate cover letter
        print("Generating cover letter...")
        cover_letter = generate_cover_letter(
            resume_analysis, 
            job_analysis, 
            args.name, 
            args.company
        )
        
        # Save the cover letter
        save_document(cover_letter, args.output)
        
    elif args.command == "customize-resume":
        # Load documents
        resume_text = load_document(args.resume)
        job_text = load_document(args.job)
        
        # Analyze documents
        print("Analyzing resume...")
        resume_analysis = analyze_resume(resume_text)
        print("Analyzing job description...")
        job_analysis = analyze_job_description(job_text)
        
        # Generate customization suggestions
        print("Generating customization suggestions...")
        customization = customize_resume(resume_analysis, job_analysis)
        
        # Generate customized resume
        print("Customizing resume...")
        customized_resume = generate_customized_resume(resume_text, customization)
        
        # Save the customized resume
        save_document(customized_resume, args.output)
        
    elif args.command == "analyze":
        if args.type == "resume":
            text = load_document(args.file)
            print("Analyzing resume...")
            analysis = analyze_resume(text)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(analysis.model_dump_json(indent=2))
            else:
                print(analysis.model_dump_json(indent=2))
                
        elif args.type == "job":
            text = load_document(args.file)
            print("Analyzing job description...")
            analysis = analyze_job_description(text)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(analysis.model_dump_json(indent=2))
            else:
                print(analysis.model_dump_json(indent=2))
    
    else:
        parser.print_help()

# Wrapper functions for GUI integration
def analyze_document(file_path: str, doc_type: str) -> str:
    """
    Analyze a document and return the analysis as a formatted string.
    
    Args:
        file_path: Path to the document file
        doc_type: Type of document ('resume' or 'job')
    
    Returns:
        Formatted string with analysis results
    """
    try:
        text = load_document(file_path)
        
        if doc_type.lower() == "resume":
            print("Analyzing resume...")
            analysis = analyze_resume(text)
            return json.dumps(json.loads(analysis.model_dump_json()), indent=2)
        elif doc_type.lower() == "job":
            print("Analyzing job description...")
            analysis = analyze_job_description(text)
            return json.dumps(json.loads(analysis.model_dump_json()), indent=2)
        else:
            return f"Error: Invalid document type '{doc_type}'. Must be 'resume' or 'job'."
    except Exception as e:
        return f"Error analyzing document: {str(e)}"

def process_resume_customization(resume_path: str, job_path: str, output_path: str) -> str:
    """
    Load documents, analyze them, and generate a customized resume.
    
    Args:
        resume_path: Path to the resume file
        job_path: Path to the job description file
        output_path: Path to save the customized resume
    
    Returns:
        Status message
    """
    try:
        # Load documents
        resume_text = load_document(resume_path)
        job_text = load_document(job_path)
        
        # Analyze documents
        print("Analyzing resume...")
        resume_analysis = analyze_resume(resume_text)
        print("Analyzing job description...")
        job_analysis = analyze_job_description(job_text)
        
        # Generate customization suggestions
        print("Generating customization suggestions...")
        customization = customize_resume(resume_analysis, job_analysis)
        
        # Generate customized resume
        print("Customizing resume...")
        customized_resume = generate_customized_resume(resume_text, customization)
        
        # Save the customized resume
        save_document(customized_resume, output_path)
        
        return f"Successfully customized resume and saved to {output_path}"
    except Exception as e:
        return f"Error customizing resume: {str(e)}"

def process_cover_letter(resume_path: str, job_path: str, name: str, company: str, output_path: Optional[str] = None) -> str:
    """
    Load documents, analyze them, and generate a cover letter.
    
    Args:
        resume_path: Path to the resume file
        job_path: Path to the job description file
        name: Candidate's name
        company: Company name
        output_path: Path to save the cover letter, if None or empty a file dialog will be shown
    
    Returns:
        Status message
    """
    try:
        # Load documents
        resume_text = load_document(resume_path)
        job_text = load_document(job_path)
        
        # Analyze documents
        print("Analyzing resume...")
        resume_analysis = analyze_resume(resume_text)
        print("Analyzing job description...")
        job_analysis = analyze_job_description(job_text)
        
        # Generate cover letter
        print("Generating cover letter...")
        cover_letter = generate_cover_letter(
            resume_analysis, 
            job_analysis, 
            name, 
            company
        )
        
        # If output_path is None or empty, prompt user for save location
        if not output_path:
            # Create a root window and hide it
            root = tk.Tk()
            root.withdraw()
            
            # Show file save dialog
            output_path = filedialog.asksaveasfilename(
                initialfile="cover_letter.txt",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            # If user cancels the dialog
            if not output_path:
                return "Error: Cover letter generation canceled. No output location selected."
        
        # Save the cover letter
        save_document(cover_letter, output_path)
        
        return f"Successfully generated cover letter and saved to {output_path}"
    except Exception as e:
        return f"Error generating cover letter: {str(e)}"

def compare_resume_to_job(resume_path: str, job_description_path: str) -> JobMatch:
    """
    Compare a resume to a job description and return a detailed match analysis.
    
    Args:
        resume_path: Path to the resume file
        job_description_path: Path to the job description file
    
    Returns:
        JobMatch object with detailed analysis
    """
    # Load and analyze the resume
    resume_text = load_document(resume_path)
    resume_analysis = analyze_resume(resume_text)
    
    # Load and analyze the job description
    job_text = load_document(job_description_path)
    job_analysis = analyze_job_description(job_text)
    
    # Create a parser for the JobMatch output
    job_match_parser = PydanticOutputParser(pydantic_object=JobMatch)
    
    # Create a prompt template for the comparison
    match_prompt = PromptTemplate(
        template="""
Analyze how well the resume matches the job description and provide a detailed assessment:

Resume Analysis:
{resume_analysis}

Job Description Analysis:
{job_analysis}

Provide a detailed assessment of how well the candidate's profile matches this job opportunity.
Be objective and analytical, assessing both strengths and weaknesses. 
Consider skills match, experience alignment, and overall fit.

{format_instructions}
""",
        input_variables=["resume_analysis", "job_analysis"],
        partial_variables={"format_instructions": job_match_parser.get_format_instructions()},
    )
    
    # Create and run the chain
    chain = match_prompt | llm
    result = chain.invoke({
        "resume_analysis": resume_analysis.model_dump_json(),
        "job_analysis": job_analysis.model_dump_json()
    })
    
    try:
        # Check if result is an AIMessage object and extract content if needed
        from langchain_core.messages import AIMessage
        if isinstance(result, AIMessage):
            # Extract the content from AIMessage
            result_text = result.content
        else:
            result_text = result
            
        return job_match_parser.parse(result_text)
    except Exception as e:
        print(f"Error parsing job match analysis: {e}")
        print("Raw output:", result)
        raise

def process_job_match(resume_path: str, job_path: str) -> str:
    """
    Compare a resume to a job description and return a detailed match analysis.
    
    Args:
        resume_path: Path to the resume file
        job_path: Path to the job description file
    
    Returns:
        Formatted string with match analysis results
    """
    try:
        print("Analyzing job match...")
        match_analysis = compare_resume_to_job(resume_path, job_path)
        return json.dumps(json.loads(match_analysis.model_dump_json()), indent=2)
    except Exception as e:
        return f"Error analyzing job match: {str(e)}"

if __name__ == "__main__":
    main()



