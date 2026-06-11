"""
ScratchLM - Zero-DB AI Study Application
FastAPI + Pure HTML/JS frontend with dark theme
"""

import os
import io
import requests
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from pypdf import PdfReader

# ============================================================================
# Configuration
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-31b-it:generateContent"

# ============================================================================
# Core Functions
# ============================================================================

def generate_content(prompt: str, context: str = "") -> str:
    """Generate content using Gemma via Google AI Studio API."""
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY not configured."
    
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    full_text = f"{prompt}\n\n=== SOURCE MATERIAL ===\n{context}" if context else prompt
    
    payload = {
        "contents": [{"parts": [{"text": full_text}]}],
        "generationConfig": {"temperature": 1.0, "topP": 0.95, "topK": 64}
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        
        if "candidates" in data:
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts)
        return str(data)
    except requests.exceptions.Timeout:
        return "Error: Request timed out."
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"


def parse_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception as e:
        return f"[PDF error: {e}]"


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(title="ScratchLM")


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScratchLM</title>
    
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: system-ui, -apple-system, sans-serif; 
            background: #0d1117; 
            color: #c9d1d9; 
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { 
            background: linear-gradient(135deg, #1a1f35 0%, #2d1b4e 100%); 
            color: #ffffff; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
            margin-bottom: 20px;
            border: 1px solid #30363d;
        }
        header h1 { font-size: 2rem; color: #ffffff; }
        header p { opacity: 0.8; margin-top: 5px; color: #c9d1d9; }
        .main-grid { display: grid; grid-template-columns: 350px 1fr; gap: 20px; }
        .panel { 
            background: #161b22; 
            border-radius: 10px; 
            padding: 20px; 
            border: 1px solid #30363d;
        }
        .panel-title { font-weight: 600; margin-bottom: 15px; color: #f0f6fc; }
        .upload-area { 
            border: 2px dashed #30363d; 
            border-radius: 8px; 
            padding: 30px; 
            text-align: center; 
            cursor: pointer; 
            transition: border-color 0.2s;
            background: #0d1117;
        }
        .upload-area:hover { border-color: #58a6ff; }
        .upload-area input { display: none; }
        .btn { 
            background: #238636; 
            color: white; 
            border: none; 
            padding: 12px 24px; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 1rem; 
            width: 100%; 
            margin-top: 10px; 
            transition: background 0.2s;
        }
        .btn:hover { background: #2ea043; }
        .btn:disabled { background: #21262d; color: #484f58; cursor: not-allowed; }
        .btn-secondary { background: #21262d; border: 1px solid #30363d; }
        .btn-secondary:hover { background: #30363d; }
        .btn-primary { background: #1f6feb; }
        .btn-primary:hover { background: #388bfd; }
        .btn-download { background: #8957e5; }
        .btn-download:hover { background: #a371f7; }
        .preview { 
            background: #0d1117; 
            border-radius: 6px; 
            padding: 15px; 
            margin-top: 15px; 
            max-height: 250px; 
            overflow-y: auto; 
            font-size: 0.85rem; 
            white-space: pre-wrap; 
            font-family: 'SF Mono', Monaco, monospace;
            color: #c9d1d9;
            border: 1px solid #30363d;
            display: none;
        }
        .tabs { display: flex; gap: 5px; margin-bottom: 15px; }
        .tab { 
            padding: 10px 20px; 
            background: #21262d; 
            border-radius: 6px; 
            cursor: pointer; 
            border: 1px solid #30363d;
            color: #c9d1d9;
        }
        .tab.active { background: #1f6feb; color: white; border-color: #1f6feb; }
        .tab-content { display: none; overflow: hidden; min-width: 0; }
        .tab-content.active { display: block; }
        .output-area { 
            background: #0d1117; 
            border-radius: 6px; 
            padding: 20px; 
            height: 400px;
            max-height: 400px;
            overflow-y: auto;
            overflow-x: hidden;
            line-height: 1.6; 
            border: 1px solid #30363d;
            color: #c9d1d9;
            box-sizing: border-box;
            min-width: 0;
        }
        .chat-container { display: flex; flex-direction: column; height: 400px; overflow: hidden; }
        .chat-messages { 
            flex: 1; 
            overflow-y: auto; 
            overflow-x: hidden;
            background: #0d1117; 
            border-radius: 6px; 
            padding: 15px; 
            display: flex; 
            flex-direction: column; 
            gap: 10px;
            border: 1px solid #30363d;
            min-width: 0;
        }
        .message { padding: 10px 15px; border-radius: 10px; max-width: 85%; word-wrap: break-word; overflow-wrap: break-word; }
        .message.user { background: #1f6feb; color: white; align-self: flex-end; }
        .message.assistant { 
            background: #161b22; 
            border: 1px solid #30363d; 
            align-self: flex-start; 
            color: #c9d1d9;
        }
        .chat-input { display: flex; gap: 10px; margin-top: 10px; }
        .chat-input input { 
            flex: 1; 
            padding: 12px; 
            border: 1px solid #30363d; 
            border-radius: 6px; 
            font-size: 1rem; 
            background: #0d1117; 
            color: #c9d1d9;
        }
        .chat-input input:focus { outline: none; border-color: #58a6ff; }
        .chat-input input::placeholder { color: #6e7681; }
        .info { font-size: 0.85rem; color: #8b949e; margin-top: 15px; text-align: center; }
        .info code { background: #21262d; padding: 2px 6px; border-radius: 4px; color: #f0f6fc; }
        .loading { color: #8b949e; }
        .loading::after { content: '...'; animation: dots 1.5s infinite; }
        @keyframes dots { 0%,20% { content: '.'; } 40% { content: '..'; } 60%,100% { content: '...'; } }
        .btn-row { display: flex; gap: 10px; }
        .btn-row .btn { margin-top: 0; flex: 1; }
        .placeholder { color: #484f58; text-align: center; padding: 40px; }
        /* Markdown rendering styles */
        .markdown-body { font-size: 0.95rem; color: #c9d1d9; max-width: 100%; width: 100%; box-sizing: border-box; overflow-wrap: break-word; word-break: break-word; }
        .markdown-body * { max-width: 100%; box-sizing: border-box; word-break: break-word; }
        .markdown-body pre { background: #161b22; padding: 1rem; border-radius: 6px; margin: 0.5em 0; white-space: pre-wrap; word-break: break-all; overflow-wrap: break-word; }
        .markdown-body code { font-family: 'SF Mono', Monaco, monospace; background: #161b22; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
        .markdown-body pre code { background: transparent; padding: 0; }
        .markdown-body table { border-collapse: collapse; width: 100%; max-width: 100%; margin: 0.5em 0; display: block; overflow-x: auto; }
        .markdown-body th, .markdown-body td { border: 1px solid #30363d; padding: 0.5rem; text-align: left; word-break: break-word; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 ScratchLM</h1>
            <p>Zero-DB AI Study Assistant</p>
        </header>
        
        <div class="main-grid">
            <aside>
                <div class="panel">
                    <div class="panel-title">📁 Upload PDFs</div>
                    <div class="upload-area" id="upload-area">
                        <input type="file" id="file-input" accept=".pdf" multiple>
                        <p>📄 Drop PDFs or click to browse</p>
                        <p id="file-count" style="margin-top: 10px; font-size: 0.9rem; color: #6e7681;"></p>
                    </div>
                    <button class="btn" id="extract-btn" disabled>⚡ Extract</button>
                    <div id="extracted-preview" class="preview"></div>
                </div>
            </aside>
            
            <main>
                <div class="panel">
                    <div class="tabs">
                        <button class="tab active" data-tab="cheatsheet">📚 Cheatsheet</button>
                        <button class="tab" data-tab="chat">💬 Chat</button>
                    </div>
                    
                    <div id="cheatsheet" class="tab-content active">
                        <div class="btn-row">
                            <button class="btn btn-primary" id="generate-btn" disabled>✨ Generate</button>
                            <button class="btn btn-download" id="download-btn" disabled>📥 Download .md</button>
                        </div>
                        <div id="cheatsheet-output" class="output-area">
                            <div class="placeholder">Generated cheatsheet will appear here.</div>
                        </div>
                    </div>
                    
                    <div id="chat" class="tab-content">
                        <div class="chat-container">
                            <div class="chat-messages" id="chat-messages">
                                <div class="message assistant">Hello! Upload PDFs and extract text to start chatting.</div>
                            </div>
                            <div class="chat-input">
                                <input type="text" id="chat-input" placeholder="Ask about your documents..." disabled>
                                <button class="btn btn-secondary" id="send-btn" disabled>Send</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <p class="info">
                    Model: Gemma 4 31B (via Google AI Studio API)
                </p>
            </main>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/marked@9.1.6/marked.min.js"></script>
    <script>
        marked.setOptions({ 
            breaks: true, 
            gfm: true,
            headerIds: false,
            mangle: false
        });
        
        let extractedText = '';
        let files = [];
        let currentCheatsheet = '';
        
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            });
        });
        
        // File upload
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        const fileCount = document.getElementById('file-count');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.style.borderColor = '#58a6ff'; });
        uploadArea.addEventListener('dragleave', () => uploadArea.style.borderColor = '#30363d');
        uploadArea.addEventListener('drop', e => {
            e.preventDefault();
            uploadArea.style.borderColor = '#30363d';
            files = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
            updateUI();
        });
        fileInput.addEventListener('change', () => {
            files = Array.from(fileInput.files);
            updateUI();
        });
        
        function updateUI() {
            fileCount.textContent = files.length ? `${files.length} file(s)` : '';
            document.getElementById('extract-btn').disabled = !files.length;
        }
        
        // Extract
        document.getElementById('extract-btn').addEventListener('click', async () => {
            const btn = document.getElementById('extract-btn');
            const preview = document.getElementById('extracted-preview');
            
            btn.disabled = true;
            btn.textContent = '⏳ Extracting...';
            preview.style.display = 'block';
            preview.textContent = 'Extracting...';
            
            const formData = new FormData();
            files.forEach(f => formData.append('files', f));
            
            try {
                const resp = await fetch('/extract', { method: 'POST', body: formData });
                const data = await resp.json();
                extractedText = data.full_text || '';
                preview.textContent = data.preview || data.error || 'Done';
                document.getElementById('generate-btn').disabled = false;
                document.getElementById('chat-input').disabled = false;
                document.getElementById('send-btn').disabled = false;
                btn.textContent = '✅ Done';
            } catch (err) {
                preview.textContent = 'Error: ' + err.message;
                btn.textContent = '⚡ Extract';
            }
            
            setTimeout(() => { btn.disabled = false; btn.textContent = '⚡ Extract'; }, 2000);
        });
        
        // Generate cheatsheet
        document.getElementById('generate-btn').addEventListener('click', async () => {
            const btn = document.getElementById('generate-btn');
            const output = document.getElementById('cheatsheet-output');
            
            btn.disabled = true;
            btn.textContent = '⏳ Generating...';
            output.innerHTML = '<p class="loading">Generating cheatsheet</p>';
            
            try {
                const resp = await fetch('/generate-cheatsheet', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ context: extractedText })
                });
                const data = await resp.json();
                currentCheatsheet = data.result || data.error || '';
                output.innerHTML = `<div class="markdown-body">${marked.parse(currentCheatsheet)}</div>`;
                document.getElementById('download-btn').disabled = !currentCheatsheet;
            } catch (err) {
                output.innerHTML = `<div class="markdown-body error-text">Error: ${err.message}</div>`;
            }
            
            btn.disabled = false;
            btn.textContent = '✨ Generate';
        });
        
        // Download cheatsheet
        document.getElementById('download-btn').addEventListener('click', () => {
            if (!currentCheatsheet) return;
            const blob = new Blob([currentCheatsheet], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'scratchlm-cheatsheet.md';
            a.click();
            URL.revokeObjectURL(url);
        });
        
        // Chat
        document.getElementById('send-btn').addEventListener('click', sendMessage);
        document.getElementById('chat-input').addEventListener('keypress', e => { if (e.key === 'Enter') sendMessage(); });
        
        async function sendMessage() {
            const input = document.getElementById('chat-input');
            const messages = document.getElementById('chat-messages');
            const msg = input.value.trim();
            if (!msg || !extractedText) return;
            
            input.value = '';
            messages.innerHTML += `<div class="message user">${escapeHtml(msg)}</div>`;
            messages.innerHTML += `<div class="message assistant loading">Thinking</div>`;
            messages.scrollTop = messages.scrollHeight;
            
            try {
                const resp = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message: msg, context: extractedText, history: getHistory() })
                });
                const data = await resp.json();
                messages.innerHTML = messages.innerHTML.replace('<div class="message assistant loading">Thinking</div>', '');
                const responseText = data.response || data.error || 'No response';
                messages.innerHTML += `<div class="message assistant"><div class="markdown-body">${marked.parse(responseText)}</div></div>`;
            } catch (err) {
                messages.innerHTML = messages.innerHTML.replace('<div class="message assistant loading">Thinking</div>', '');
                messages.innerHTML += `<div class="message assistant"><div class="markdown-body error-text">Error: ${err.message}</div></div>`;
            }
            messages.scrollTop = messages.scrollHeight;
        }
        
        function getHistory() {
            return Array.from(document.querySelectorAll('.message:not(.loading)'))
                .map(m => ({ role: m.classList.contains('user') ? 'user' : 'assistant', content: m.textContent }));
        }
        
        function escapeHtml(text) {
            const d = document.createElement('div');
            d.textContent = text;
            return d.innerHTML;
        }
    </script>
</body>
</html>
"""


@app.post("/extract")
async def extract_files(files: list[UploadFile] = File(...)):
    """Extract text from uploaded PDFs."""
    if not files:
        return JSONResponse({"error": "No files", "preview": "", "full_text": ""})
    
    consolidated, full_text = [], ""
    
    for i, file in enumerate(files):
        text = parse_pdf(await file.read()) if file.filename.lower().endswith('.pdf') else f"[Unsupported: {file.filename}]"
        header = f"\n=== DOCUMENT {i+1}: {file.filename} ===\n"
        consolidated.append(header + text)
        full_text += header + text + "\n"
    
    preview = "\n".join(consolidated)
    return {"preview": preview[:3000] + ("..." if len(preview) > 3000 else ""), "full_text": preview}


@app.post("/generate-cheatsheet")
async def generate_cheatsheet(request: dict):
    """Generate cheatsheet from context."""
    context = request.get("context", "")
    if not context:
        return JSONResponse({"error": "No context", "result": ""})
    
    prompt = """Create a 4-zone markdown cheatsheet:

## Zone A: Concept Deep-Dive
Key concepts, definitions, theorems

## Zone B: Real-World Analogies
Intuitive explanations

## Zone C: Worked Problems
Step-by-step solutions with LaTeX math

## Zone D: Exam Traps & Strategy
Common mistakes and how to avoid them"""
    
    return {"result": generate_content(prompt, context)}


@app.post("/chat")
async def chat(request: dict):
    """RAG chat with context."""
    message = request.get("message", "")
    context = request.get("context", "")
    history = request.get("history", [])
    
    if not message:
        return JSONResponse({"error": "No message", "response": ""})
    if not context:
        return JSONResponse({"error": "Extract documents first", "response": ""})
    
    history_str = "\n".join(f"{'User' if m.get('role') == 'user' else 'Assistant'}: {m.get('content', '')}" for m in history)
    prompt = f"Tutor mode. Answer step-by-step.\n\nContext:\n{context}\n\nHistory:\n{history_str}\n\nUser: {message}"
    
    return {"response": generate_content(prompt, "")}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
