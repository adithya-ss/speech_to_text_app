import vosk
import sounddevice as sd
import json
import os
import queue
import argparse
import wave
import sys

# --- Settings ---
SAMPLE_RATE = 16000
CHANNELS = 1

# --- Real-time Transcription ---
q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    # Only print status if it's not just input overflow
    if status and str(status) != 'Input overflow!':
        print(status, flush=True)
    # To suppress all status messages, comment out the above line.
    q.put(bytes(indata))

def select_preferred_input_device():
    """Automatically select a preferred input device (mic/headset), or fallback to default."""
    devices = sd.query_devices()
    # Try to find a device with 'mic' or 'headset' in the name
    for idx, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            name = dev['name'].lower()
            if 'mic' in name or 'headset' in name:
                print(f"Auto-selected input device: {dev['name']} (index {idx})")
                return idx
    # Fallback to system default input device
    default = sd.default.device[0]
    if default is not None and default >= 0:
        print(f"Using default input device: {devices[default]['name']} (index {default})")
        return default
    # No suitable input device found
    print("No suitable input device found!")
    return None

def realtime_transcribe(model):
    """Transcribes audio in real-time from the microphone."""
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    device_index = select_preferred_input_device()
    if device_index is None:
        print("ERROR: No audio input device available.")
        return
    last_text = ""
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', callback=callback, blocksize=8000, device=device_index):
            print("Starting real-time transcription. Press Ctrl+C to stop.")
            while True:
                try:
                    data = q.get(timeout=1)
                except queue.Empty:
                    continue
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '')
                    if text and text != last_text:
                        print(text)
                        last_text = text
    except KeyboardInterrupt:
        print("\nStopping transcription.")
        final_result = json.loads(recognizer.FinalResult())
        print(f"Final Transcription: {final_result.get('text', '')}")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- File-based Transcription ---
def transcribe_from_file(model, audio_filename):
    """Transcribes an audio file using the Vosk model."""
    if not os.path.exists(audio_filename):
        print(f"Audio file '{audio_filename}' not found.")
        return

    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    with wave.open(audio_filename, "rb") as wf:
        if wf.getnchannels() != CHANNELS or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            return

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            recognizer.AcceptWaveform(data)

        result = json.loads(recognizer.FinalResult())
        print(f"Transcription: {result['text']}")

if __name__ == "__main__":
    print("[INFO] Starting Vosk Speech-to-Text Application...")
    # --- Model Configuration ---
    MODELS_BASE_DIR = "vosk_speech_models"
    MODEL_MAP = {
        "en-us": "en-us-0.22",
        "en-in": "en-in-0.4"
    }

    class HelpOnErrorParser(argparse.ArgumentParser):
        def error(self, message):
            self.print_help(sys.stderr)
            self.exit(2, f"\nError: {message}\n")

    parser = HelpOnErrorParser(description="Vosk Speech-to-Text Application")
    parser.add_argument("-m", "--mode", required=True, choices=['realtime', 'file'], help="Transcription mode: 'realtime' or 'file'")
    parser.add_argument("-l", "--lang", required=True, choices=MODEL_MAP.keys(), help="Specify the language model to use.")
    parser.add_argument("-i", "--input", help="Path to the audio file (required for 'file' mode)")

    args = parser.parse_args()

    # Construct the model path from the language choice
    model_folder = MODEL_MAP[args.lang]
    model_path = os.path.join(MODELS_BASE_DIR, model_folder)

    if not os.path.exists(model_path):
        print(f"Model path '{model_path}' not found. Please ensure the models are in the '{MODELS_BASE_DIR}' directory.")
        exit()

    print(f"[INFO] Loading model from: {model_path}")
    try:
        model = vosk.Model(model_path)
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        sys.exit(1)

    if args.mode == 'realtime':
        print("[INFO] Starting real-time transcription mode...")
        try:
            realtime_transcribe(model)
        except Exception as e:
            print(f"[ERROR] Real-time transcription failed: {e}")
    elif args.mode == 'file':
        if not args.input:
            parser.error("--input is required for 'file' mode.")
        print(f"[INFO] Transcribing from file: {args.input}")
        try:
            transcribe_from_file(model, args.input)
        except Exception as e:
            print(f"[ERROR] File transcription failed: {e}")

    print("[INFO] Application completed.")
