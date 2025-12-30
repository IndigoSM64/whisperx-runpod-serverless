import os
import json
import tempfile
import urllib.request

import runpod
import whisper

MODEL = None

def _download(url: str, dst_path: str):
    # Téléchargement simple via URL (idéalement une URL signée temporaire)
    req = urllib.request.Request(url, headers={"User-Agent": "runpod-worker"})
    with urllib.request.urlopen(req) as r, open(dst_path, "wb") as f:
        f.write(r.read())

def handler(job):
    """
    Input attendu (exemple):
    {
      "audio_url": "https://.../file.mp3",
      "model": "small",
      "language": null,
      "task": "transcribe"
    }
    """
    global MODEL
    inp = job.get("input", {}) or {}

    audio_url = inp.get("audio_url")
    if not audio_url:
        return {"error": "Missing input.audio_url"}

    model_name = inp.get("model", "small")         # tiny/base/small/medium/large
    language = inp.get("language")                 # ex: "fr" ou null
    task = inp.get("task", "transcribe")           # "transcribe" ou "translate"

    # Cache modèle en RAM si le worker reste chaud
    if MODEL is None or getattr(MODEL, "_model_name", None) != model_name:
        MODEL = whisper.load_model(model_name)
        MODEL._model_name = model_name

    with tempfile.TemporaryDirectory() as td:
        audio_path = os.path.join(td, "input_audio")
        _download(audio_url, audio_path)

        # Whisper retourne "segments": [{start, end, text, ...}, ...]
        result = MODEL.transcribe(
            audio_path,
            task=task,
            language=language,
            verbose=False
        )

    phrases = []
    for seg in result.get("segments", []):
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        phrases.append({
            "start": float(seg.get("start", 0.0)),
            "end": float(seg.get("end", 0.0)),
            "text": text
        })

    return {
        "status": "ok",
        "model": model_name,
        "language": result.get("language", language),
        "phrases": phrases
    }

runpod.serverless.start({"handler": handler})
