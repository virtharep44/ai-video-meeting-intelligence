AI Video Meeting Intelligence
AI Video Meeting Intelligence is a full-stack AI pipeline that processes YouTube videos or local audio/video files and extracts everything meaningful from them automatically.

You paste a YouTube URL or drop a local file, hit Analyse, and within minutes you get:

A full transcript of the meeting

A professional bullet-point summary

Extracted action items with owners and deadlines

Key decisions made during the meeting

Open or unresolved questions

Speaker diarization

A ready-to-send follow-up email and we can also edit that email accordingly.

An interactive RAG chat to ask anything about the meeting

Built with a dark deep-space Streamlit UI, a modular Python backend, and a fully local CPU-friendly pipeline — no GPU required.

Features
Transcription

Local Whisper (CPU) for English

Sarvam AI saaras:v2.5 for Hinglish

Summarization

Map-Reduce pattern: chunks → individual summaries → combined final summary

Action Items

Extracts tasks, owners, and deadlines from transcript

Key Decisions

Lists all decisions made during the meeting

Open Questions

Flags unresolved topics needing follow-up

Speaker Diarization

Energy-based approach, lightweight, no ML model needed

Email Generator

AI-drafted professional follow-up email, editable and downloadable

RAG Chat

Ask any question about the meeting using ChromaDB + Mistral AI

YouTube Support

Paste any YouTube URL, audio downloads automatically via yt-dlp

Local File Support

Upload any .mp4, .mp3, .wav, .m4a file

PDF Export

Download results as a PDF report via fpdf2

Dark UI

Custom deep-space Streamlit theme with Syne + JetBrains Mono fonts

Architecture
text
Input (YouTube URL / Local File)
        │
        ▼
┌─────────────────────┐
│  utils/audio_       │  yt-dlp → download
│  processor.py       │  pydub  → convert to WAV (mono, 16kHz)
│                     │  pydub  → chunk into 10-min segments
└────────┬────────────┘
         │  chunks[] (WAV files)
         ▼
┌─────────────────────┐
│  core/transcriber   │  English  → Whisper (local, base model)
│  .py                │  Hinglish → Sarvam AI saaras:v2.5
│                     │             (25s slices, HTTP API)
└────────┬────────────┘
         │  full transcript (str)
         ▼
┌────────────────────────────────────────────────────────┐
│                   Parallel Processing                  │
│                                                        │
│  core/summarizer.py   → Map-Reduce summarization       │
│  core/summarizer.py   → generate_title()               │
│  core/extractor.py    → action items                   │
│  core/extractor.py    → key decisions                  │
│  core/extractor.py    → open questions                 │
│  core/email_generator → follow-up email                │
│  core/vector_store.py → ChromaDB + MiniLM embeddings   │
│  core/diarizer.py     → energy-based speaker segments  │
└────────┬───────────────────────────────────────────────┘
         │  result dict
         ▼
┌─────────────────────┐
│  app.py             │  Streamlit UI
│  (Streamlit)        │  Tabs · Cards · RAG Chat · Email Editor
└─────────────────────┘
Tech Stack
LLM
Library	Version	Role
mistralai	1.0.3	Core Mistral AI SDK
langchain-mistralai	0.1.13	LangChain integration
Model	mistral-small-latest	All generation tasks
Temperature	0.2 / 0.3	Controls output creativity
Speech to Text
Engine	Details	Used For
OpenAI Whisper	Local, CPU, base model, openai-whisper	English transcription
Sarvam AI	saaras:v2.5, speech-to-text-translate API, 25s chunk logic	Hinglish transcription fallback
Whisper model is configurable via WHISPER_MODEL env var. Default is base for speed on CPU.

RAG Pipeline
Component	Details
Vector Store	ChromaDB 0.5.3, persisted to vector_db/, collection: meeting_transcript
Embedding Model	all-MiniLM-L6-v2 via sentence-transformers==3.0.1, CPU
Retrieval	Similarity search, k=4 chunks per query
Chunk Size	500 tokens, overlap 50
LangChain Ecosystem
Package	Version	Role
langchain	0.2.16	Core framework
langchain-core	0.2.38	LCEL, prompts, parsers, runnables
langchain-community	0.2.16	Chroma, HuggingFaceEmbeddings
langchain-mistralai	0.1.13	ChatMistralAI
langchain-huggingface	0.0.3	HuggingFace embeddings
langchain-text-splitters	latest	RecursiveCharacterTextSplitter
tiktoken	0.7.0	Token counting
LangChain patterns used:

LCEL pipe syntax: prompt | llm | StrOutputParser()

Map-Reduce summarization across transcript chunks

Full RAG chain: retriever | format_docs → prompt → llm → parser

RunnablePassthrough, RunnableLambda for pipeline composition

Audio Processing
Library	Version	Role
yt-dlp	2024.5.27	YouTube audio download, bestaudio format, cookie auth
pydub	0.25.1	WAV conversion, mono 16kHz, 10-min chunking, 25s Sarvam slicing
ffmpeg-python	0.2.0	FFmpeg bindings, WAV extraction, 192kbps
torchaudio	2.3.1	Audio support for PyTorch
Audio pipeline steps:

YouTube URL → yt-dlp → best audio format → FFmpeg → .wav

Local file → pydub → mono, 16kHz .wav

WAV → pydub → 10-minute chunks

Each chunk → Whisper or Sarvam API, with 25s sub-slices for Sarvam

Speaker Diarization
Custom energy-based approach, no external ML model:

Audio → 10s segments → numpy RMS energy per segment

If |energy_diff| > 500 threshold → switch speaker

Output: SPEAKER_0 / SPEAKER_1 with timestamps

This approach was chosen over pyannote.audio and speechbrain due to Windows CPU constraints.

Translation
Library	Version	Role
deep-translator	1.11.4	Hindi → English, free, no API key
PyTorch (CPU)
Library	Version	Note
torch	2.3.1	Required by Whisper + sentence-transformers
torchaudio	2.3.1	Audio ops
torchvision	0.18.1	Required alongside torch
All inference runs on CPU. No CUDA required.

Export and UI
Library	Version	Role
streamlit	1.37.0	Full UI framework
fpdf2	2.7.9	PDF report export
python-dotenv	1.0.1	.env API key loading
requests	2.32.3	HTTP calls to Sarvam AI API
numpy	1.26.4	RMS energy calculation for diarization
Project Structure
text
ai-video-meeting-intelligence/
│
├── app.py                      # Streamlit UI — main entry point
├── main.py                     # CLI entry point (for testing pipeline)
├── requirements.txt            # All dependencies pinned
├── .env                        # API keys (not committed)
├── .env.example                # Template for env vars
├── www.youtube.com_cookies.txt # YouTube cookies for yt-dlp auth
│
├── core/
│   ├── transcriber.py          # Whisper + Sarvam AI STT routing
│   ├── summarizer.py           # Map-Reduce summarization + title generation
│   ├── extractor.py            # Action items, decisions, questions extraction
│   ├── rag_engine.py           # Full LCEL RAG pipeline + ask_question()
│   ├── vector_store.py         # ChromaDB + all-MiniLM-L6-v2 embeddings
│   ├── email_generator.py      # AI follow-up email generation
│   └── diarizer.py             # Energy-based speaker diarization
│
├── utils/
│   └── audio_processor.py      # YouTube download + WAV convert + chunking
│
└── vector_db/                  # ChromaDB persistence directory (auto-created)
Configuration
Create a .env file in the project root:

text
# Required
MISTRAL_API_KEY=your_mistral_api_key_here

# Optional — Sarvam AI (for Hinglish transcription)
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_STT_MODEL=saaras:v2.5

# Optional — Whisper model size (base/small/medium/large)
# Larger = more accurate but slower on CPU
WHISPER_MODEL=base
Get your Mistral API key at console.mistral.ai.
Get your Sarvam API key at dashboard.sarvam.ai.

Installation
Prerequisites
Python 3.10+

FFmpeg installed and in PATH

Windows / Linux / macOS (CPU only, no GPU needed)

Step 1 — Clone the repo
bash
git clone https://github.com/your-username/ai-video-meeting-intelligence.git
cd ai-video-meeting-intelligence
Step 2 — Create virtual environment
bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
Step 3 — Install dependencies
bash
pip install -r requirements.txt
If you only want CPU torch:

bash
pip install torch==2.3.1 torchaudio==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cpu
Step 4 — Set up environment variables
bash
cp .env.example .env
# Edit .env and add your API keys
Step 5 — Install FFmpeg
Windows: Download from ffmpeg.org and add to PATH

Linux: sudo apt install ffmpeg

Mac: brew install ffmpeg

Usage
Streamlit App (Recommended)
bash
streamlit run app.py
Then open http://localhost:8501 in your browser.

Steps:

Paste a YouTube URL or local file path in the sidebar

Select language: english or hinglish

Click ⚡ Analyse

Watch the live pipeline status in the sidebar

Explore results: Summary, Action Items, Decisions, Questions, Speakers

Edit and download the AI-generated follow-up email

Chat with your meeting using the RAG chatbot

CLI Mode (for testing)
bash
python main.py
Runs the full pipeline in terminal and drops into an interactive RAG chat loop.

Pipeline Flow
Input Detection

https:// URL → yt-dlp download → WAV

Local path → pydub convert → WAV (mono, 16kHz)

Audio Chunking

pydub → 10-minute WAV chunks

Transcription (per chunk)

English → Whisper base (local, CPU)

Hinglish → Sarvam saaras:v2.5 (25s sub-slices via HTTP)

LLM Processing

generate_title() → 8-word meeting title

summarize() → Map-Reduce bullet summary

extract_action_items() → numbered task list

extract_key_decisions() → numbered decisions

extract_questions() → open questions

generate_email() → professional follow-up email

RAG Pipeline

RecursiveCharacterTextSplitter (chunk=500, overlap=50)

all-MiniLM-L6-v2 embeddings (CPU)

ChromaDB vector store (persisted)

Similarity retrieval k=4 → Mistral → answer

Speaker Diarization

pydub 10s segments → numpy RMS energy → SPEAKER_0 / SPEAKER_1

Key Design Decisions
Why Whisper over Sarvam for English?
Whisper runs fully locally — no API quota, no latency, no cost.

Why keep Sarvam for Hinglish?
Sarvam integration is useful where translation capability matters.

Why energy-based diarization?
pyannote.audio and speechbrain require heavier setup or GPU support. The custom numpy + pydub approach works on CPU with minimal dependencies.

Why Map-Reduce summarization?
Meetings can be long. A single LLM call on a long transcript may exceed context limits, so chunked summarization is more reliable.

Why ChromaDB over FAISS?
ChromaDB persists automatically to disk, so the vector store survives between sessions without manual save/load logic.

Dependencies Summary
text
openai-whisper
yt-dlp==2024.5.27
ffmpeg-python==0.2.0
pydub==0.25.1
deep-translator==1.11.4
langchain==0.2.16
langchain-core==0.2.38
langchain-community==0.2.16
langchain-mistralai==0.1.13
langchain-huggingface==0.0.3
mistralai==1.0.3
chromadb==0.5.3
sentence-transformers==3.0.1
streamlit==1.37.0
fpdf2==2.7.9
python-dotenv==1.0.1
requests==2.32.3
torch==2.3.1
torchvision==0.18.1
torchaudio==2.3.1
numpy==1.26.4
tiktoken==0.7.0
Known Limitations
Sarvam routing: Both English and Hinglish currently route to Whisper

Speaker diarization: Detects max 2 speakers and may misclassify noisy audio

Whisper on CPU: base model is faster but less accurate than small or medium

YouTube cookies: Some videos require authentication via www.youtube.com_cookies.txt

Author
Built by Pragya
