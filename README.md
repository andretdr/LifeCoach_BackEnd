# Introduction
LifeCoach is a full-stack demo project created by me, developed to mimic conversations with a Life Coach. On the Backend, it is implemented on fastAPI and features a REST API, and runs on OpenAI's Chat Completions and Audio Transcriptions API. It utilises ElevenLabs for voicing.   
It is inspired by Travis Media's tutorial [here](https://youtu.be/4y1a4syMJHM)   

Front End implementation can be found [here](https://github.com/andretdr/LifeCoach_FrontEnd)

It is created by me, Andre Tong.
You can find the link to the app below.

[LifeCoach](https://lifecoach-frontend.vercel.app/)

# Development
The back-end is developed using fastAPI / Python.   
It is deployed on Heroku

# Full feature list
- Mantains the session history on the front-end as a design choice to allow for a REST API in the back end.
- The back-end has 3 routes.
- '/' route is mainly for testing and just returns a json message
- '/talk' route accepts Formdata of a audio file and a json array. The audio file is a recording of user's response and the array is the chat history so far.   
    If this is the first response, it will setup the context of the chat within the chat history.   
    It will firstly transcribe the audio file into a text reply using a call to openAI's transcription API, using the Whisper model.   
    Then it will append the text reply to the chat history and send that to openAI's chat completion API, using chatGPT 3.5 model, to recieve a reply.   
    Finally it will return just the updated chat history itself to the client.   
- '/reply' routes accepts Formdata of a json array. The array is the chat history so far.   
    It will send the latest reply from chatGPT 3.5 in the chat history to elevenLab's text to speech API.   
    Finally it will return this audio response.   

