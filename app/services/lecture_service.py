import os
import tempfile
from google import genai
from dotenv import load_dotenv

load_dotenv()

def upload_to_gemini(client, flask_file):
    """Safely saves a Flask FileStorage object to a temp file and uploads it to Gemini."""
    if not flask_file or not flask_file.filename:
        return None
    
    # Extract the file extension to keep format consistency
    ext = os.path.splitext(flask_file.filename)[1]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        flask_file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        # Pass the path string to the GenAI SDK
        uploaded_file = client.files.upload(file=temp_path)
        return uploaded_file
    finally:
        # Always remove the local file when done
        if os.path.exists(temp_path):
            os.remove(temp_path)

def generate_lecture_summary(pdf_file=None, user_notes=None, audio=None, youtube_url=None, api_key=None):
    target_key = api_key or os.getenv("GEMINI_API_KEY")
    if not target_key:
        raise ValueError("GEMINI_API_KEY is missing.")
    
    client = genai.Client(api_key=target_key)
    input_content = []

    # 1. Process Lecture PDF
    if pdf_file:
        uploaded_pdf = upload_to_gemini(client, pdf_file)
        if uploaded_pdf:
            input_content.append({"type": "document", "uri": uploaded_pdf.uri})

    # 2. Process User Notes
    if user_notes:
        uploaded_notes = upload_to_gemini(client, user_notes)
        if uploaded_notes:
            input_content.append({"type": "document", "uri": uploaded_notes.uri})

    # 3. Process Audio
    if audio:
        uploaded_audio = upload_to_gemini(client, audio)
        if uploaded_audio:
            input_content.append({"type": "document", "uri": uploaded_audio.uri})

    # 4. Process YouTube Link (passed purely as a context string instruction)
    if youtube_url:
        input_content.append({"type": "text", "text": f"Analyze this YouTube video link: {youtube_url}"})

    # 5. Fallback check & prompt assignment
    if not input_content:
        return "No valid files or links were submitted."

    input_content.append({"type": "text", "text": "Create a comprehensive, structured summary of the lecture using the provided assets."})

    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=input_content
    )
    
    return interaction.output_text