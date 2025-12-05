# Medical Voice Assistant - Demo

An AI-powered voice assistant that calls patients and performs symptom triage through natural conversation.

## Features

- Web interface to input phone numbers
- Automated outbound calling via Twilio
- AI-powered conversation with 4 medical triage questions
- Speech recognition for patient responses
- OpenAI GPT-4 powered summary and recommendations
- Natural text-to-speech voice responses

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Voice**: Twilio Voice API
- **AI**: OpenAI GPT-4
- **Frontend**: HTML, CSS, JavaScript

## Prerequisites

Before you begin, you'll need:

1. **Twilio Account**
   - Sign up at [https://www.twilio.com/](https://www.twilio.com/)
   - Get a phone number with voice capabilities
   - Note your Account SID and Auth Token

2. **OpenAI API Key**
   - Sign up at [https://platform.openai.com/](https://platform.openai.com/)
   - Create an API key

3. **Ngrok** (for local development)
   - Download from [https://ngrok.com/](https://ngrok.com/)
   - Used to expose your local server to Twilio webhooks

## Installation

### 1. Install Dependencies

```bash
cd medical-voice-assistant
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
OPENAI_API_KEY=your_openai_api_key_here
BASE_URL=http://localhost:8000
```

## Running the Application

### Step 1: Start the FastAPI Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### Step 2: Expose Local Server with Ngrok (Required for Twilio)

In a new terminal:

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

### Step 3: Update BASE_URL

Copy the ngrok HTTPS URL and update your `.env` file:

```env
BASE_URL=https://abc123.ngrok.io
```

Restart the FastAPI server for changes to take effect.

### Step 4: Access the Web Interface

Open your browser and go to:
```
http://localhost:8000
```

## Usage

1. Enter a phone number in E.164 format (e.g., `+1234567890`)
2. Click "Initiate Call"
3. Answer the incoming call on your phone
4. Respond to the 4 medical triage questions:
   - Describe your main symptoms
   - How long you've had the symptoms
   - Rate your pain/discomfort (1-10 scale)
   - Current medications
5. Receive an AI-generated summary and recommendation

## Project Structure

```
medical-voice-assistant/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Example environment file
├── README.md              # This file
├── templates/
│   └── index.html         # Web interface
└── static/
    └── style.css          # Styling
```

## API Endpoints

- `GET /` - Home page with phone input form
- `POST /initiate-call` - Triggers outbound call
- `POST /voice/start` - Twilio webhook for call start
- `POST /voice/process` - Twilio webhook for processing responses
- `GET /health` - Health check endpoint

## Medical Triage Questions

The system asks 4 questions:

1. **Main Symptoms**: What are you experiencing?
2. **Duration**: How long have you had these symptoms?
3. **Pain Scale**: Rate your discomfort (1-10)
4. **Medications**: Are you taking any medications?

After collecting responses, GPT-4 generates a brief summary and general recommendation.

## Important Notes

### Security & Compliance

- This is a **DEMO ONLY** - not for production medical use
- Does NOT comply with HIPAA regulations
- Not suitable for real patient data
- For production, implement:
  - Proper encryption (at rest and in transit)
  - HIPAA-compliant infrastructure
  - Secure patient data storage
  - Emergency detection and routing
  - Professional medical review

### Disclaimers

The system includes disclaimers that:
- This is not a medical diagnosis
- Always consult a healthcare professional
- In emergencies, call 911

### Cost Considerations

Running this demo incurs costs:
- **Twilio**: Per-minute voice call charges
- **OpenAI**: API usage charges for GPT-4
- Monitor usage to avoid unexpected charges

## Troubleshooting

### Call doesn't go through
- Verify Twilio credentials are correct
- Check phone number format (must include country code)
- Ensure ngrok is running and BASE_URL is updated
- Check Twilio console for error logs

### "No speech detected" error
- Speak clearly after the question
- Ensure quiet environment
- Check phone microphone

### OpenAI errors
- Verify API key is valid
- Check OpenAI account has credits
- Review OpenAI API status page

## Future Enhancements

- Add emergency keyword detection ("chest pain", "can't breathe")
- Implement call recording and transcription storage
- Add multi-language support
- Create admin dashboard for call logs
- Integrate with EHR systems
- Add patient authentication
- Implement HIPAA compliance measures

## License

This is a demo project for educational purposes.

## Support

For issues or questions, please check:
- Twilio documentation: [https://www.twilio.com/docs](https://www.twilio.com/docs)
- OpenAI documentation: [https://platform.openai.com/docs](https://platform.openai.com/docs)
- FastAPI documentation: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
