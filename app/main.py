from fastapi import FastAPI
from app.detector import detector

app = FastAPI()


@app.post("/start")
def start_camera():
    if detector.running:
        return {"status": "Камера уже запущена"}
    detector.start()
    return {"status": "Камера запущена"}


@app.post("/stop")
def stop_camera():
    if not detector.running:
        return {"status": "Камера уже остановлена"}
    detector.stop()
    return {"status": "Камера остановлена"}
