# ScratchLM

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
![Docker](https://img.shields.io/badge/container-Docker-2496ED?style=flat&logo=docker&logoColor=white)
[![License: AGPL](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0-blue.svg)

<div align="center">
  <br/>
  <a href="https://huggingface.co/spaces/mingnatthakitt/ScratchLM">
    <img src="https://huggingface.co/datasets/huggingface/badges/resolve/main/open-in-hf-spaces-xl-dark.svg" alt="Try our demo in Hugging Face Spaces" width="300px">
  </a>
  <br/>
  <br/>
</div>

**Zero-DB AI Study Assistant** — Choose your model, upload PDFs, and get AI-powered cheatsheets and interactive tutoring.

<p align="center">
  <img src="screenshot.png" width="70%" />
</p>

## ✨ Key Features

### 🤖 Dual Model Support
- **`gemma-4-31b-it`** via Google AI Studio — fast, text-based
- **`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`** via NVIDIA NIM — multimodal, PDF rendered as images
- Automatic fallback: if Nemotron fails, gracefully switches to Gemma

### 📄 PDF Processing
- **Drag & Drop Upload**: Upload PDFs directly in your browser
- **Gemma path**: PDF → pypdf text extraction → text sent to model
- **Nemotron path**: PDF → PyMuPDF renders each page as PNG image → sent to model as image content blocks
- **Multi-Page Support**: All pages rendered and sent for full document understanding

### 📚 AI-Powered Cheatsheet Generator
- **4-Zone Structure**: Automatically generates comprehensive study guides:
  - **Zone A**: Concept Deep-Dive
  - **Zone B**: Real-World Analogies
  - **Zone C**: Worked Problems
  - **Zone D**: Exam Traps & Strategy
- **Markdown Export**: Download cheatsheets as `.md` files for Obsidian, Notion, or any app

### 💬 AI Chat with Full Context
- **Document-Aware**: Chat remembers everything from your uploaded PDFs
- **Conversation History**: Multi-turn dialogues with context retention
- **Step-by-Step Teaching**: AI tutor explains concepts rather than just answering

### 🔒 Privacy First
- **Zero Database**: No user data stored anywhere
- **Session Isolation**: Each browser tab is isolated
- **One-Click Wipe**: Refresh the page to clear all data

---

## 🎓 AI Architecture

### Model Selection
The app ships with two model options, selectable via the UI:

| Model | Provider | Document Processing |
|-------|----------|-------------------|
| `gemma-4-31b-it` | Google AI Studio | PDF → pypdf text extraction → text |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | NVIDIA NIM | PDF → PNG images (150 DPI) → multimodal |

### Retry & Fallback
Nemotron calls retry up to 2 times with a 2-second delay on failure. If all retries fail, the request automatically falls back to Gemma — no data loss.

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| Web Framework | FastAPI |
| Frontend | Vanilla HTML/CSS/JS |
| AI Models | Gemma 4 31B IT (Google AI Studio) + Nemotron 3 Nano (NVIDIA NIM) |
| SDK | OpenAI Python SDK (both endpoints are OpenAI-compatible) |
| PDF Text Extraction | pypdf |
| PDF Image Rendering | PyMuPDF (fitz) |
| Markdown Rendering | marked.js |

---

## 🚀 Getting Started

### Prerequisites
- A Google AI Studio API key (`GEMINI_API_KEY`) — free tier available
- A NVIDIA NIM API key (`NVIDIA_API_KEY`) — available at [build.nvidia.com](https://build.nvidia.com)
- Python 3.12+ or Docker

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mingnatthakitt/ScratchLM.git
   cd ScratchLM
   ```

2. **Set up environment variables**:
   ```bash
   export GEMINI_API_KEY="your_google_api_key_here"
   export NVIDIA_API_KEY="your_nvidia_api_key_here"
   ```

3. **Run with Docker**:
   ```bash
   docker build -t scratchlm .
   docker run -p 7860:7860 \
     -e GEMINI_API_KEY=$GEMINI_API_KEY \
     -e NVIDIA_API_KEY=$NVIDIA_API_KEY \
     scratchlm
   ```

   Or run without Docker:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```

4. **Open in browser**:
   Navigate to `http://localhost:7860`

### Hugging Face Spaces

1. **Fork the Space**: Clone it to your account
2. **Add Secrets**: Go to Space Settings → Repository secrets → Add `GEMINI_API_KEY` and `NVIDIA_API_KEY`
3. **Done**: The Space will automatically build and run

---

## 📖 How to Use

### Step 1: Select a Model
Use the dropdown in the sidebar to choose:
- **Gemma 4** — text-based extraction, good for fast responses
- **Nemotron 3** — renders PDF pages as images for full document understanding

### Step 2: Upload PDF
Drag and drop a PDF onto the upload area, or click to browse.

### Step 3: Extract
Click **⚡ Extract** to process the document. For Gemma, text is extracted. For Nemotron, pages are rendered as images.

### Step 4: Generate Cheatsheet or Chat
- **✨ Generate**: Create a 4-zone study guide from your PDF
- **💬 Chat**: Ask questions about your PDF with full context awareness
- **📥 Download .md**: Save the cheatsheet as a Markdown file

---

## ⚖️ License

**GNU Affero General Public License v3.0 (AGPL-3.0)**

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/agpl-3.0.en.html>.

---

## 🙏 Acknowledgments

- **Google AI** for Gemma models via AI Studio
- **NVIDIA** for Nemotron models via NIM
- **Hugging Face** for Spaces infrastructure
- **FastAPI** for the excellent web framework
