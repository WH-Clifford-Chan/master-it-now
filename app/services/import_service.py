from app.models import db
from app.models.sets import Card
from google import genai
from google.genai import types
import os
import json
import io
from dotenv import load_dotenv
from pypdf import PdfReader
from pydantic import BaseModel, Field
 

def get_form_cards(form_data, set_id):
    cards = []
    index = 1

    while True:
        term = (form_data.get(f"term_{index}") or "")
        definition = (form_data.get(f"definition_{index}") or "")
        example = (form_data.get(f"example_{index}") or "")
        notes = (form_data.get(f"notes_{index}") or "")

        # stop condition: no more rows at all
        if not term and not definition and not example and not notes:
            break

        # skip incomplete rows 
        if not term or not definition:
            index += 1
            continue

        cards.append(Card(
            term=term,
            definition=definition,
            example=example,
            notes=notes,
            score=0,
            set_id=set_id
        ))

        index += 1

    db.session.add_all(cards)
    db.session.commit()


# AI 
load_dotenv()

# Define structural output schemas using Pydantic
class Flashcard(BaseModel):
    term: str = Field(description="The key term, word, or concept")
    definition: str = Field(description="A clear and accurate definition of the term")
    example: str = Field(description="An example sentence or use case illustrating the term")
    notes: str = Field(description="Any additional helpful context, study tips, or related ideas")

class FlashcardList(BaseModel):
    cards: list[Flashcard]


def read_pdf(pdf_file, chunk_size=2):
    """
    Reads a PDF file safely using a byte stream, extracts text,
    and returns chunks of combined page text.
    """
    # Wrap Flask's FileStorage in a seekable BytesIO stream
    pdf_stream = io.BytesIO(pdf_file.read())
    reader = PdfReader(pdf_stream, strict=False)

    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append(text)

    chunks = []
    for i in range(0, len(pages), chunk_size):
        chunk = "\n\n".join(pages[i:i + chunk_size])
        chunks.append(chunk)

    return chunks

def get_ai_cards(chunks, api_key=None):
    target_key = api_key or os.getenv("GEMINI_API_KEY")
    if not target_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    client = genai.Client(api_key=target_key)
    all_cards = []

    # DEBUG STEP 1
    print(f"--- DEBUG: Total chunks received from PDF: {len(chunks)} ---")

    for index, chunk in enumerate(chunks):
        print(f"--- DEBUG: Sending chunk {index + 1}/{len(chunks)} to Gemini (Length: {len(chunk)} chars) ---")

        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=f"Extract terms:\n\nTEXT:\n{chunk}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=FlashcardList,
                    temperature=0.2
                ),
            )

            data = json.loads(response.text)
            chunk_cards = data.get("cards", [])

            # DEBUG STEP 2
            print(f"--- DEBUG: Chunk {index + 1} successfully generated {len(chunk_cards)} cards ---")

            all_cards.extend(chunk_cards)

        except Exception as e:
            print(f"!!! CRITICAL ERROR in chunk {index + 1}: {e} !!!")
            continue

    # DEBUG STEP 3
    print(f"--- DEBUG: Total cards accumulated: {len(all_cards)} ---")
    return all_cards

def generate_card(term, api_key=None):
    target_key = api_key or os.getenv("GEMINI_API_KEY")
    if not target_key:
        raise ValueError("GEMINI_API_KEY is missing.")

    client = genai.Client(api_key=target_key)
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite", 
            contents=f"Generate the definition, example and notes for: {term}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=FlashcardList,
                temperature=0.2 
            ),
        )
        data = json.loads(response.text)
        card = data.get("cards", [])

    except Exception as e:
        print(f"!!! CRITICAL ERROR: {e} !!!")
        return []

    return card



