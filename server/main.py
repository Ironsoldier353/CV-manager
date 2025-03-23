from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import pdfminer.high_level
import numpy as np
import re
import spacy
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_md")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cv-manager-1.onrender.com"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

def extract_text_from_pdf(file: UploadFile) -> str:
    try:
        file.file.seek(0)  # Reset file pointer before reading
        text = pdfminer.high_level.extract_text(file.file)
        return text.strip() if text else ""
    except Exception as e:
        logger.error(f"Error extracting text from {file.filename}: {e}")
        return ""

def extract_keywords(text: str) -> list:
    doc = nlp(text)
    keywords = []
    
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) <= 3:  # Limit to reasonable length phrases
            keywords.append(chunk.text.lower())
    
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE", "LOC", "LANGUAGE"]:
            keywords.append(ent.text.lower())
    
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
            keywords.append(token.text.lower())
    
    clean_keywords = []
    for keyword in keywords:
        keyword = re.sub(r'[^\w\s]', '', keyword).strip()
        if keyword and len(keyword) > 2:
            clean_keywords.append(keyword)
    
    return list(set(clean_keywords))

def extract_contact_info(text: str) -> Dict[str, str]:
    contact_info = {
        "name": "",
        "email": "",
        "phone": ""
    }
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    section_headers = ["summary", "professional summary", "profile", "objective", "experience", 
                      "education", "skills", "projects", "certifications", "references"]
    
    for i, line in enumerate(lines[:3]):
        if (len(line) > 50 or 
            any(header in line.lower() for header in section_headers) or
            '@' in line or 
            re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line)):
            continue
            
        words = line.split()
        if 1 <= len(words) <= 4: 
            contact_info["name"] = line
            break
    
    if not contact_info["name"]:
        for i, line in enumerate(lines[:10]):
            name_prefixes = ["name:", "i am", "this is"]
            
            lower_line = line.lower()
            for prefix in name_prefixes:
                if lower_line.startswith(prefix):
                    contact_info["name"] = line[len(prefix):].strip()
                    break
            
            if contact_info["name"]:
                break
    
    if not contact_info["name"]:
        contact_headers = ["contact", "contact information", "personal information", "personal details"]
        for i, line in enumerate(lines[:-1]):  # Skip last line
            if any(header in line.lower() for header in contact_headers):
                # The name might be in the next 1-3 lines
                for j in range(1, 4):
                    if i + j < len(lines):
                        potential_name = lines[i + j]
                        if ('@' in potential_name or 
                           re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', potential_name) or
                           re.search(r'\d+ .+ (street|ave|avenue|road|rd|blvd)', potential_name.lower())):
                            continue
                        if len(potential_name) < 40:
                            contact_info["name"] = potential_name
                            break
                break
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        contact_info["email"] = email_matches[0]
    
    phone_contexts = ["phone", "mobile", "phone no","cell", "tel", "telephone", "contact"]
    
    for i, line in enumerate(lines):
        lower_line = line.lower()
        if any(context in lower_line for context in phone_contexts):
            phone_patterns = [
                r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or +1 123-456-7890
                r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # 123-456-7890
                r'\+\d{1,3}[-.\s]?\d{9,11}'  # +1 1234567890
            ]
            for pattern in phone_patterns:
                phone_matches = re.findall(pattern, line)
                if phone_matches:
                    contact_info["phone"] = phone_matches[0]
                    break
            
            if contact_info["phone"]:
                break
    
    # If phone not found with context, fall back to general extraction
    if not contact_info["phone"]:
        phone_patterns = [
            r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or +1 123-456-7890
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 123-456-7890
            r'\b\+\d{1,3}[-.\s]?\d{9,11}\b'  # +1 1234567890
        ]
        
        for pattern in phone_patterns:
            phone_matches = re.findall(pattern, text)
            if phone_matches:
                contact_info["phone"] = phone_matches[0]
                break
    
    # Final cleaning for the name
    if contact_info["name"]:
        contact_info["name"] = re.sub(r'\s+', ' ', contact_info["name"]).strip()
        for prefix in ["name:", "i am", "this is"]:
            if contact_info["name"].lower().startswith(prefix):
                contact_info["name"] = contact_info["name"][len(prefix):].strip()
    
    return contact_info

from datetime import datetime

def extract_experience(text: str) -> float:
    """Extracts years of experience from a resume."""

    experience_section = extract_work_experience_section(text)
    
    if not experience_section.strip():
        return 0.0

    # Explicit experience patterns (e.g., "5 years of experience")
    patterns = [
        r'(\d+)[\+]?\s*years?\s+(?:of\s+)?(?:work|professional|relevant)?\s*experience',
        r'(?:work|professional|relevant)\s+experience\s+(?:of\s+)?(\d+)[\+]?\s*years?',
        r'(?:over|more\sthan)\s+(\d+)\s+years?\s+(?:of\s+)?(?:work|professional|relevant)\s+experience',
        r'(\d+)\s*\+\s*years?\s+(?:of\s+)?(?:work|professional|relevant)?\s*experience',
        r'(\d+)\s*-\s*(\d+)\s*years?\s+(?:of\s+)?(?:work|professional|relevant)\s*experience',
        r'(\d+)\s*to\s*(\d+)\s*years?\s+(?:of\s+)?(?:work|professional|relevant)\s*experience'
    ]

    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, experience_section.lower())
        for match in matches:
            try:
                years = float(match) if isinstance(match, str) else float(match[1])  # Handle range case
                max_years = max(max_years, years)
            except ValueError:
                pass

    # If no explicit experience is found, estimate from work history
    if max_years == 0:
        max_years = extract_experience_from_work_dates(experience_section)

    return max_years

def extract_experience_from_work_dates(text: str) -> float:
    """Extracts experience based on job history date ranges."""

    # Extract date patterns like "2015 - 2020", "Jan 2017 to Present", etc.
    date_pattern = r'(\b(?:19|20)\d{2})\s*(?:-|–|to)\s*(\b(?:19|20)\d{2}|present|current|now)'
    matches = re.findall(date_pattern, text.lower())

    total_experience = 0
    current_year = datetime.now().year
    work_periods = []

    for start, end in matches:
        try:
            start_year = int(start)
            end_year = current_year if end in ["present", "current", "now"] else int(end)

            # Ensure valid year range
            if start_year <= end_year:
                work_periods.append((start_year, end_year))
        except ValueError:
            pass

    # Merge overlapping work periods
    work_periods.sort()  # Sort by start year
    merged_periods = []
    
    for start, end in work_periods:
        if not merged_periods or merged_periods[-1][1] < start:
            merged_periods.append((start, end))
        else:
            merged_periods[-1] = (merged_periods[-1][0], max(merged_periods[-1][1], end))

    # Calculate total experience (non-overlapping)
    for start, end in merged_periods:
        total_experience += end - start

    return total_experience

def extract_work_experience_section(text: str) -> str:
    """Extracts the relevant work experience section from the resume."""
    section_keywords = [
        "work experience", "experience", "employment history",
        "professional experience", "internships", "career summary",
        "relevant experience"
    ]
    
    # Split text into sections based on headers
    lines = text.split("\n")
    section_text = []
    in_experience_section = False
    
    for line in lines:
        line_lower = line.strip().lower()
        
        # Check if we are entering the experience section
        if any(keyword in line_lower for keyword in section_keywords):
            in_experience_section = True
            continue  # Skip the heading itself
        
        # Stop if another section starts (Education, Skills, Certifications, etc.)
        if in_experience_section and any(word in line_lower for word in ["education", "skills", "certifications", "projects", "summary"]):
            break
        
        # If we are in the experience section, collect lines
        if in_experience_section:
            section_text.append(line)
    
    return "\n".join(section_text)

# Extract education level from resume
def extract_education(text: str) -> Dict[str, bool]:
    """Extracts education qualifications from text with strict keyword matching."""
    
    education = {
        "phd": False,
        "masters": False,
        "bachelors": False,
        "diploma": False,
        "high_school": False
    }
    
    text_lower = text.lower()

    # PhD Detection
    if re.search(r'\b(ph\.?d|doctor of philosophy|doctorate)\b', text_lower):
        education["phd"] = True

    # Masters Detection
    if re.search(r'\b(m\.?s\.?|msc|m\.sc|ma|m\.a\.|mba|mtech|m\.tech|master\'?s|masters degree|master of)\b', text_lower):
        education["masters"] = True

    # Bachelors Detection (Ensures B.Tech is not confused with M.Tech)
    if re.search(r'\b(b\.?s\.?|bsc|b\.sc|ba|b\.a\.|btech|b\.tech|bachelors degree|bachelor\'?s|bachelor of)\b', text_lower):
        education["bachelors"] = True

    # Diploma Detection
    if re.search(r'\b(diploma)\b', text_lower):
        education["diploma"] = True

    # High School Detection
    if re.search(r'\b(high school|secondary school|12th|10\+2|\+2)\b', text_lower):
        education["high_school"] = True

    return education


def extract_required_experience(job_description: str) -> float:
    """Extracts required experience level from job description."""
    
    job_description = job_description.lower()
    
    required_exp_pattern = r'(?:(?:experience\s*(?:level|required)?[:\-]?\s*|at\s+least|min(?:imum)?|over|more\s+than|upto|around|approx(?:imately)?)\s*)?(\d+)[\+]?\s*years?'
    required_exp_matches = re.findall(required_exp_pattern, job_description)

    return max(map(float, required_exp_matches)) if required_exp_matches else 0


def extract_required_education(job_description: str) -> str:
    """Extracts required education level from job description."""
    
    job_description = job_description.lower()
    education_levels = {
        "phd": ["ph.d", "phd", "doctor of philosophy", "doctorate"],
        "masters": ["master", "m.s.", "msc", "m.sc", "ma", "m.a.", "mba", "m.tech", "mtech"],
        "bachelors": ["bachelor", "b.s.", "bsc", "b.sc", "ba", "b.a.", "b.tech", "btech"],
        "diploma": ["diploma"],
        "high_school": ["high school", "secondary school", "12th", "10+2", "+2"]
    }

    for level, keywords in education_levels.items():
        if any(keyword in job_description for keyword in keywords):
            return level
    
    return "Not Specified"


def calculate_skill_match(job_skills: list, resume_skills: list) -> float:
    """Calculates skill match score using word embeddings (Semantic similarity)."""
    
    if not job_skills:
        return 0.0
    
    job_vectors = [nlp(skill).vector for skill in job_skills]
    resume_vectors = [nlp(skill).vector for skill in resume_skills]
    
    matches = 0
    threshold = 0.75  # Similarity threshold
    
    for job_vec in job_vectors:
        if not resume_vectors:
            continue
            
        max_sim = max(
            np.dot(job_vec, resume_vec) / (np.linalg.norm(job_vec) * np.linalg.norm(resume_vec) + 1e-8) 
            for resume_vec in resume_vectors if np.linalg.norm(resume_vec) > 0
        )
        
        if max_sim >= threshold:
            matches += 1
    
    return (matches / len(job_skills)) * 100 if job_skills else 0


@app.post("/rank-resumes/")
async def rank_resumes(job_description: str = Form(...), resumes: List[UploadFile] = File(...)):
    if not job_description or not resumes:
        return {"error": "Job description and at least one resume are required."}
    
    job_keywords = extract_keywords(job_description)
    job_doc = nlp(job_description)

    required_experience = extract_required_experience(job_description)
    required_education = extract_required_education(job_description)

    results = []
    
    for resume in resumes:
        resume_text = extract_text_from_pdf(resume)
        if not resume_text:
            continue
            
        # Extract contact information
        contact_info = extract_contact_info(resume_text)
        
        resume_data = {
            "filename": resume.filename,
            "text_length": len(resume_text),
            "name": contact_info["name"],
            "email": contact_info["email"],
            "phone": contact_info["phone"]
        }
        
        # Extract resume information
        resume_keywords = extract_keywords(resume_text)
        resume_doc = nlp(resume_text)
        resume_experience = extract_experience(resume_text)
        resume_education = extract_education(resume_text)
        
        # Calculate different score components
        
        # 1. Keyword matching (30%)
        keyword_count = Counter(job_keywords)
        resume_keyword_count = Counter(resume_keywords)
        
        common_keywords = set(keyword_count.keys()) & set(resume_keyword_count.keys())
        keyword_score = len(common_keywords) / len(keyword_count) if keyword_count else 0
        
        # 2. Semantic similarity with job description (30%)
        if len(resume_doc) > 0 and len(job_doc) > 0:
            semantic_score = resume_doc.similarity(job_doc)
        else:
            semantic_score = 0
            
        # 3. Skills matching (20%)
        skill_score = calculate_skill_match(job_keywords, resume_keywords) / 100
        
        # 4. Experience match (10%)
        if required_experience > 0:
            if resume_experience == 0:
                exp_score = 0.0  # Fresher, does not meet experience requirement
            elif resume_experience >= required_experience:
                exp_score = 1.0  # Meets or exceeds requirement
            else:
                exp_score = resume_experience / required_experience  # Partial match
        else:
            exp_score = 1.0  # No experience required, full score

        # 5. Education match (10%)
        edu_score = 0
        
        if resume_education["phd"]:
            edu_score = 1.0
        elif resume_education["masters"]:
            edu_score = 0.9
        elif resume_education["bachelors"]:
            edu_score = 0.8
        elif resume_education["associate"]:
            edu_score = 0.6
        elif resume_education["high_school"]:
            edu_score = 0.4
            
        # Calculate final weighted score (0-100 scale)
        final_score = (
            keyword_score * 30 +
            semantic_score * 30 +
            skill_score * 20 +
            exp_score * 10 +
            edu_score * 10
        )
        
        # Record details for analysis
        resume_data.update({
            "keyword_match": round(keyword_score * 100, 2),
            "semantic_match": round(semantic_score * 100, 2),
            "skill_match": round(skill_score * 100, 2),
            "experience_match": round(exp_score * 100, 2),
            "education_match": round(edu_score * 100, 2),
            # "matched_keywords": list(common_keywords),
            "years_experience": resume_experience,
            "education": [level for level, found in resume_education.items() if found],
            "final_score": round(final_score, 2)
        })
        
        results.append(resume_data)
    
    # Sort resumes by final score
    sorted_results = sorted(results, key=lambda x: x["final_score"], reverse=True)
    
    # Use names instead of filenames for display when available
    ranked_resumes = []
    for r in sorted_results:
        display_name = r["name"] if r["name"] else r["filename"]
        ranked_resumes.append((r["filename"], display_name, r["final_score"]))
    
    return {
        "ranked_resumes": ranked_resumes,
        "detailed_results": sorted_results,
        "job_analysis": {
            "extracted_keywords": job_keywords,
            "required_experience": required_experience,
            "required_education": required_education
        }
    }