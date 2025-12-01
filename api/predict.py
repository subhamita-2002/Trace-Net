# api/predict.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import io, os, requests
from PIL import Image

app = FastAPI()

# Use an external model URL (S3/Hugging Face). We'll set this as an env var in Vercel.
MODEL_URL = os.environ.get("MODEL_URL", "")  # set this in Vercel if you need a real model
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
            for chunk in r.iter_content(1024*1024):
                if chunk:
                    f.write(chunk)
    # Example: load a torch model if you actually have one (make sure 'torch' is in requirements)
    try:
        import torch
        _model = torch.load(MODEL_PATH, map_location="cpu")
        _model.eval()
    except Exception:
        _model = None

@app.on_event("startup")
def startup_event():
    try:
        download_model_if_needed()
    except Exception:
        pass

def predict_from_image(img: Image.Image):
    # --- Replace this function with your actual inference logic from your repo ---
    # Minimal placeholder: return fixed string so endpoint works even without model.
    return "Generated recipe (placeholder). Replace with real inference code."
    # ---------------------------------------------------------------------------

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    if _model is None and MODEL_URL:
        # attempt lazy load if startup didn't
        try:
            download_model_if_needed()
        except Exception:
            pass

    # If still no model, we run placeholder inference (so endpoint responds)
    recipe = predict_from_image(img)
    return {"recipe": recipe}
