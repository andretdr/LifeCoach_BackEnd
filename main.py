# Following Travis Media's tutorial
# https://www.youtube.com/watch?v=4y1a4syMJHM
#
# uses fastAPI
# https://fastapi.tiangolo.com/
#
# uses POSTMAN for clientside tests
# https://web.postman.co/
#
# openAI
# https://openai.com/
#
# eleven labs text to voice
# https://elevenlabs.io/
#
# voice recorder for quick voice replies
# https://online-voice-recorder.com/#google_vignette
# 
# 1.) Send it audio, have it transcribed
# 2.) send it to chatgpt to get a response
# 3.) save chat history to send back and forth for context
#
# Deploying
# https://testdriven.io/blog/fastapi-react/
#
# uvicorn main:app --reload
# https://stackoverflow.com/questions/59391560/how-to-run-uvicorn-in-heroku



from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse, Response, JSONResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

import openai
import os, io
import json
import requests

# import uvicorn

# if __name__ == "__main__":
#     uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)

app = FastAPI()

# setup CORS handler
origins = [
    "http://localhost:5173",
    "localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Custom-Header"]
)

# FOR DEV TESTING
LIVE = True
elevenLabs = True

# setup env vars
load_dotenv()

# grabbing env variables
openai.api_key = os.getenv('OPEN_AI_KEY')
openai.organization = os.getenv('OPEN_AI_ORG')
elevenlabs_key = os.getenv('ELEVENLABS_KEY')
voice_id = os.getenv('VOICE_ID')

# app
@app.get('/')
async def root():
    return jsonable_encoder({'message': 'Created by Andre Tong'})


@app.post('/talk')
    # this is a FAST API UPLOAD FILE HANDLER, uploadFile, file: UploadFile
    # https://fastapi.tiangolo.com/tutorial/request-files/?h=upload#define-file-parameters
async def post_audio(file: UploadFile = File(...), history: str = Form(...)):

    history_chat = json.loads(history)
    # print(f'initial history : {history_chat}')
    
    # gets the audio file from client, sends it to openAI to transcribe
    user_message = {"role": "user", "content": await transcribe_audio(file)}
    # sends that transscribed msg to openAI, gets their reply and handles file history of chat
    updated_chat = get_chat_response(user_message, history_chat)
    # print(f'updated_chat : {updated_chat}')
    # update historyData with new responses

    return JSONResponse(updated_chat)


# gets text to speech from elevenLabs, then returns the audio blob
@app.post('/reply')
async def post_audio(history: str = Form(...)):

    history_chat = json.loads(history)
    latest_response = history_chat[len(history_chat)-1]['content']

    # print(f'latest_response : {latest_response}')
    # text to speech openAI's reply
    audio_output = text_to_speech(latest_response)

    return Response(content=audio_output, media_type="audio/mpeg")


# Functions

# transcribes audio using openAI
async def transcribe_audio(file):
    # this is a FAST API UPLOAD FILE HANDLER, uploadFile, format file.filename
    # https://fastapi.tiangolo.com/tutorial/request-files/?h=upload#define-file-parameters
    
    # openAI docs, transcriptions

    if LIVE:
        audio_data = await file.read()
        buffer = io.BytesIO(audio_data)
        buffer.name = "file.mp3"
        transcription = openai.audio.transcriptions.create(
            model = "whisper-1", 
            #file = audio_file,
            file = buffer,
            language = "en"
        )
        return transcription.text
    else:
        return 'not live, Hi, how are you?'



# load history, get openAI response, save history 
def get_chat_response(user_message, history_message):

    messages = initialise_messages(history_message)
    messages.append(user_message)

    # Send to OpenAI, get response
    if LIVE:
        gpt_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = messages
            )

        parsed_response = to_dict(gpt_response.choices[0].message)

    else:
        parsed_response = {"role": "assistant",
        "content": "greg's transcribed response"}

    # Save messages in database.json
    messages.append(parsed_response)
    
    return messages


# INITIALISE MESSAGES FROM CLIENT SIDE HISTORY
def initialise_messages(history_message):

    messages = []
    # context for chatBot
#    context = "You are interviewing the user for a front-end React developer position. Ask short questions that are relevant for a junior position. Your name is Greg. The user is Andre. Keep responses under 30 words and be funny sometimes."
#    context = 'Ask generic questions about life and well-being. Keep questions and responses short, under 15 words if possible'
    context = []
    context.append("Your name is Dave. You are a life coach giving advice on how to get to the next step in the user's personal or professional life. Ask short questions to find out more about the user's goals and give suggestions on how he can improve his current position. Keep your response under 20 words if possible, and be funny sometimes. Do not say #lifecoach")
    context.append("Your name is Dave. You are a career coach giving advice on how to get to the next step in the user's career. Ask short questions to find out more about the user's career situation and offer advice on how he can improve his current position. Keep your response under 20 words if possible, and be funny sometimes")

    empty = (len(history_message) == 0)

    # if file not empty just return it
    if not empty:
        return history_message
    # if file is empty we need to add the context, 'system role'    
    else:
        messages.append(
            {"role": "system", "content": context[0]},
        )
        return [{"role": "system", "content": context[0]}]


# API post to elevenlabs, gets back audio content
def text_to_speech(text):

    

    body = {
        "text": text,
       # "text": "Hi my name is Dave, how can I help you with your personal or professional goals?",
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0,
            "style": 0.5,
            "use_speaker_boost": True
            }
        }

    headers = {
        'Content-Type': 'application/json',
        'accept': 'audio/mpeg',
        'xi-api-key': elevenlabs_key
    }

    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'

    if LIVE and elevenLabs:
        try:
            response = requests.post(url, json=body, headers=headers)
            # if all good, return content
            if response.status_code == 200:
                return response.content
            else:
                print('Something went wrong')
        except Exception as e:
            print(e)
    else:
        with open('./testAudio/test-audio.mp3', mode='rb') as audio_file:
            audio_output = audio_file.read()
        return audio_output
    

# to dict chatcompletionmessage as it was not a dict
def to_dict(self):
    return {
        'role': self.role,
        'content': self.content
        # 'function_call': self.function_call,
        # 'tool_calls': self.tool_calls
    }









