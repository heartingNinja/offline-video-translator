# Video Subtitle Translator

A Python GUI application that extracts audio from video files, transcribes and optionally translates the audio using OpenAI's Whisper and GPT models, and generates subtitle files (SRT).

## Features

- Extract audio from video files (supports MP4, MKV, AVI, MOV).
- Transcribe audio to text using Whisper models (`tiny`, `base`, `small`, `medium`, `large`).
- Translate subtitles to selected target languages via Whisper built-in translation or OpenAI GPT translation.
- Save subtitles as SRT files.
- Simple Tkinter-based GUI for easy interaction.

## Supported Languages

- **Whisper transcription languages:** English, Spanish, French, German, Japanese, Chinese, Arabic, Bengali, Catalan, Czech, Danish, Dutch, Greek, Hindi, Hungarian, Italian, Korean, Malay, Norwegian, Polish, Portuguese, Romanian, Russian, Turkish, Ukrainian, Vietnamese.
- **Translation target languages:** English, Spanish, French, German, Italian, Portuguese.

## Requirements

- Python 3.8+
- [openai](https://pypi.org/project/openai/)
- [whisper](https://pypi.org/project/openai-whisper/)
- [pysrt](https://pypi.org/project/pysrt/)
- [moviepy](https://pypi.org/project/moviepy/)
- tkinter (usually included with Python)

Install dependencies with:

```bash
pip install openai whisper pysrt moviepy



