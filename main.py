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
    allow_headers=["*"]
)

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
    print('got here')
    return jsonable_encoder({'message': 'Hello World'})


@app.post('/talk')
    # this is a FAST API UPLOAD FILE HANDLER, uploadFile, file: UploadFile
    # https://fastapi.tiangolo.com/tutorial/request-files/?h=upload#define-file-parameters
async def post_audio(file: UploadFile = File(...), history: str = Form(...)):


    historyData = json.loads(history)

# #   ONCE AFTER MID AUG, JUST UNCOMMENT THIS
#     print(historyData)
#     # gets a audio file from client, sends it to openAI to transcribe
#     user_message = {"role": "user", "content": await transcribe_audio(file)}
#     # sends that transscribed msg to openAI, gets their reply and handles file history of chat
#     chat_response = get_chat_response(user_message)
#     # text to speech openAI's reply
#     audio_output = text_to_speech(chat_response['content'])

    # this is for testing
    audio_output = open('./testAudio/test-audio.mp3', 'rb')

#https://www.npmjs.com/package/react-use-audio-player


#    FOR STREAMING UNCOMMENT ME
#    def iterfile():   
#        yield audio_output
#    return StreamingResponse(iterfile(), media_type="audio/mpeg")

#    FOR NONSTREAMING UNCOMMENT ME
#    return Response(content=audio_output, media_type="audio/mpeg")

    # this is for testing
    return FileResponse(path='./testAudio/test-audio.mp3', media_type="audio/mpeg")


# Functions

# transcribes audio using openAI
async def transcribe_audio(file):
    # this is a FAST API UPLOAD FILE HANDLER, uploadFile, format file.filename
    # https://fastapi.tiangolo.com/tutorial/request-files/?h=upload#define-file-parameters
    
    # openAI docs, transcriptions

    #audio_file = open(file, "rb")
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


# load history, get openAI response, save history 
def get_chat_response(user_message):
    messages = load_messages()
    messages.append(user_message)

    # print(messages)
    # print(type(messages))

    # Send to OpenAI, get response
    gpt_response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = messages
        )

    parsed_response = to_dict(gpt_response.choices[0].message)

    # Save messages in database.json
    save_messages(user_message, parsed_response)

    return parsed_response

# LOAD MESSAGES FROM DATABASE.JSON
# Chat Completions API
# https://platform.openai.com/docs/guides/text-generation/chat-completions-api
def load_messages():
    messages = []
    file = 'database.json'

    # context for chatBot
    context = "You are interviewing the user for a front-end React developer position. Ask short questions that are relevant for a junior position. Your name is Greg. The user is Andre. Keep responses under 30 words and be funny sometimes."

    # check if file is empty
    empty = os.stat(file).st_size == 0

    # if file not empty loop through and add to messages
    if not empty:
        with open(file) as db_file:
            data = json.load(db_file)    
            for item in data:
                messages.append(item)
    # if file is empty we need to add the context, 'system role'    
    else:
        messages.append(
            {"role": "system", "content": context},
        )
    return messages

# write to file
def save_messages(user_message, gpt_response):
    file = 'database.json'
    # load all history, append user msg and gpt reply
    messages = load_messages()
    messages.append(user_message)
    messages.append(gpt_response)
    # write and dump everything into file
    with open(file, 'w') as f:
        json.dump(messages, f)


# API post to elevenlabs, gets back audio content
def text_to_speech(text):

    body = {
        "text": text,
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

    try:
        response = requests.post(url, json=body, headers=headers)
        # if all good, return content
        if response.status_code == 200:
            return response.content
        else:
            print('Something went wrong')
    except Exception as e:
        print(e)
    

# to dict chatcompletionmessage as it was not a dict
def to_dict(self):
    return {
        'role': self.role,
        'content': self.content
        # 'function_call': self.function_call,
        # 'tool_calls': self.tool_calls
    }









