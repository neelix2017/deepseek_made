import os
import wave
import json
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer

#Install the required libraries:
#
#pip install vosk sounddevice numpy
#
#Download a Vosk model:https://alphacephei.com/vosk/models
#
#Visit the Vosk models page and download a model (e.g., vosk-model-small-en-us-0.15 for English).
#
#Extract the model and place it in the same directory as the script or provide the path to the model in the script.

# Parameters
SAMPLE_RATE = 16000  # Sample rate for audio recording
RECORD_DURATION = 10  # Duration of recording in seconds
MODEL_PATH = "vosk-model-small-en-us-0.15"  # Path to the Vosk model

# Check if the model exists
if not os.path.exists(MODEL_PATH):
    print(f"Error: Vosk model not found at {MODEL_PATH}.")
    print("Please download a model from https://alphacephei.com/vosk/models and update the MODEL_PATH.")
    exit(1)

# Load the Vosk model
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE)

# Function to record audio from the microphone
def record_audio(duration, sample_rate):
    print("Recording... Speak now!")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording complete.")
    return audio.flatten()

# Record audio for 10 seconds
audio_data = record_audio(RECORD_DURATION, SAMPLE_RATE)

# Save the recorded audio to a WAV file (optional, for debugging)
output_wav = "recording.wav"
with wave.open(output_wav, "wb") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 2 bytes for int16
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio_data.tobytes())
print(f"Audio saved to {output_wav}")

# Process the audio with Vosk
recognizer.AcceptWaveform(audio_data.tobytes())
result = recognizer.FinalResult()

# Extract and print the recognized text
result_dict = json.loads(result)
recognized_text = result_dict.get("text", "No speech detected.")
print("\nRecognized Text:")
print(recognized_text)