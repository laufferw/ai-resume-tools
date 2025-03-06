# Job Descriptions Directory

Store job description files in this directory. The AI Resume Tools application uses these job descriptions to:

1. Analyze required skills and qualifications
2. Customize your resume to highlight relevant experience
3. Generate targeted cover letters that address specific job requirements

## Supported Formats

- Microsoft Word (.docx)
- Text files (.txt)
- PDF files (.pdf) - limited support, text extraction only
- HTML files (.html) - limited support

## Example Usage

When using the command line interface:
```
python main.py analyze --type job --file data/job_descriptions/job_posting.docx
```

When using the GUI, you can browse to select files from this directory.

## Privacy

Files in this directory are excluded from git by default to protect your privacy. Job descriptions often contain confidential information that shouldn't be publicly shared.

