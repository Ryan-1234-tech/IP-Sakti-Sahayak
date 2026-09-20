"""
Interactive Demo Application for IP-SAKTI Sahayak (Member 4 - Multilingual & Voice).
Supports both CLI mode and modern Web Dashboard mode with audio playback.
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    from src.multilingual.pipeline import (
        process_multilingual_query,
        format_multilingual_response,
    )
    from src.demo.mock_rag import MockIPRAGEngine
    from src.voice.tts import synthesize_speech
    from src.voice.stt import transcribe_audio
except (ImportError, ModuleNotFoundError):
    from multilingual.pipeline import (
        process_multilingual_query,
        format_multilingual_response,
    )
    from demo.mock_rag import MockIPRAGEngine
    from voice.tts import synthesize_speech
    from voice.stt import transcribe_audio

rag_engine = MockIPRAGEngine()


def run_pipeline_step_by_step(query_text: str, target_style: str = None) -> dict:
    """Executes the full Member 4 flow with diagnostic breakdowns."""
    print(f"\n=======================================================")
    print(f"📥 [STEP 1] Input Query: \"{query_text}\"")
    print(f"=======================================================")

    # Step 1: Multilingual Processing & Normalization
    proc_result = process_multilingual_query(query_text)
    style_to_use = target_style or proc_result.get("target_response_style", "hinglish")
    print(f"🔍 Detected Language : {proc_result['language']} (Script: {proc_result['detected_script']})")
    print(f"🎯 IP Intent Category: {proc_result['intent_category']}")
    print(f"✨ Normalized Query  : \"{proc_result['normalized_query']}\"")
    print(f"⚙️  Engine Used       : {proc_result['engine']}")

    # Step 2: RAG Retrieval (English Grounding)
    print(f"\n📚 [STEP 2] Querying IP-SAKTI RAG Engine with Normalized Query...")
    rag_result = rag_engine.query(
        proc_result["normalized_query"],
        intent_category=proc_result["intent_category"]
    )
    print(f"📄 Topic             : {rag_result['topic']}")
    print(f"📖 English RAG Answer:\n{rag_result['answer']}")

    # Step 3: Response Localization (Hindi / Hinglish)
    print(f"\n🌐 [STEP 3] Localizing Response to User's Language ({proc_result['target_response_language']} / {style_to_use})...")
    loc_result = format_multilingual_response(
        english_response=rag_result["answer"],
        target_language=proc_result["target_response_language"],
        style=style_to_use
    )
    print(f"🗣️ Localized Output ({loc_result['style']}):\n{loc_result['localized_response']}")

    # Step 4: Text-to-Speech Audio Synthesis
    print(f"\n🎙️ [STEP 4] Synthesizing Voice Audio Response...")
    tts_result = synthesize_speech(
        text=loc_result["localized_response"],
        language=proc_result["target_response_language"]
    )
    if tts_result["status"] == "success":
        print(f"🔊 Audio generated successfully: {tts_result['audio_path']}")
    else:
        print(f"⚠️ Audio synthesis note: {tts_result.get('error')}")

    return {
        "input": query_text,
        "multilingual_metadata": proc_result,
        "rag_result": rag_result,
        "localized_response": loc_result,
        "tts_result": tts_result
    }


def run_cli_interactive():
    """Runs interactive terminal loop for live judging & testing."""
    print("==================================================================")
    print("🇮🇳 IP-SAKTI Sahayak — Member 4: Multilingual & Voice Assistant")
    print("==================================================================")
    print("Supported inputs: Hindi (Devanagari), Hinglish (Roman script), English.")
    print("Type 'exit' to quit.\n")

    sample_queries = [
        "Maine Ayurvedic medicine banayi hai, isko patent kaise karu?",
        "आयुर्वेदिक दवा का पेटेंट कैसे कराएं?",
        "Brand name aur logo register karne ke liye kitna fees lagta hai?",
        "Provisional patent file karne ke baad permanent patent kitne din me file karna hota hai?",
        "How can I patent a software algorithm in India?"
    ]

    print("Quick Sample Queries you can test:")
    for idx, q in enumerate(sample_queries, 1):
        print(f"  [{idx}] {q}")
    print()

    while True:
        try:
            user_input = input("\nEnter Query (or sample #1-5): ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting IP-SAKTI Multilingual Module. Dhanyawad!")
                break

            # If user selected a number
            if user_input.isdigit() and 1 <= int(user_input) <= len(sample_queries):
                user_input = sample_queries[int(user_input) - 1]

            run_pipeline_step_by_step(user_input)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


def run_web_server(port: int = 5000):
    """Launches lightweight Flask web demo dashboard with real-time UI & audio player."""
    from flask import Flask, request, jsonify, render_template_string

    app = Flask(__name__)

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IP-SAKTI Sahayak - Multilingual & Voice Engine</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .card-custom { background: #1e293b; border: 1px solid #334155; border-radius: 12px; }
            .badge-lang { background: #3b82f6; font-size: 0.85rem; }
            .badge-intent { background: #10b981; font-size: 0.85rem; }
            .accent-text { color: #38bdf8; }
            .btn-preset { font-size: 0.85rem; margin: 4px; border-radius: 20px; }
            .result-box { background: #090d16; border: 1px solid #1e293b; border-radius: 8px; padding: 15px; }
            pre { color: #a5f3fc; }
        </style>
    </head>
    <body class="p-4">
        <div class="container" style="max-width: 1000px;">
            <div class="text-center mb-4">
                <h2 class="fw-bold text-white"><i class="fa-solid fa-language text-primary me-2"></i>IP-SAKTI Sahayak</h2>
                <p class="text-secondary">Member 4: Multilingual Normalization (Hindi/Hinglish/English) & Voice Engine</p>
                <div class="d-inline-flex gap-2">
                    <span class="badge bg-primary">Hindi / Hinglish / English</span>
                    <span class="badge bg-success">Govt of India Bhashini Ready</span>
                    <span class="badge bg-info text-dark">Indian Patent Office RAG Bridge</span>
                </div>
            </div>

            <!-- Input Card -->
            <div class="card card-custom p-4 mb-4 shadow">
                <label class="form-label fw-bold text-white">Enter Your Intellectual Property Query (Voice / Text):</label>
                <div class="input-group mb-3">
                    <input type="text" id="queryInput" class="form-control bg-dark text-white border-secondary" 
                           placeholder="e.g. Maine Ayurvedic medicine banayi hai, isko patent kaise karu?" value="Maine Ayurvedic medicine banayi hai, isko patent kaise karu?">
                    <button class="btn btn-primary px-4 fw-bold" onclick="processQuery()">
                        <i class="fa-solid fa-paper-plane me-1"></i> Process Query
                    </button>
                </div>

                <div>
                    <span class="text-secondary small fw-bold">Try Sample Queries:</span>
                    <button class="btn btn-outline-info btn-sm btn-preset" onclick="setQuery('Maine Ayurvedic medicine banayi hai, isko patent kaise karu?')">🌿 Ayurvedic Medicine (Hinglish)</button>
                    <button class="btn btn-outline-info btn-sm btn-preset" onclick="setQuery('आयुर्वेदिक दवा का पेटेंट कैसे कराएं?')">🇮🇳 Ayurvedic Patent (Hindi Devanagari)</button>
                    <button class="btn btn-outline-info btn-sm btn-preset" onclick="setQuery('Brand name aur logo register karne me kitna fees lagta hai?')">🏷️ Trademark Fees (Hinglish)</button>
                    <button class="btn btn-outline-info btn-sm btn-preset" onclick="setQuery('Provisional patent file karne ke baad permanent patent kab tak file karna hota hai?')">⏳ Provisional Timeline (Hinglish)</button>
                </div>
            </div>

            <!-- Pipeline Breakdown Cards -->
            <div id="resultsArea" style="display: none;">
                <div class="row g-3 mb-4">
                    <!-- Step 1 Card -->
                    <div class="col-md-6">
                        <div class="card card-custom p-3 h-100 shadow-sm">
                            <h5 class="text-info"><i class="fa-solid fa-filter me-2"></i>1. Language & Normalization</h5>
                            <div class="mb-2">
                                <span class="badge badge-lang" id="detectedLang">Language: Hinglish</span>
                                <span class="badge badge-intent" id="detectedIntent">Intent: Patent</span>
                            </div>
                            <p class="text-secondary small mb-1">Normalized English Query for RAG:</p>
                            <div class="result-box fw-bold text-warning" id="normalizedQuery"></div>
                        </div>
                    </div>

                    <!-- Step 2 Card -->
                    <div class="col-md-6">
                        <div class="card card-custom p-3 h-100 shadow-sm">
                            <h5 class="text-success"><i class="fa-solid fa-database me-2"></i>2. IP-SAKTI RAG Retrieval</h5>
                            <p class="text-secondary small mb-1">Retrieved Statutory Topic:</p>
                            <div class="fw-bold text-white mb-2" id="ragTopic"></div>
                            <div class="result-box small" style="max-height: 140px; overflow-y: auto;" id="ragAnswer"></div>
                        </div>
                    </div>
                </div>

                <!-- Step 3 & 4 Card -->
                <div class="card card-custom p-4 mb-4 shadow">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="text-warning mb-0"><i class="fa-solid fa-comments me-2"></i>3. Localized Response & Voice Output</h5>
                        <div id="audioContainer"></div>
                    </div>
                    <div class="result-box text-white mb-3" style="font-size: 1.05rem;" id="localizedResponse"></div>
                    
                    <h6 class="text-secondary small mb-1"><i class="fa-solid fa-code me-1"></i>Standard Interface JSON (`process_multilingual_query` Output):</h6>
                    <pre class="bg-dark p-2 rounded small" id="jsonDebug"></pre>
                </div>
            </div>
        </div>

        <script>
            function setQuery(text) {
                document.getElementById('queryInput').value = text;
                processQuery();
            }

            async function processQuery() {
                const text = document.getElementById('queryInput').value.trim();
                if (!text) return;

                const resp = await fetch('/api/process', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: text})
                });
                const data = await resp.json();

                document.getElementById('resultsArea').style.display = 'block';
                document.getElementById('detectedLang').innerText = `Language: ${data.multilingual_metadata.language} (${data.multilingual_metadata.detected_script})`;
                document.getElementById('detectedIntent').innerText = `Intent: ${data.multilingual_metadata.intent_category}`;
                document.getElementById('normalizedQuery').innerText = data.multilingual_metadata.normalized_query;
                document.getElementById('ragTopic').innerText = data.rag_result.topic;
                document.getElementById('ragAnswer').innerText = data.rag_result.answer;
                document.getElementById('localizedResponse').innerText = data.localized_response.localized_response;
                document.getElementById('jsonDebug').innerText = JSON.stringify(data.multilingual_metadata, null, 2);

                if (data.tts_result && data.tts_result.audio_base64) {
                    document.getElementById('audioContainer').innerHTML = `
                        <audio controls autoplay src="data:audio/mp3;base64,${data.tts_result.audio_base64}"></audio>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """

    @app.route("/")
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route("/api/process", methods=["POST"])
    def api_process():
        body = request.get_json() or {}
        q = body.get("query", "")
        style = body.get("style", "hinglish")
        res = run_pipeline_step_by_step(q, target_style=style)
        return jsonify(res)

    print(f"🚀 IP-SAKTI Sahayak Multilingual Web Dashboard running at: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IP-SAKTI Sahayak - Multilingual & Voice Subsystem")
    parser.add_argument("--web", action="store_true", help="Launch Flask web demo dashboard")
    parser.add_argument("--port", type=int, default=5000, help="Port for web dashboard")
    parser.add_argument("--query", type=str, help="Process a single query directly")
    args = parser.parse_args()

    if args.web:
        run_web_server(port=args.port)
    elif args.query:
        run_pipeline_step_by_step(args.query)
    else:
        run_cli_interactive()
