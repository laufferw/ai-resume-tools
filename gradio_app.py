"""
AI Resume Tools - Gradio Web Interface

This module provides a web-based interface using Gradio for the AI Resume Tools application.
It allows users to analyze resumes, job descriptions, customize resumes for specific jobs,
generate cover letters, and evaluate job fit.

The interface is designed to be user-friendly and accessible through any web browser.
"""

import os
import tempfile
import gradio as gr
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

# Import necessary functions from main.py
# Import necessary functions from main.py
from main import (
    load_document, 
    analyze_resume, 
    analyze_job_description,
    customize_resume,
    generate_cover_letter,
    compare_resume_to_job
)
# Load environment variables
load_dotenv()

# Check if API key is available
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not found in environment variables. Please set it before using the application.")

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to a temporary location and return the path.
    
    Args:
        uploaded_file: The uploaded file object from Gradio
        
    Returns:
        str: Path to the saved temporary file
    """
    if uploaded_file is None:
        return None
        
    temp_dir = tempfile.mkdtemp()
    
    # Safely access the name attribute
    if hasattr(uploaded_file, 'name'):
        # Check if it's a NamedString object (which has a name but no read method)
        if type(uploaded_file).__name__ == 'NamedString':
            # Extract just the filename from the path
            filename = os.path.basename(uploaded_file.name)
        else:
            filename = uploaded_file.name
    else:
        filename = "uploaded_file.txt"
    
    temp_path = os.path.join(temp_dir, filename)
    
    # Check if the file is likely a binary file based on extension
    binary_extensions = ['.docx', '.pdf', '.xlsx', '.pptx', '.zip', '.png', '.jpg', '.jpeg', '.gif']
    is_binary = any(filename.lower().endswith(ext) for ext in binary_extensions)
    
    try:
        # Safely attempt to read the file
        if hasattr(uploaded_file, 'read'):
            file_content = uploaded_file.read()
            with open(temp_path, "wb") as f:
                f.write(file_content)
        else:
            # Handle NamedString objects (which are essentially strings with a name attribute)
            if type(uploaded_file).__name__ == 'NamedString':
                # Check if the name attribute contains a valid file path
                if hasattr(uploaded_file, 'name') and os.path.isfile(uploaded_file.name):
                    # If it's a valid file path, copy the content from that file
                    print(f"Reading file directly from path: {uploaded_file.name}")
                    if is_binary:
                        # For binary files, read and write in binary mode
                        with open(uploaded_file.name, "rb") as src_file, open(temp_path, "wb") as dest_file:
                            dest_file.write(src_file.read())
                    else:
                        # For text files, read and write in text mode
                        with open(uploaded_file.name, "r") as src_file, open(temp_path, "w") as dest_file:
                            dest_file.write(src_file.read())
                else:
                    # If it's not a valid file path, handle as before
                    print(f"NamedString doesn't contain a valid file path: {uploaded_file.name}")
                    
                    if is_binary:
                        # For binary files, write in binary mode
                        with open(temp_path, "wb") as f:
                            f.write(str(uploaded_file).encode())
                    else:
                        # For text files, write in text mode
                        with open(temp_path, "w") as f:
                            f.write(str(uploaded_file))
            # Try to handle the case where it might be a string or bytes
            elif isinstance(uploaded_file, (str, bytes)):
                with open(temp_path, "wb") as f:
                    content = uploaded_file if isinstance(uploaded_file, bytes) else uploaded_file.encode()
                    f.write(content)
            else:
                raise AttributeError("Object has no 'read' method and is not a string or bytes")
    except Exception as e:
        raise
    
    return temp_path

def process_resume_analysis(resume_file):
    """
    Process the resume analysis and return the results.
    
    Args:
        resume_file: Uploaded resume file
        
    Returns:
        str: Analysis results or error message
    """
    try:
        if resume_file is None:
            return "Please upload a resume file."
            
        temp_path = save_uploaded_file(resume_file)
        if not temp_path:
            return "Error saving uploaded file."
            
        resume_text = load_document(temp_path)
        analysis_result = analyze_resume(resume_text)
        
        # Format the result for display
        formatted_result = f"## Resume Analysis Results\n\n"
        formatted_result += f"### Summary\n{analysis_result.summary}\n\n"
        formatted_result += f"### Skills\n{', '.join(analysis_result.skills)}\n\n"
        
        # Format experience (list of dictionaries)
        formatted_result += f"### Experience\n"
        for exp in analysis_result.experience:
            formatted_result += f"- **{exp.get('title', 'Role')}** at *{exp.get('company', 'Company')}*\n"
            if 'dates' in exp:
                formatted_result += f"  {exp['dates']}\n"
            if 'description' in exp:
                formatted_result += f"  {exp['description']}\n"
            formatted_result += "\n"
        
        # Format education (list of dictionaries)
        formatted_result += f"### Education\n"
        for edu in analysis_result.education:
            formatted_result += f"- **{edu.get('degree', 'Degree')}** from *{edu.get('institution', 'Institution')}*\n"
            if 'dates' in edu:
                formatted_result += f"  {edu['dates']}\n"
            if 'description' in edu:
                formatted_result += f"  {edu['description']}\n"
            formatted_result += "\n"
        
        return formatted_result
    except Exception as e:
        return f"Error analyzing resume: {str(e)}"

def process_job_analysis(job_description):
    """
    Process the job description analysis and return the results.
    
    Args:
        job_description: Job description text
        
    Returns:
        str: Analysis results or error message
    """
    try:
        if not job_description or job_description.strip() == "":
            return "Please enter a job description."
            
        analysis_result = analyze_job_description(job_description)
        
        # Format the result for display
        formatted_result = f"## Job Analysis Results\n\n"
        formatted_result += f"### Required Skills\n{', '.join(analysis_result.required_skills)}\n\n"
        formatted_result += f"### Preferred Skills\n{', '.join(analysis_result.preferred_skills)}\n\n"
        
        # Format responsibilities as a list if it's a list, otherwise as text
        formatted_result += f"### Responsibilities\n"
        if isinstance(analysis_result.responsibilities, list):
            for resp in analysis_result.responsibilities:
                formatted_result += f"- {resp}\n"
            formatted_result += "\n"
        else:
            formatted_result += f"{analysis_result.responsibilities}\n\n"
        
        formatted_result += f"### Company Values\n"
        if isinstance(analysis_result.company_values, list):
            for value in analysis_result.company_values:
                formatted_result += f"- {value}\n"
            formatted_result += "\n"
        else:
            formatted_result += f"{analysis_result.company_values}\n\n"
        
        formatted_result += f"### Keywords\n{', '.join(analysis_result.keywords)}\n\n"
        
        return formatted_result
    except Exception as e:
        return f"Error analyzing job description: {str(e)}"

def process_resume_customization(resume_file, job_description):
    """
    Process resume customization for a specific job and return the results.
    
    Args:
        resume_file: Uploaded resume file
        job_description: Job description text
        
    Returns:
        str: Customization recommendations or error message
    """
    try:
        if resume_file is None:
            return "Please upload a resume file."
            
        if not job_description or job_description.strip() == "":
            return "Please enter a job description."
            
        temp_path = save_uploaded_file(resume_file)
        if not temp_path:
            return "Error saving uploaded file."
            
        resume_text = load_document(temp_path)
        # First analyze the resume and job description
        resume_analysis = analyze_resume(resume_text)
        job_analysis = analyze_job_description(job_description)
        # Then customize the resume
        customization_result = customize_resume(resume_analysis, job_analysis)
        
        # Format the result for display
        formatted_result = f"## Resume Customization Recommendations\n\n"
        formatted_result += f"### Highlighted Skills\n{', '.join(customization_result.highlighted_skills)}\n\n"
        formatted_result += f"### Experience to Emphasize\n{customization_result.experience_emphasize}\n\n"
        formatted_result += f"### Suggested Additions\n{customization_result.suggested_additions}\n\n"
        formatted_result += f"### Suggested Removals\n{customization_result.suggested_removals}\n\n"
        
        return formatted_result
    except Exception as e:
        return f"Error customizing resume: {str(e)}"

def process_cover_letter_generation(resume_file, job_description, candidate_name, company_name):
    """
    Generate a cover letter based on a resume and job description.
    
    Args:
        resume_file: Uploaded resume file
        job_description: Job description text
        candidate_name: Name of the candidate
        company_name: Name of the company
        
    Returns:
        str: Generated cover letter or error message
    """
    try:
        if resume_file is None:
            return "Please upload a resume file."
            
        if not job_description or job_description.strip() == "":
            return "Please enter a job description."
            
        temp_path = save_uploaded_file(resume_file)
        if not temp_path:
            return "Error saving uploaded file."
            
        resume_text = load_document(temp_path)
        # First analyze the resume and job description
        resume_analysis = analyze_resume(resume_text)
        job_analysis = analyze_job_description(job_description)
        # Then generate the cover letter
        # Use the candidate name and company name from the input fields
        # If they're empty, use default values
        if not candidate_name or candidate_name.strip() == "":
            candidate_name = "Candidate"
        if not company_name or company_name.strip() == "":
            company_name = "Company"
        cover_letter = generate_cover_letter(resume_analysis, job_analysis, candidate_name, company_name)
        
        return cover_letter
    except Exception as e:
        return f"Error generating cover letter: {str(e)}"

def process_job_match(resume_file, job_description):
    """
    Calculate match percentage between a resume and a job description.
    
    Args:
        resume_file: Uploaded resume file
        job_description: Job description text
        
    Returns:
        tuple: (Match percentage, explanation or error message)
    """
    try:
        if resume_file is None:
            return 0, "Please upload a resume file."
            
        if not job_description or job_description.strip() == "":
            return 0, "Please enter a job description."
        
        # We'll now handle files without 'read' method in save_uploaded_file
        
        # Add debugging to show what file we're processing
        if hasattr(resume_file, 'name'):
            file_name = resume_file.name
            file_extension = Path(file_name).suffix.lower() if file_name else "unknown"
            print(f"Processing resume file: {file_name} (type: {type(resume_file).__name__}, extension: {file_extension})")
        else:
            print(f"Processing resume file with unknown name (type: {type(resume_file).__name__})")
        
        temp_path = save_uploaded_file(resume_file)
        if not temp_path:
            return 0, "Error saving uploaded file."
            
        # Add debugging to show the temporary file path
        print(f"Temporary file saved at: {temp_path}")
        file_extension = Path(temp_path).suffix.lower()
        print(f"File extension: {file_extension}")
            
        resume_text = load_document(temp_path)
        # We need the path for the job description, so save it to a temp file
        job_temp_dir = tempfile.mkdtemp()
        job_temp_path = os.path.join(job_temp_dir, "job_description.txt")
        with open(job_temp_path, "w") as f:
            f.write(job_description)
        
        match_result = compare_resume_to_job(temp_path, job_temp_path)
        
        # Format the result for display
        match_percentage = match_result.match_score
        explanation = f"## Job Match Analysis\n\n"
        explanation += f"Match Score: {match_percentage}%\n\n"
        explanation += f"### Matching Skills\n{', '.join(match_result.matching_skills)}\n\n"
        explanation += f"### Missing Skills\n{', '.join(match_result.missing_skills)}\n\n"
        explanation += f"### Experience Alignment\n{match_result.experience_alignment}\n\n"
        explanation += f"### Strengths\n{', '.join(match_result.strengths)}\n\n"
        explanation += f"### Weaknesses\n{', '.join(match_result.weaknesses)}\n\n"
        explanation += f"### Recommendations\n{', '.join(match_result.recommendations)}\n\n"
        
        return match_percentage, explanation
    except Exception as e:
        return 0, f"Error calculating job match: {str(e)}"

def create_ui():
    """
    Create and configure the Gradio UI components.
    
    Returns:
        gr.Blocks: Configured Gradio interface
    """
    with gr.Blocks(title="AI Resume Tools") as app:
        gr.Markdown("# AI Resume Tools")
        gr.Markdown("Upload your resume and job descriptions to get AI-powered analysis and recommendations.")
        
        with gr.Tab("Resume Analysis"):
            with gr.Row():
                with gr.Column():
                    resume_file_analysis = gr.File(label="Upload Resume", file_types=[".pdf", ".docx", ".txt"])
                    analyze_resume_btn = gr.Button("Analyze Resume", variant="primary")
                with gr.Column():
                    resume_analysis_output = gr.Markdown(label="Analysis Results")
            
            analyze_resume_btn.click(
                fn=process_resume_analysis,
                inputs=[resume_file_analysis],
                outputs=resume_analysis_output
            )
        
        with gr.Tab("Job Description Analysis"):
            with gr.Row():
                with gr.Column():
                    job_description_analysis = gr.Textbox(label="Enter Job Description", lines=10)
                    analyze_job_btn = gr.Button("Analyze Job Description", variant="primary")
                with gr.Column():
                    job_analysis_output = gr.Markdown(label="Analysis Results")
            
            analyze_job_btn.click(
                fn=process_job_analysis,
                inputs=[job_description_analysis],
                outputs=job_analysis_output
            )
        
        with gr.Tab("Resume Customization"):
            with gr.Row():
                with gr.Column():
                    resume_file_custom = gr.File(label="Upload Resume", file_types=[".pdf", ".docx", ".txt"])
                    job_description_custom = gr.Textbox(label="Enter Job Description", lines=10)
                    customize_resume_btn = gr.Button("Customize Resume", variant="primary")
                with gr.Column():
                    customization_output = gr.Markdown(label="Customization Recommendations")
            
            customize_resume_btn.click(
                fn=process_resume_customization,
                inputs=[resume_file_custom, job_description_custom],
                outputs=customization_output
            )
        with gr.Tab("Cover Letter Generation"):
            with gr.Row():
                with gr.Column():
                    resume_file_cover = gr.File(label="Upload Resume", file_types=[".pdf", ".docx", ".txt"])
                    job_description_cover = gr.Textbox(label="Enter Job Description", lines=10)
                    candidate_name = gr.Textbox(label="Your Name", placeholder="Enter your full name")
                    company_name = gr.Textbox(label="Company Name", placeholder="Enter the company name")
                    generate_cover_btn = gr.Button("Generate Cover Letter", variant="primary")
                with gr.Column():
                    cover_letter_output = gr.Textbox(label="Generated Cover Letter", lines=20)
            
            generate_cover_btn.click(
                fn=process_cover_letter_generation,
                inputs=[resume_file_cover, job_description_cover, candidate_name, company_name],
                outputs=cover_letter_output
            )
        
        with gr.Tab("Job Match"):
            with gr.Row():
                with gr.Column():
                    resume_file_match = gr.File(label="Upload Resume", file_types=[".pdf", ".docx", ".txt"])
                    job_description_match = gr.Textbox(label="Enter Job Description", lines=10)
                    calculate_match_btn = gr.Button("Calculate Match", variant="primary")
                with gr.Column():
                    match_percentage = gr.Number(label="Match Percentage")
                    match_explanation = gr.Markdown(label="Match Explanation")
            
            calculate_match_btn.click(
                fn=process_job_match,
                inputs=[resume_file_match, job_description_match],
                outputs=[match_percentage, match_explanation]
            )
        
        gr.Markdown("""
        ## About AI Resume Tools
        
        This application uses AI to help job seekers optimize their resumes and cover letters for specific job opportunities.
        
        Features include:
        - Resume analysis to identify strengths and areas for improvement
        - Job description analysis to understand key requirements
        - Resume customization recommendations for specific jobs
        - Cover letter generation tailored to your resume and the job
        - Job match calculation to assess fit with a position
        
        **Note:** All processing is done locally. Your data is not stored.
        """)
    
    return app

def main():
    """
    Main function to launch the Gradio web interface.
    """
    # Create and launch the UI
    app = create_ui()
    app.launch(share=True)

if __name__ == "__main__":
    main()

