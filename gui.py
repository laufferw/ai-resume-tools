import os
import sys
import threading
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import docx
import main  # Import functionality from main.py

class AIResumeToolsGUI:
    def __init__(self, root):
        self.root = root
        self.root = root
        self.root.title("AI Resume Tools v1.0")
        self.root.geometry("900x700")
        
        # Create variables to store file paths
        # Create variables to store file paths
        self.resume_path = tk.StringVar()
        self.job_desc_path = tk.StringVar()
        self.job_desc_text = tk.StringVar()  # Added variable for pasted job description text
        self.output_path = tk.StringVar()
        self.candidate_name = tk.StringVar()
        self.company_name = tk.StringVar()
        self.ask_each_time = tk.BooleanVar(value=False)  # Variable for "Ask each time" checkbox
        # Create status variables
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.is_processing = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.root, text="AI Resume Tools v1.0", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 20))
        
        # Help button
        help_button = ttk.Button(self.root, text="?", width=3, command=self.show_help)
        help_button.grid(row=0, column=3, sticky="e", pady=(0, 20))
        
        # File Selection Frame
        file_frame = ttk.LabelFrame(self.root, text="File Selection")
        file_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        file_frame.columnconfigure(1, weight=1)
        
        # Resume file
        ttk.Label(file_frame, text="Resume:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.resume_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_resume).grid(row=0, column=2, padx=5, pady=5)
        
        # Job description file
        ttk.Label(file_frame, text="Job Description:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.job_desc_path, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_job_desc).grid(row=1, column=2, padx=5, pady=5)
        
        # Job Description Text Box
        jd_text_frame = ttk.LabelFrame(self.root, text="Paste Job Description Here")
        jd_text_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        jd_text_frame.columnconfigure(0, weight=1)
        jd_text_frame.rowconfigure(0, weight=1)
        
        self.job_desc_text_area = scrolledtext.ScrolledText(jd_text_frame, wrap=tk.WORD, width=80, height=10)
        self.job_desc_text_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Add note about priority
        ttk.Label(jd_text_frame, text="Note: Pasted text will be used over file input if both are provided.", 
                  font=("Arial", 8, "italic")).grid(row=1, column=0, sticky="w", padx=5, pady=(0, 5))
        
        # Output file
        ttk.Label(file_frame, text="Output File:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.output_entry = ttk.Entry(file_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=2, column=2, padx=5, pady=5)
        
        # Add "Ask each time" checkbox
        ask_each_time_cb = ttk.Checkbutton(file_frame, text="Ask each time", variable=self.ask_each_time, 
                                           command=self.toggle_output_entry_state)
        ask_each_time_cb.grid(row=2, column=3, padx=5, pady=5)
        
        # Info Frame for Cover Letter
        info_frame = ttk.LabelFrame(self.root, text="Additional Information (for Cover Letter)")
        info_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        info_frame.columnconfigure(1, weight=1)
        
        # Candidate name
        ttk.Label(info_frame, text="Candidate Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.candidate_name, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Company name
        ttk.Label(info_frame, text="Company Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(info_frame, textvariable=self.company_name, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Action Buttons
        action_frame = ttk.Frame(self.root)
        action_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        ttk.Button(action_frame, text="Analyze Resume", command=lambda: self.run_task("analyze_resume")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(action_frame, text="Analyze Job Description", command=lambda: self.run_task("analyze_job")).grid(row=0, column=1, padx=5, pady=5)
        
        # Use lambda to pass the task_type to browse_output when opening the file dialog
        customize_btn = ttk.Button(action_frame, text="Customize Resume", 
                               command=lambda: self.run_task("customize_resume"))
        customize_btn.grid(row=0, column=2, padx=5, pady=5)
        customize_btn.bind("<Button-3>", lambda e: self.browse_output("customize_resume"))
        
        cover_letter_btn = ttk.Button(action_frame, text="Generate Cover Letter", 
                                 command=lambda: self.run_task("cover_letter"))
        cover_letter_btn.grid(row=0, column=3, padx=5, pady=5)
        cover_letter_btn.grid(row=0, column=3, padx=5, pady=5)
        cover_letter_btn.bind("<Button-3>", lambda e: self.browse_output("cover_letter"))
        
        # Add Match Job Fit button
        match_job_btn = ttk.Button(action_frame, text="Match Job Fit", 
                               command=lambda: self.run_task("match_job"))
        match_job_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # Results area
        result_frame = ttk.LabelFrame(self.root, text="Results")
        result_frame.grid(row=5, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)
        self.root.rowconfigure(5, weight=1)
        result_frame.rowconfigure(0, weight=1)
        result_frame.columnconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, width=80, height=20)
        self.result_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=6, column=0, columnspan=4, sticky="ew", padx=5, pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        status_frame.columnconfigure(0, weight=1)
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=1, padx=5, pady=5)
    
    def browse_resume(self):
        filename = filedialog.askopenfilename(
            title="Select Resume",
            filetypes=[("Word Documents", "*.docx"), ("All files", "*.*")]
        )
        if filename:
            self.resume_path.set(filename)
            # Try to extract candidate name from filename
            name = Path(filename).stem
            if "-" in name:
                name = name.split("-")[0].strip()
            self.candidate_name.set(name)
    
    def browse_job_desc(self):
        filename = filedialog.askopenfilename(
            title="Select Job Description",
            filetypes=[("Word Documents", "*.docx"), ("All files", "*.*")]
        )
        if filename:
            self.job_desc_path.set(filename)
    
    def browse_output(self, task_type=None):
        # Set a descriptive default filename based on the operation
        initial_file = ""
        if task_type == "cover_letter":
            initial_file = "Cover_Letter.docx"
        elif task_type == "customize_resume":
            initial_file = "Customized_Resume.docx"
        
        filename = filedialog.asksaveasfilename(
            title="Save Output As",
            defaultextension=".docx",
            initialfile=initial_file,
            filetypes=[("Word Documents", "*.docx"), ("Text files", "*.txt")]
        )
        if filename:
            self.output_path.set(filename)
            # Uncheck "Ask each time" checkbox if user manually selects a file
            self.ask_each_time.set(False)
            self.toggle_output_entry_state()
    
    def toggle_output_entry_state(self):
        """Enable or disable the output entry field based on the 'Ask each time' checkbox"""
        if self.ask_each_time.get():
            self.output_entry.configure(state="disabled")
            self.output_path.set("")
        else:
            self.output_entry.configure(state="normal")
    
    def run_task(self, task_type):
        if self.is_processing:
            messagebox.showwarning("Process Running", "Please wait until the current task completes.")
            return
        
        # Validate inputs
        if task_type in ["analyze_resume", "customize_resume", "cover_letter"]:
            if not self.resume_path.get():
                messagebox.showerror("Input Error", "Please select a resume file.")
                return
        
        if task_type in ["analyze_job", "customize_resume", "cover_letter", "match_job"]:
            job_desc_text = self.job_desc_text_area.get("1.0", tk.END).strip()
            # Check if either job description file or pasted text is provided
            if not self.job_desc_path.get() and not job_desc_text:
                messagebox.showerror("Input Error", "Please either select a job description file or paste job description text.")
                return
        
        if task_type == "cover_letter":
            if not self.candidate_name.get() or not self.company_name.get():
                messagebox.showerror("Input Error", "Please provide candidate name and company name for cover letter.")
                return
        
        if task_type in ["customize_resume", "cover_letter"]:
            if not self.output_path.get() and not self.ask_each_time.get():
                # Set default output path if none is specified
                data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
                os.makedirs(data_dir, exist_ok=True)
                
                if task_type == "customize_resume":
                    default_filename = "Customized_Resume.docx"
                elif task_type == "cover_letter":
                    default_filename = "Cover_Letter.docx"
                    
                default_path = os.path.join(data_dir, default_filename)
                self.output_path.set(default_path)
                self.result_text.insert(tk.END, f"No output file specified. Using default: {default_path}\n\n")
                
                # Ask user if they want to choose a different location
                should_browse = messagebox.askyesno(
                    "Default Output", 
                    f"Output will be saved to:\n{default_path}\n\nWould you like to select a different location?"
                )
                if should_browse:
                    self.browse_output(task_type)
                    if not self.output_path.get():  # User cancelled file dialog
                        return
        # Run the task in a separate thread to keep UI responsive
        thread = threading.Thread(target=self.execute_task, args=(task_type,))
        thread.daemon = True
        thread.start()
    
    def execute_task(self, task_type):
        self.is_processing = True
        self.status_var.set(f"Processing: {task_type.replace('_', ' ').title()}...")
        self.progress_bar.start(10)
        self.result_text.delete(1.0, tk.END)
        
        try:
            if task_type == "analyze_resume":
                result = self.analyze_document("resume")
            elif task_type == "analyze_job":
                result = self.analyze_document("job")
            elif task_type == "customize_resume":
                result = self.customize_resume()
            elif task_type == "cover_letter":
                result = self.generate_cover_letter()
            elif task_type == "match_job":
                result = self.compare_job_match()
            
            # Update UI with result
            self.root.after(0, lambda: self.update_result(result))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
        
        finally:
            self.root.after(0, self.reset_ui)
    
    def update_result(self, result):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)
    
    def show_error(self, error_msg):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, error_msg)
        messagebox.showerror("Error", error_msg)
    
    def reset_ui(self):
        self.progress_bar.stop()
        self.is_processing = False
        self.status_var.set("Ready")
    
    def analyze_document(self, doc_type):
        try:
            if doc_type == "resume":
                file_path = self.resume_path.get()
                doc_type_str = "resume"
                # Call the analyze function from main.py with file path
                result = main.analyze_document(file_path, doc_type_str)
            else:  # job description
                doc_type_str = "job"
                job_desc_text = self.job_desc_text_area.get("1.0", tk.END).strip()
                
                # Prioritize pasted text over file input
                if job_desc_text:
                    # Save the pasted text to a temporary file
                    temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "temp_job_desc.txt")
                    os.makedirs(os.path.dirname(temp_file), exist_ok=True)
                    
                    with open(temp_file, "w", encoding="utf-8") as f:
                        f.write(job_desc_text)
                    
                    # Call the analyze function with the temp file
                    result = main.analyze_document(temp_file, doc_type_str)
                else:
                    file_path = self.job_desc_path.get()
                    # Call the analyze function with the selected file
                    result = main.analyze_document(file_path, doc_type_str)
            return result
        except Exception as e:
            raise Exception(f"Error analyzing {doc_type}: {str(e)}")
    
    def customize_resume(self):
        try:
            resume_path = self.resume_path.get()
            job_desc_text = self.job_desc_text_area.get("1.0", tk.END).strip()
            output_path = self.output_path.get()
            
            # Determine which job description source to use (prioritize pasted text)
            if job_desc_text:
                # Save the pasted text to a temporary file
                temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "temp_job_desc.txt")
                os.makedirs(os.path.dirname(temp_file), exist_ok=True)
                
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(job_desc_text)
                
                job_path = temp_file
            else:
                job_path = self.job_desc_path.get()
            
            # Call the process_resume_customization function from main.py
            result = main.process_resume_customization(resume_path, job_path, output_path)
            
            # If successful, show success message
            if os.path.exists(output_path):
                # Show success message box
                messagebox.showinfo(
                    "Success", 
                    f"Customized resume created successfully!\nSaved to: {output_path}"
                )
                return f"✅ CUSTOMIZED RESUME CREATED SUCCESSFULLY!\nSaved to: {output_path}\n\n{result}"
            else:
                raise Exception("Output file was not created")
        except Exception as e:
            raise Exception(f"Error customizing resume: {str(e)}")
    
    def generate_cover_letter(self):
        try:
            resume_path = self.resume_path.get()
            job_desc_text = self.job_desc_text_area.get("1.0", tk.END).strip()
            name = self.candidate_name.get()
            company = self.company_name.get()
            
            # Check if "Ask each time" checkbox is checked
            if self.ask_each_time.get():
                output_path = None
            else:
                output_path = self.output_path.get()
            
            # Determine which job description source to use (prioritize pasted text)
            if job_desc_text:
                # Save the pasted text to a temporary file
                temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "temp_job_desc.txt")
                os.makedirs(os.path.dirname(temp_file), exist_ok=True)
                
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(job_desc_text)
                
                job_path = temp_file
            else:
                job_path = self.job_desc_path.get()
            
            # Call the process_cover_letter function from main.py
            result = main.process_cover_letter(resume_path, job_path, name, company, output_path)
            
            # Check if the operation was canceled
            if "Error: Cover letter generation canceled" in result:
                return result
            
            # Extract the actual output path from the result message
            import re
            path_match = re.search(r"saved to (.+)$", result)
            if path_match:
                actual_output_path = path_match.group(1)
                
                # If successful, show success message
                if os.path.exists(actual_output_path):
                    # Show success message box
                    messagebox.showinfo(
                        "Success", 
                        f"Cover letter created successfully!\nSaved to: {actual_output_path}"
                    )
                    return f"✅ COVER LETTER CREATED SUCCESSFULLY!\nSaved to: {actual_output_path}\n\n{result}"
                else:
                    raise Exception("Output file was not created")
            else:
                raise Exception("Could not determine output path from result message")
        except Exception as e:
            raise Exception(f"Error generating cover letter: {str(e)}")
            
    def compare_job_match(self):
        """
        Compare resume with job description to determine fit and provide analysis.
        """
        try:
            resume_path = self.resume_path.get()
            job_desc_text = self.job_desc_text_area.get("1.0", tk.END).strip()
            
            # Determine which job description source to use (prioritize pasted text)
            if job_desc_text:
                # Save the pasted text to a temporary file
                temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "temp_job_desc.txt")
                os.makedirs(os.path.dirname(temp_file), exist_ok=True)
                
                with open(temp_file, "w", encoding="utf-8") as f:
                    f.write(job_desc_text)
                
                job_path = temp_file
            else:
                job_path = self.job_desc_path.get()
            
            # Call the process_job_match function from main.py
            result = main.process_job_match(resume_path, job_path)
            
            # Format the result nicely
            try:
                # Extract JSON content from markdown code blocks if present
                if isinstance(result, str) and "```json" in result and "```" in result:
                    # Find the JSON content between ```json and the next ```
                    start_marker = "```json"
                    end_marker = "```"
                    start_index = result.find(start_marker) + len(start_marker)
                    end_index = result.find(end_marker, start_index)
                    
                    if start_index > 0 and end_index > start_index:
                        # Extract just the JSON content
                        json_content = result[start_index:end_index].strip()
                        job_match = json.loads(json_content)
                    else:
                        # If markers not found as expected, try parsing the whole string
                        job_match = json.loads(result)
                else:
                    # No markdown formatting, parse directly
                    job_match = json.loads(result)
                
                formatted_result = f"# Job Match Analysis\n\n"
                formatted_result += f"## Match Score: {job_match['match_score']}%\n\n"
                
                formatted_result += "## Strengths:\n"
                for strength in job_match['strengths']:
                    formatted_result += f"- {strength}\n"
                
                formatted_result += "\n## Weaknesses:\n"
                for weakness in job_match['weaknesses']:
                    formatted_result += f"- {weakness}\n"
                
                formatted_result += "\n## Matching Skills:\n"
                for skill in job_match['matching_skills']:
                    formatted_result += f"- {skill}\n"
                
                formatted_result += "\n## Missing Skills:\n"
                for skill in job_match['missing_skills']:
                    formatted_result += f"- {skill}\n"
                
                formatted_result += f"\n## Experience Alignment:\n{job_match['experience_alignment']}\n\n"
                
                formatted_result += "## Recommendations:\n"
                for rec in job_match['recommendations']:
                    formatted_result += f"- {rec}\n"
                
                return formatted_result
            except Exception as e:
                # If JSON parsing fails, log the error and return the raw result
                print(f"Error parsing job match result: {e}")
                return result
            
        except Exception as e:
            raise Exception(f"Error analyzing job match: {str(e)}")
            
    def show_help(self):
        """Display help information when the help button is clicked"""
        help_text = """AI Resume Tools v1.0 - Basic Instructions

1. File Selection:
   - Select your resume file (.docx format)
   - Select a job description file (.docx format) OR paste job description text
   - Optionally specify an output file location

2. Analysis:
   - Click "Analyze Resume" to get insights about your resume
   - Click "Analyze Job Description" to extract key requirements
   - Click "Match Job Fit" to see how well your resume matches the job

3. Resume Customization:
   - Click "Customize Resume" to tailor your resume to the job description
   - The customized resume will be saved to the specified output location

4. Cover Letter:
   - Fill in your name and the company name
   - Click "Generate Cover Letter" to create a personalized cover letter
   - The cover letter will be saved to the specified output location

Note: This application requires an OpenAI API key in the .env file.
"""
        messagebox.showinfo("Help", help_text)

def save_as_docx(text, output_path):
    """
    Save text as a properly formatted .docx file
    """
    doc = docx.Document()
    
    # Split text into paragraphs
    paragraphs = text.split('\n')
    
    # Add each paragraph to the document
    for para in paragraphs:
        if para.strip():  # Only add non-empty paragraphs
            doc.add_paragraph(para)
    
    # Save the document
    doc.save(output_path)

def main_gui():
    root = tk.Tk()
    app = AIResumeToolsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main_gui()

