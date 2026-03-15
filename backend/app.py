from fastapi import FastAPI, UploadFile, File
import os
from pipeline import analyze_document

# Create FastAPI app
app = FastAPI()

# Path to uploads folder
UPLOAD_FOLDER = "../uploads"

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def root():
    return {"message": "Financial Document AI Auditor Running"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    
    # Save uploaded file temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Run analysis pipeline
    result = analyze_document(file_path)

    # Delete the file after analysis for privacy
    if os.path.exists(file_path):
        os.remove(file_path)

    return result