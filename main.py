from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def summarize_with_huggingface(text, lang):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"

    prompt = (
        f"Résume la transcription de la vidéo Youtube suivante, en français :\n{text}\n\nresume-youtube-response :"
        if lang == "fr"
        else f"Summarize the transcription of the following YouTube video in English:\n{text}\n\resume-youtube-response :"
    )

    payload = {
        "inputs": prompt,
        "parameters": {"max_length": 300, "temperature": 0.5},
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            full_output = result[0]["generated_text"].strip()

            marker = "resume-youtube-response :"

            if marker in full_output:
                summary = full_output.split(marker)[-1].strip()
            else:
                summary = full_output

            return summary
        else:
            return "Erreur de réponse inattendue : " + str(result)
    elif response.status_code == 503:
        return (
            "Le modèle Hugging Face est en train de démarrer. Réessaie dans un instant."
            if lang == "fr"
            else "The Hugging Face model is starting up. Please try again shortly."
        )
    else:
        return f"Erreur Hugging Face {response.status_code} : {response.text}"


@app.get("/summary/")
def get_summary(
    video_id: str, lang: str = Query("fr", regex="^(fr|en)$")
):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["fr", "en"])
        full_text = " ".join([entry["text"] for entry in transcript])
        summary = summarize_with_huggingface(full_text, lang)
        return {"summary": summary}

    except Exception as e:
        return {"error": str(e)}