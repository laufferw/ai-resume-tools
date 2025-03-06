# Resumes Directory

Place your resume files in this directory. The AI Resume Tools application can read and analyze these resumes to:

1. Customize them for specific job applications
2. Generate tailored cover letters
3. Provide analysis and improvement suggestions

## Supported Formats

- Microsoft Word (.docx)
- Text files (.txt)
- PDF files (.pdf) - limited support, text extraction only

## Example Usage

When using the command line interface:
```
python main.py customize-resume --resume data/resumes/my_resume.docx --job data/job_descriptions/job_posting.docx
```

When using the GUI, you can browse to select files from this directory.

## Privacy

Files in this directory are excluded from git by default to protect your privacy. Your personal resume information won't be uploaded to the repository when you commit changes.

