# System libraries
import sys
import os

# OpenAI model text-davinci-003
import openai

# Libraries for voice recognition and text-to-speech synthesis
import speech_recognition as sr
from gtts import gTTS

# Libraries for playing audio
from pygame import mixer

# Libraries for getting audio duration
import time
import wave
import contextlib
from pydub import AudioSegment

# Libraries and API for voice transcription
from deepgram import Deepgram
import asyncio
import aiohttp
import pyaudio
import keyboard
import json

# API keys
openai.api_key = 'INSERT_API_KEY'
DEEPGRAM_API_KEY = 'INSERT_API_KEY'

# Variables
conversation_history = []
top_p = 0.9
temperature = 0
audioNumber = 0
PATH_TO_FILE = 'audio.wav'

# Function that uses Deepgram to transcribe audio to text
def deepgramTranscript():
    deepgram = Deepgram(DEEPGRAM_API_KEY)
    with open(PATH_TO_FILE, 'rb') as audio:
        source = {'buffer': audio, 'mimetype': 'audio/wav'}
        response = deepgram.transcription.sync_prerecorded(source, {'punctuate': True})
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript

# Function that makes a request to the OpenAI API with the given prompt and returns the response
def ask_ai(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        top_p=top_p,
        max_tokens=150,
        n=1,
    )
    return response.choices[0].text.strip()

# Function that converts text to an audio file
def text_to_speech(text, language, filename):
    speech = gTTS(text=text, lang=language, slow=False)
    speech.save(filename)

# Function that records audio from the microphone and saves it to a file
def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = PATH_TO_FILE

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    print("Press the spacebar to start recording.")
    while True:
        if keyboard.is_pressed(' '):
            print("Recording...")
            break

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        if keyboard.is_pressed('c'):
            print("Recording finished.")
            break

    print("Saving audio...")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# Main function that manages the interaction flow
if __name__ == "__main__":
    mixer.init()  # Initialize the audio player

    while True:
        # Record user's audio
        record_audio()
        
        # Transcribe the recorded audio
        prompt = deepgramTranscript().lower()
        print('User: ' + prompt)

        # End the conversation if "goodbye" or "bye" is detected
        if prompt in ["goodbye", "bye"]:
            print("Goodbye detected, ending conversation.")
            break

        # Send the transcribed text to the OpenAI API
        conversation_history.append(prompt)
        full_prompt = " ".join(conversation_history)
        response = ask_ai(full_prompt)
        conversation_history.append(response)

        # Convert OpenAI's response to speech
        audio_filename = f"Speech{audioNumber}.mp3"
        text_to_speech(response, "en", audio_filename)

        # Play the response audio
        mixer.music.load(audio_filename)
        mixer.music.play()
        time.sleep(2)  # Brief pause before playback
        
        while mixer.music.get_busy():  # Wait for audio to finish
            time.sleep(0.1)

        audioNumber += 1  # Increment the counter for the next audio file

        print("Assistant:", response)
        print("-----------------------------------------------")
