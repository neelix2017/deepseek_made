#Install the required libraries:
#
#pip install vosk sounddevice numpy
#
#Download a Vosk model:https://alphacephei.com/vosk/models
#
#Visit the Vosk models page and download a model (e.g., vosk-model-small-en-us-0.15 for English).
#
#Extract the model and place it in the same directory as the script or provide the path to the model in the script.

import sys
import os
import queue
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import json

# Parameters
SAMPLE_RATE = 16000  # Sample rate for audio recording
CHUNK_SIZE = 4000    # Number of frames per buffer
MODEL_PATH = "vosk-model-small-en-us-0.15"  # Path to the Vosk model

# Check if the model exists
if not os.path.exists(MODEL_PATH):
    print(f"Error: Vosk model not found at {MODEL_PATH}.")
    print("Please download a model from https://alphacephei.com/vosk/models and update the MODEL_PATH.")
    exit(1)

# Load the Vosk model
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

# Queue to hold audio data
audio_queue = queue.Queue()

# Callback function to process audio chunks
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))

# Start recording from the microphone
print("Listening... Speak now! (Press Ctrl+C to stop)")
with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=CHUNK_SIZE,
    dtype="int16",
    channels=1,
    callback=audio_callback,
):
    try:
        while True:
            # Get audio data from the queue
            data = audio_queue.get()
            
            # Process the audio chunk with Vosk
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_dict = json.loads(result)
                recognized_text = result_dict.get("text", "")
                if recognized_text:
                    print("Recognized Text:", recognized_text)
            #else:
            #    partial_result = recognizer.PartialResult()
            #    partial_dict = json.loads(partial_result)
            #    partial_text = partial_dict.get("partial", "")
            #    if partial_text:
            #        print("Partial Result:", partial_text)
    except KeyboardInterrupt:
        print("\nStopped listening.")