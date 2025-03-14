from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
import requests
import os
from dotenv import load_dotenv
from transformers import AutoTokenizer
from huggingface_hub import login

load_dotenv()

# Récupération du token Hugging Face depuis les variables d'environnement
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    raise ValueError("HUGGINGFACE_API_TOKEN n'est pas défini dans les variables d'environnement.")

# Authentification explicite auprès de Hugging Face
login(token=HUGGINGFACE_API_TOKEN)

MAX_TOKEN_LIMIT = 32768  # Limite maximale de tokens imposée par Hugging Face

# Initialisation du tokenizer avec authentification
tokenizer = AutoTokenizer.from_pretrained(
    "mistralai/Mixtral-8x7B-Instruct-v0.1", use_auth_token=True
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fonction pour compter les tokens
def count_tokens(text):
    return len(tokenizer.encode(text, add_special_tokens=False))

# Fonction pour résumer avec Hugging Face
def summarize_with_huggingface(text, lang):
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    # On ajoute le paramètre library dans l'URL pour utiliser la bonne librairie
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1?library=transformers"

    prompt = (
        f"Résume la transcription de la vidéo Youtube suivante, en français :\n{text}\n\nresume-youtube-response :"
        if lang == "fr"
        else f"Summarize the transcription of the following YouTube video in English:\n{text}\n\nresume-youtube-response :"
    )

    # Vérification de la limite de tokens
    token_count = count_tokens(prompt)
    if token_count > MAX_TOKEN_LIMIT:
        raise HTTPException(
            status_code=422,
            detail=f"La transcription est trop longue ({token_count} tokens, limite: {MAX_TOKEN_LIMIT}). Veuillez choisir une vidéo plus courte."
        )

    payload = {
        "inputs": prompt,
        "parameters": {"max_length": 300, "temperature": 0.5},
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Déclenche une erreur pour tout statut HTTP >= 400

        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            full_output = result[0]["generated_text"].strip()
            marker = "resume-youtube-response :"
            summary = full_output.split(marker)[-1].strip() if marker in full_output else full_output
            return summary
        else:
            raise HTTPException(status_code=500, detail=f"Réponse inattendue de Hugging Face : {result}")

    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Erreur API Hugging Face : {e.response.text}")
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Erreur de communication avec Hugging Face : {str(e)}")

# Route pour générer le résumé
@app.get("/summary/")
def get_summary(video_id: str, lang: str = Query("fr", regex="^(fr|en)$")):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["fr", "en"])
        full_text = " ".join([entry["text"] for entry in transcript])
        return {"summary": summarize_with_huggingface(full_text, lang)}
    except TranscriptsDisabled:
        raise HTTPException(status_code=403, detail="Les transcriptions sont désactivées pour cette vidéo.")
    except NoTranscriptFound:
        raise HTTPException(status_code=404, detail="Aucune transcription trouvée pour cette vidéo.")
    except CouldNotRetrieveTranscript:
        raise HTTPException(status_code=502, detail="Impossible de récupérer la transcription.")
