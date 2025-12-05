from fastapi import FastAPI, Request, Form, Response, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Optional
import sqlite3
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI(title="Medical Voice Assistant")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Twilio and Gemini configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# In-memory storage for conversation state (use Redis in production)
conversations = {}

# Voice and language settings
VOICE = "Polly.Aditi"  # Change this to try different voices
LANGUAGE = "hi-IN"

# Medical triage questions (in Hindi)
TRIAGE_QUESTIONS = [
    "नमस्ते, मैं मेडिकल असिस्टेंट हूं। कृपया अपना नाम बताएं?",
    "धन्यवाद। आपकी उम्र क्या है?",
    "आप कहां रहते हैं?",
    "कृपया अपनी मेडिकल समस्या या लक्षणों का वर्णन करें।"
]


# Database initialization
def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()

    # Create patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT UNIQUE,
            name TEXT,
            age TEXT,
            location TEXT,
            problem TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create conversation_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            question TEXT,
            answer TEXT,
            question_index INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES patients(conversation_id)
        )
    ''')

    conn.commit()
    conn.close()


def save_patient_info(conversation_id: str, name: str, age: str, location: str, problem: str):
    """Save or update patient information in database"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO patients (conversation_id, name, age, location, problem)
        VALUES (?, ?, ?, ?, ?)
    ''', (conversation_id, name, age, location, problem))

    conn.commit()
    conn.close()


def save_conversation_response(conversation_id: str, question: str, answer: str, question_index: int):
    """Save individual conversation response to database"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO conversation_history (conversation_id, question, answer, question_index)
        VALUES (?, ?, ?, ?)
    ''', (conversation_id, question, answer, question_index))

    conn.commit()
    conn.close()


# Initialize database on startup
init_database()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page with phone number input form"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/initiate-call")
async def initiate_call(phone_number: str = Form(...)):
    """Initiate an outbound call to the provided phone number"""
    try:
        # Initialize conversation state
        conversation_id = phone_number.replace("+", "").replace(" ", "")
        conversations[conversation_id] = {
            "question_index": 0,
            "responses": []
        }

        # Make the call using Twilio
        call = twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{BASE_URL}/voice/start?conversation_id={conversation_id}",
            method="POST"
        )

        return {
            "success": True,
            "message": f"Call initiated successfully to {phone_number}",
            "call_sid": call.sid
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error initiating call: {str(e)}"
        }


@app.post("/voice/start")
async def voice_start(request: Request, conversation_id: str = Query(...)):
    """Handle the initial voice interaction"""
    response = VoiceResponse()

    # Get the first question
    gather = Gather(
        input="speech",
        action=f"/voice/process?conversation_id={conversation_id}",
        method="POST",
        timeout=5,
        speech_timeout="auto",
        language=LANGUAGE
    )

    gather.say(TRIAGE_QUESTIONS[0], voice=VOICE, language=LANGUAGE)
    response.append(gather)

    # Fallback if no input
    response.say("क्षमा करें, मुझे आपका जवाब नहीं मिला। अलविदा।", voice=VOICE, language=LANGUAGE)

    return Response(content=str(response), media_type="application/xml")


@app.post("/voice/process")
async def voice_process(request: Request, conversation_id: str = Query(...)):
    """Process user speech and ask next question or end call"""
    form_data = await request.form()
    speech_result = form_data.get("SpeechResult", "")

    response = VoiceResponse()

    # Get conversation state
    if conversation_id not in conversations:
        response.say("क्षमा करें, एक त्रुटि हुई। अलविदा।", voice=VOICE, language=LANGUAGE)
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    conv = conversations[conversation_id]

    # Store the response in memory
    conv["responses"].append({
        "question": TRIAGE_QUESTIONS[conv["question_index"]],
        "answer": speech_result
    })

    # Save to database immediately after each answer
    save_conversation_response(
        conversation_id=conversation_id,
        question=TRIAGE_QUESTIONS[conv["question_index"]],
        answer=speech_result,
        question_index=conv["question_index"]
    )

    # Move to next question
    conv["question_index"] += 1

    # Check if there are more questions
    if conv["question_index"] < len(TRIAGE_QUESTIONS):
        gather = Gather(
            input="speech",
            action=f"/voice/process?conversation_id={conversation_id}",
            method="POST",
            timeout=5,
            speech_timeout="auto",
            language=LANGUAGE
        )
        gather.say(TRIAGE_QUESTIONS[conv["question_index"]], voice=VOICE, language=LANGUAGE)
        response.append(gather)
        response.say("क्षमा करें, मुझे आपका जवाब नहीं मिला। अलविदा।", voice=VOICE, language=LANGUAGE)
    else:
        # All questions answered - extract patient information
        name = conv["responses"][0]["answer"] if len(conv["responses"]) > 0 else "Unknown"
        age = conv["responses"][1]["answer"] if len(conv["responses"]) > 1 else "Unknown"
        location = conv["responses"][2]["answer"] if len(conv["responses"]) > 2 else "Unknown"
        problem = conv["responses"][3]["answer"] if len(conv["responses"]) > 3 else "Unknown"

        # Save complete patient information to database
        save_patient_info(
            conversation_id=conversation_id,
            name=name,
            age=age,
            location=location,
            problem=problem
        )

        # End message
        response.say(
            f"धन्यवाद {name}। हमने आपकी जानकारी दर्ज कर ली है। हमारा डॉक्टर जल्द ही आपसे संपर्क करेगा। अलविदा।",
            voice=VOICE,
            language=LANGUAGE
        )
        response.hangup()

        # Clean up conversation state
        del conversations[conversation_id]

    return Response(content=str(response), media_type="application/xml")


async def generate_ai_summary(responses: list) -> str:
    """Use Google Gemini to generate a brief summary and recommendation"""
    try:
        # Build context from Q&A
        context = "Patient responses:\n"
        for qa in responses:
            context += f"Q: {qa['question']}\nA: {qa['answer']}\n\n"

        # Call Gemini
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""You are a medical triage assistant. Based on the patient's responses, provide a brief 2-sentence summary and general recommendation. Always remind them this is not a diagnosis and to consult a healthcare professional. Keep it under 50 words.

{context}"""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Based on your symptoms, we recommend consulting with a healthcare professional soon."


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
