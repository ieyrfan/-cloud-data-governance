import json
import csv
import io

def extract_text_from_file(file_content_bytes: bytes, filename: str) -> str:
    """
    Intelligently extracts text from different file formats (TXT, CSV, JSON, PDF).
    """
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    try:
        if ext == 'json':
            # Parse and re-serialize to normalize it for text analysis
            data = json.loads(file_content_bytes.decode('utf-8', errors='ignore'))
            return json.dumps(data, indent=2)
            
        elif ext == 'csv':
            decoded = file_content_bytes.decode('utf-8', errors='ignore')
            csv_reader = csv.reader(io.StringIO(decoded))
            text_lines = []
            for row in csv_reader:
                text_lines.append(" ".join(row))
            return "\n".join(text_lines)
            
        elif ext == 'pdf':
            # Requires PyPDF2 in the Lambda environment
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content_bytes))
                text = ""
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                return text
            except ImportError:
                print("WARNING: PyPDF2 not installed. Cannot parse PDF correctly.")
                return ""
                
        else:
            # Default fallback for .txt, .md, .log, etc.
            return file_content_bytes.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"Error parsing file {filename}: {e}")
        # Return whatever we can extract safely
        return str(file_content_bytes)[:1000]
