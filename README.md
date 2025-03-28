# CV Manager 📄✨

## Project Overview

CV Manager is an intelligent resume parsing and analysis tool built with Next.js and FastAPI, designed to help the recruiters to screen resumes with detailed analytics and help job seekers understand their application potential and optimize their resumes.

![Project Screenshots](https://github.com/user-attachments/assets/61e65991-7f7c-48ec-98a4-3f6510285cad)
![Analysis View](https://github.com/user-attachments/assets/36998163-03d9-4079-a2df-eeea9d0ee9cd)

## 🚀 Features

- **Resume Upload**: Easily upload resumes in PDF or DOCX formats
- **Intelligent Parsing**: Advanced AI-powered resume analysis
- **Detailed Insights**: 
  - Skills extraction
  - Experience breakdown
  - Keyword matching
  - Semantic matching
- **User-Friendly Interface**: Clean, intuitive design

## 🛠 Tech Stack

### Frontend
- Next.js
- React
- Tailwind CSS

### Backend
- FastAPI (Python)
- Machine Learning Libraries
  - spaCy
  - NLTK
  - pdfminer-six

### Deployment
- Frontend: Render
- Backend: Render

## 📦 Project Structure

```
cv-manager/
│
├── client/                 # Next.js Frontend
│   ├── components/
│   ├── app/
│   ├── public/
│   └── ...
│
└── server/                 # FastAPI Backend
    ├── main.py             # Primary API entry point
    └── requirements.txt
```

## 🔧 Local Development Setup
Change the frontend and backend url in the code with your localhost url to run it locally.
### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- pip

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

### Backend Setup
```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🌐 Deployment Notes

- **Frontend**: Deployed on Render
- **Backend**: Deployed on Render
- **Current Limitation**: Due to Render's 512MB resource constraint, the application can analyze only one resume simultaneously. But using your local machine you can screen multiple number of resume at once.

## 🔮 Future Roadmap
- AI resume builder
- Directly message the applicants after screening using the extracted candidate info
- Job market trend integration

## 👨‍💻 Author
[Jeet Sarkar/ironsoldier353]

---

**Happy Resume Optimization!** 📈🚀
