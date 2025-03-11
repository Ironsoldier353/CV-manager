"use client"; // Required for state management in App Router
import { useState } from "react";

export default function Home() {
  const [jobDescription, setJobDescription] = useState<string>("");
  const [resumes, setResumes] = useState<File[]>([]);
  const [rankedResumes, setRankedResumes] = useState<[string, number][]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setResumes(Array.from(e.target.files));
    }
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    formData.append("job_description", jobDescription);
    resumes.forEach((resume) => formData.append("resumes", resume));
  
    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        console.error("Error in response:", response.status, response.statusText);
        return;
      }
  
      const data = await response.json();
      // console.log("Response from backend:", data);
  
      if (data.ranked_resumes) {
        setRankedResumes(data.ranked_resumes);
      } else {
        console.warn("No ranked resumes received!");
      }
    } catch (error) {
      console.error("Error while uploading:", error);
    }
  };
  

  return (
    <main className="flex flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-4">Resume Screening</h1>
      
      <textarea
        className="border p-2 w-1/2"
        placeholder="Paste Job Description"
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
      />
      
      <input type="file" multiple onChange={handleFileChange} className="mt-2" />
      
      <button onClick={handleSubmit} className="bg-blue-500 text-white px-4 py-2 mt-2 rounded">
        Rank Resumes
      </button>

      <h2 className="text-2xl font-bold mt-6">Results</h2>
      <ul>
        {rankedResumes.map(([name, score]) => (
          <li key={name}>{name} - Score: {score.toFixed(2)}</li>
        ))}
      </ul>
    </main>
  );
}
