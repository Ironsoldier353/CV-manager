from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import pdfminer.high_level
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract text from PDFs **without saving them**
def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        file.file.seek(0)  # Reset file pointer before reading
        text = pdfminer.high_level.extract_text(file.file)
        return text.strip().lower() if text else ""  # Normalize text
    except Exception as e:
        print(f"Error extracting text from {file.filename}: {e}")
        return ""

@app.post("/rank-resumes/")
async def rank_resumes(job_description: str = Form(...), resumes: List[UploadFile] = File(...)):
    resume_texts = []
    resume_names = []

    # Convert job description to lowercase for consistency
    job_description = job_description.strip().lower()

    for resume in resumes:
        text = extract_text_from_pdf(resume)  
        if text:  # Only add non-empty resumes
            resume_texts.append(text)
            resume_names.append(resume.filename)

    if not resume_texts:
        return {"error": "No valid resumes were processed."}

    # Vectorize job description & resumes
    vectorizer = TfidfVectorizer()
    texts = [job_description] + resume_texts
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Compute cosine similarity scores
    scores = np.dot(tfidf_matrix[0], tfidf_matrix[1:].T).toarray().flatten()

    # Rank resumes
    ranked_resumes = sorted(zip(resume_names, scores), key=lambda x: x[1], reverse=True)

    return {"ranked_resumes": ranked_resumes}
