import runpod

def handler(job):
    job_input = job["input"]

    # ici plus tard :
    # - récupérer audio_url
    # - lancer whisperx
    # - retourner le texte

    return {
        "status": "ok",
        "message": "worker alive"
    }

runpod.serverless.start({"handler": handler})
