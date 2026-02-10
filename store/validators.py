# validators.py
from django.core.exceptions import ValidationError

def validate_document_file(value):
    allowed_extensions = ['.pdf', '.docx']
    if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError("Only PDF and DOCX files are allowed.")
    