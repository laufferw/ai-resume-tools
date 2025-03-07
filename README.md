# AI Resume Tools

An AI-powered toolkit to help you customize your resume and generate cover letters tailored to specific job descriptions.

## Project Overview

AI Resume Tools uses OpenAI's large language models to:

1. **Customize your resume** by highlighting relevant skills and experiences based on a job description
2. **Generate personalized cover letters** that match your qualifications with job requirements
3. **Save you time** in the job application process while creating more targeted application materials
The toolkit leverages LangChain for seamless integration with OpenAI models and provides both a graphical user interface and a command-line interface for ease of use.

## Recent Updates

**March 2025**: Updated the project to fix LangChain deprecation warnings by:
- Replaced `LLMChain` with the modern `RunnableSequence` pattern
- Updated all chain executions from `.run()` to `.invoke()`
- Ensured compatibility with the latest LangChain library standards

## Installation

### Prerequisites
- Python 3.6 or higher
- OpenAI API key
- Python-docx library (for .docx file handling)
### Setup

1. Clone this repository or download the source code:
   ```
   git clone <repository-url>
   cd ai-resume-tools
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required dependencies:
   ```
   pip install openai langchain langchain-openai python-dotenv pandas tiktoken python-docx
   ```

4. For the GUI version, you'll also need Tkinter:
   ```
   # On Ubuntu/Debian:
   sudo apt-get install python3-tk
   
   # On macOS (if using Homebrew):
   brew install python-tk
   
   # On Windows:
   # Tkinter is included with Python installations by default
   ```

## Configuration
1. In the project root directory, copy the `.env.example` file to create a new `.env` file:
   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with your actual OpenAI API key from [OpenAI's platform](https://platform.openai.com/api-keys)
## Usage

### GUI Application (Recommended)

Run the graphical user interface for an easier experience:

```bash
python gui.py
```

The GUI provides a user-friendly interface where you can:
- Browse and select your resume and job description files
- Paste job description text directly into the application (alternative to uploading a file)
- Analyze documents to extract key information
- Customize your resume to match job requirements
- Generate tailored cover letters
- Save outputs to specified locations

### Command Line Interface

#### Generate a Cover Letter

```bash
python main.py cover-letter --resume path/to/resume.docx --job path/to/job_description.docx --name "Your Name" --company "Company Name" --output path/to/cover_letter.docx
```

#### Customize Your Resume

```bash
python main.py customize-resume --resume path/to/resume.docx --job path/to/job_description.docx --output path/to/customized_resume.docx
```

#### Analyze a Document

```bash
python main.py analyze --type resume --file path/to/resume.docx
```

```bash
python main.py analyze --type job --file path/to/job_description.docx
```
## Main Features

### Resume Customization
- Analyzes your existing resume to identify key skills and experiences
- Compares resume content to job requirements and identifies gaps
- Generates tailored content that highlights relevant experience
- Provides suggestions for improvements to match job requirements

### Cover Letter Generation
- Creates personalized cover letters based on your resume and a job description
- Highlights relevant skills and experience that match the job requirements
- Adapts to different company cultures and job roles
- Maintains a professional tone while showcasing your qualifications

### Document Analysis
- Extracts key information from resumes and job descriptions
- Identifies important skills, qualifications, and requirements
- Provides insights on how well your profile matches a job

## Project Structure

```
ai-resume-tools/
├── main.py                  # Main application file with CLI interface
├── gui.py                   # Graphical user interface application
├── .env                     # Environment variables (API keys)
├── .env.example             # Example environment file template
├── templates/               # Example templates for resumes and cover letters  
├── data/                    # For storing user data (resumes, job descriptions)
├── venv/                    # Virtual environment (not tracked in git)
├── .gitignore               # Git ignore file
└── README.md                # This documentation file
```

## Tips for Best Results
1. **Resume Format**: For best results, provide your resume in .docx format, which the application can properly parse.
2. **Detailed Job Descriptions**: The more detailed the job description, the better the AI can tailor your materials. You can either upload a job description file or paste the text directly into the application.
3. **Review Generated Content**: Always review and edit AI-generated content before using it in actual job applications.
4. **API Usage**: Be aware that using the OpenAI API will incur charges based on your usage.
5. **Save Your API Key**: Never commit your `.env` file with your actual API key to version control. The `.gitignore` file is set up to prevent this.
## License

MIT License

## Acknowledgements

This project uses:
- OpenAI's GPT models for natural language processing
- LangChain framework for building LLM applications

