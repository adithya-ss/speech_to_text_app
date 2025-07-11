## Vosk Speech-to-Text Application

This is a simple application to demonstrate the use of the Vosk toolkit for speech-to-text conversion.

### Getting Started

#### 1. Install Dependencies

Install the necessary Python packages using pip:

```bash
pip install -r requirements.txt
```

#### 2. Download a Vosk Model

You need to download a language model from the [Vosk Model Page](https://alphacephei.com/vosk/models).

For a quick start, download the small English model (`vosk-model-small-en-us-0.15`).

#### 3. Set up the Models

For this application to work, you must create a directory named `vosk_speech_models` in the root of your project. Then, download and extract the following models into it:

1.  **US English Model:** `vosk-model-en-us-0.22`
2.  **Indian English Model:** `vosk-model-en-in-0.4`

Your final directory structure must look like this:

```
.
├── vosk_speech_models/
│   ├── en-us-0.22/       (contents of the US model)
│   └── en-in-0.4/        (contents of the Indian English model)
├── speech_to_text.py
└── ...
```

#### 4. Run the Application

The application supports two modes: real-time transcription and file-based transcription.

##### Real-time Transcription

To transcribe audio from your microphone in real-time, run:

```bash
python speech_to_text.py --mode realtime
```

Speak into your microphone, and the transcribed text will appear in the console. Press `Ctrl+C` to stop.

##### Transcription from a File

To transcribe a WAV audio file, use the `--mode file` and `--input` arguments:

```bash
python speech_to_text.py --mode file --input your_audio_file.wav
```

##### Selecting a Language Model

Use the `--lang` flag to specify which language model to use.

**To use the US English model:**

```bash
python speech_to_text.py --mode realtime --lang en-us
```

**To use the Indian English model with a file:**

```bash
python speech_to_text.py --mode file --lang en-in --input your_audio_file.wav
```

Replace `your_audio_file.wav` with the path to your audio file. The file must be in WAV format (16-bit PCM, 16000Hz, Mono).
