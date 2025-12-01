# api/predict.py
import os
import io
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image

app = FastAPI()

MODEL_URL = os.environ.get("MODEL_URL", "")   # set this in Render if you have a remote model
MODEL_PATH = "/tmp/trace_net_model.pt"
_model = None

def download_model_if_needed():
    global _model
    if _model is not None or not MODEL_URL:
        return
    if not os.path.exists(MODEL_PATH):
        r = requests.get(MODEL_URL, stream=True, timeout=60)
        r.raise_for_status()
        with open(MODEL_PATH, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
    # Example: try to load a torch model if you included torch in requirements
    try:
        import torch
        _model = torch.load(MODEL_PATH, map_location="cpu")
        _model.eval()
    except Exception:
        # If loading fails or torch not installed, keep _model None
        _model = None

@app.on_event("startup")
def startup_event():
    try:
        download_model_if_needed()
    except Exception:
        pass

def predict_from_image(img: Image.Image):
    # TODO: replace with your repo's preprocessing + inference code
    # Placeholder:
    return "Generated recipe (placeholder). Replace with your model inference."

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    if _model is None and MODEL_URL:
        try:
            download_model_if_needed()
        except Exception:
            pass

    # Run inference (placeholder if model missing)
    recipe = predict_from_image(img)
    return {"recipe": recipe}
