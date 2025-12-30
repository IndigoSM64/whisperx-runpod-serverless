import runpod

def handler(job):
    return {"status": "ok", "input": job.get("input")}

runpod.serverless.start({"handler": handler})
