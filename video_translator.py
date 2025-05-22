import os
import openai
import whisper
import pysrt
import tkinter as tk
from tkinter import filedialog, messagebox
import tempfile
from moviepy.editor import VideoFileClip

# Set OpenAI API Key
openai.api_key = ""

# Supported Whisper languages
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Japanese": "ja",
    "Chinese": "zh",
    "Arabic": "ar",
    "Bengali": "bn",
    "Catalan": "ca",
    "Czech": "cs",
    "Danish": "da",
    "Dutch": "nl",
    "Greek": "el",
    "Hindi": "hi",
    "Hungarian": "hu",
    "Italian": "it",
    "Korean": "ko",
    "Malay": "ms",
    "Norwegian": "no",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Turkish": "tr",
    "Ukrainian": "uk",
    "Vietnamese": "vi"
}

# Supported target languages for translation (e.g., into English, Spanish, etc.)
TRANSLATE_LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt"
}

# Whisper model sizes
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]

# Translation method choices
TRANSLATION_METHODS = ["Whisper Translation", "OpenAI Translation"]

def extract_audio(video_path):
    """Extracts audio from video to a temporary file."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
            audio_path = temp_audio_file.name
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, codec='mp3')
            video.close()  # Make sure the video file is closed after extraction
            return audio_path
    except Exception as e:
        messagebox.showerror("Error", f"Error extracting audio: {str(e)}")
        return None
        
def transcribe_audio(audio_path, lang, model_size):
    """Transcribes audio using Whisper."""
    try:
        model = whisper.load_model(model_size)  # Use "small", "medium", or "large"
        result = model.transcribe(audio_path, language=lang)
        return result["segments"]
    except Exception as e:
        messagebox.showerror("Error", f"Error transcribing audio: {str(e)}")
        return []

def translate_text(text, target_lang):
    """Translates text to a target language using OpenAI."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": f"Your task is to translate the following text to {target_lang}. If the text is already in {target_lang}, leave it unchanged. If the text contains non-standard words or phrases (such as slang, typos, or unclear terms), leave them as they are without attempting to interpret or alter their meaning."},
                      {"role": "user", "content": text}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        messagebox.showerror("Error", f"Error during translation: {str(e)}")
        return text

def whisper_translate(audio_path, target_lang, model_size, whisper_srt):
    """Uses Whisper's built-in translation feature and saves the translated text as an SRT file."""
    try:
        # Print the target language to verify it's being passed correctly
        print(f"Target language for translation: {target_lang}")

        # Load the Whisper model
        model = whisper.load_model(model_size)
        
        # Transcribe and translate the audio in one step with Whisper
        result = model.transcribe(audio_path, task="translate", language=target_lang)
        
        # Save the Whisper translation directly as an SRT file
        subs = pysrt.SubRipFile()
        for i, segment in enumerate(result['segments']):
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            
            # Create a subtitle item
            sub = pysrt.SubRipItem(
                index=i + 1,
                start=pysrt.SubRipTime(seconds=int(start_time)),
                end=pysrt.SubRipTime(seconds=int(end_time)),
                text=text
            )
            subs.append(sub)
        
        # Save the SRT file
        subs.save(whisper_srt, encoding="utf-8")
        print(f"Whisper translation saved: {whisper_srt}")
        
        return result['text']  # Return the translated text (optional, if needed elsewhere)
    
    except Exception as e:
        messagebox.showerror("Error", f"Error during Whisper translation: {str(e)}")
        return None


def export_whisper_transcription(transcriptions, whisper_srt):
    """Saves the raw Whisper transcription as an SRT file before translation."""
    try:
        subs = pysrt.SubRipFile()
        for i, segment in enumerate(transcriptions):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]

            sub = pysrt.SubRipItem(
                index=i + 1,
                start=pysrt.SubRipTime(seconds=int(start_time)),
                end=pysrt.SubRipTime(seconds=int(end_time)),
                text=text
            )
            subs.append(sub)

        subs.save(whisper_srt, encoding="utf-8")
        print(f"Whisper transcription saved: {whisper_srt}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving Whisper transcription: {str(e)}")

def generate_srt(transcriptions, output_srt, target_lang, translation_method, model_size, audio_source):
    """Creates an SRT file from transcriptions."""
    try:
        subs = pysrt.SubRipFile()

        for i, segment in enumerate(transcriptions):
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]

         
            text = translate_text(text, target_lang)

            sub = pysrt.SubRipItem(
                index=i + 1,
                start=pysrt.SubRipTime(seconds=int(start_time)),
                end=pysrt.SubRipTime(seconds=int(end_time)),
                text=text
            )
            subs.append(sub)

        subs.save(output_srt, encoding="utf-8")
        messagebox.showinfo("Success", f"Subtitles saved: {output_srt}")
    except Exception as e:
        messagebox.showerror("Error", f"Error generating SRT: {str(e)}")


def process_video():
    """Handles GUI button click to process video."""
    video_path = file_path_var.get()
    lang = LANGUAGES[lang_var.get()]
    model_size = model_var.get()  # Get selected model size
    target_lang = TRANSLATE_LANGUAGES[translate_lang_var.get()]  # Get selected target translation language
    translation_method = translation_method_var.get()  # Get selected translation method

    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return

    output_srt = os.path.splitext(video_path)[0] + ".srt"
    whisper_srt = os.path.splitext(video_path)[0] + "_whisper.srt"

    try:
            # Extract audio to a temporary file
            audio_path = extract_audio(video_path)
            
            if audio_path:
                if translation_method == "Whisper Translation":
                    # Directly use Whisper's translation feature if chosen
                    whisper_translate(audio_path, target_lang, model_size, whisper_srt)
                    
                else:
                    # Process the audio and generate subtitles with another translation method
                    transcriptions = transcribe_audio(audio_path, lang, model_size)
                    if transcriptions:
                        export_whisper_transcription(transcriptions, whisper_srt)
                        generate_srt(transcriptions, output_srt, target_lang, translation_method, model_size, audio_path)
            
            # Clean up temporary audio
            os.remove(audio_path)  # Delete the temporary audio file
    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_file():
    """Opens file dialog to choose a video file."""
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov")])
    file_path_var.set(file_path)

# --- GUI SETUP ---
root = tk.Tk()
root.title("Video Translator")
root.geometry("500x500")

# File selection
file_path_var = tk.StringVar()
tk.Label(root, text="Select Video:").pack(pady=5)
tk.Entry(root, textvariable=file_path_var, width=50).pack()
tk.Button(root, text="Browse", command=select_file).pack(pady=5)

# Language selection
lang_var = tk.StringVar(value="English")
tk.Label(root, text="Select Language:").pack(pady=5)
tk.OptionMenu(root, lang_var, *LANGUAGES.keys()).pack()

# Target language selection (for translation)
translate_lang_var = tk.StringVar(value="English")
tk.Label(root, text="Select Translation Language:").pack(pady=5)
tk.OptionMenu(root, translate_lang_var, *TRANSLATE_LANGUAGES.keys()).pack()

# Add GUI option for model size selection
model_var = tk.StringVar(value="large")  # Default model size (e.g., "large")
tk.Label(root, text="Select Whisper Model Size:").pack(pady=5)
tk.OptionMenu(root, model_var, *WHISPER_MODELS).pack()

# Add translation method selection
translation_method_var = tk.StringVar(value="Whisper Translation")
tk.Label(root, text="Select Translation Method:").pack(pady=5)
tk.OptionMenu(root, translation_method_var, *TRANSLATION_METHODS).pack()

# Start button
tk.Button(root, text="Generate Subtitles", command=process_video, bg="green", fg="white").pack(pady=20)

root.mainloop()
