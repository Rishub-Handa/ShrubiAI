'''
ShrubiAI is a bot for mom to make recipes with her dietary restrictions and get some basic wellness advice. 

Author: Rishub Handa 
Get started: uvicorn main:app   
'''

from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
import openai

load_dotenv()

OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
WHATSAPP_FROM_NUMBER = os.getenv('WHATSAPP_FROM_NUMBER')
WHATSAPP_TO_NUMBER = os.getenv('WHATSAPP_TO_NUMBER')
ENVIRONMENT = os.getenv('ENVIRONMENT')
MAX_TOKENS=1024
TEMPERATURE=0.7

app = FastAPI()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai.api_key = OPEN_AI_KEY

# Send message outside of response object 
def send_message(msg, to): 
    message = client.messages.create(
        body=msg,
        from_=WHATSAPP_FROM_NUMBER,
        to=to
    )
    print(message.status, message.body)

# Generate prompt for openai
def generate_prompt(name, input): 
    prompt = f'''
    This is a chat with Shrubi, an intellient, health conscious chef and fitness expert. He can create recipe ideas given a list of ingredients. He considers dietary restrictions and can exclude certain ingredients. He can also provide physical wellness advice for exercise and yoga. 

{name}: {input}
Shrubi:
    '''
    return prompt

def get_completion_response(prompt): 
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=TEMPERATURE, 
        max_tokens=MAX_TOKENS
    )
    return response


@app.post("/")
async def root(ProfileName: str = Form(...), Body: str = Form(...)):

    # Generate prompt
    prompt = generate_prompt(ProfileName, Body).strip()

    # Get response from openai 
    if ENVIRONMENT == "local": 
        response_body = "sample response"
    else: 
        ai_response = get_completion_response(prompt)
        response_body = ai_response['choices'][0]['text']

    # Create twilio response 
    response = MessagingResponse() 
    msg = response.message(response_body)
    return Response(content=str(response), media_type="application/xml")

@app.get("/")
async def hello_world(): 
    return {"message": "hello world!"}




