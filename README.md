# 🎬 YouTube Video Summarizer API

🚀 **FastAPI-based API to fetch and summarize YouTube video transcripts using Hugging Face models.**

## 📌 Features
- Retrieves YouTube video transcripts
- Summarizes the transcript using Hugging Face's Mixtral-8x7B model
- Supports summaries in **French (`fr`)** and **English (`en`)**
- CORS enabled for easy integration with front-end applications

## 🛠️ Installation & Setup

### 1️⃣ Clone the repository
```sh
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### 2️⃣ Create a virtual environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3️⃣ Install dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Create a `.env` file
Add your **Hugging Face API token** to a `.env` file:
```ini
HUGGINGFACE_API_TOKEN=your_huggingface_api_key
```

## 🚀 Running the API
```sh
uvicorn main:app --reload
```

API will be available at: `http://127.0.0.1:8000`

## 🛠️ API Endpoints

### 🎯 `GET /summary/`
Fetches and summarizes the transcript of a YouTube video.

#### ✅ Request Parameters:
| Parameter | Type  | Default | Description |
|-----------|-------|---------|-------------|
| `video_id` | `str` | Required | YouTube video ID (from URL) |
| `lang` | `str` | `fr` | Summary language: `fr` (French) or `en` (English) |

#### 🔹 Example Request:
```sh
curl "http://127.0.0.1:8000/summary/?video_id=dQw4w9WgXcQ&lang=en"
```

#### 🔹 Example Response:
```json
{
  "summary": "This video explains how to..."
}
```

## 📜 License
This project is licensed under the **Apache License 2.0**.

## 🤝 Contributing
Feel free to submit issues or pull requests!

## 🌟 Credits
- **FastAPI** for the API framework
- **Hugging Face** for AI models
- **YouTubeTranscriptApi** for extracting video transcripts

---

🔥 _Happy coding! 🚀_
