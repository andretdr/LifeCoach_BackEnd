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

# https://www.youtube.com/watch?v=H7zAJf20Moc
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

app.add_middleware(
    CORSMiddleware,

    allow_origins=['*']
    #allow_origins=origins,
    # allow_credentials=True,
    # allow_methods=["*"],
    # allow_headers=["*"],
    # expose_headers=["Custom-Header"]
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

