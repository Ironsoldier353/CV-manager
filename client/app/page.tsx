"use client";
import { useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

type ResumeResult = {
  filename: string;
  final_score: number;
  keyword_match: number;
  semantic_match: number;
  skill_match: number;
  experience_match: number;
  education_match: number;
  years_experience: number;
  education: string[];
  name: string;
  email: string;
  phone: string;
};

type JobAnalysis = {
  extracted_keywords: string[];
  required_experience: number;
  required_education: string | null;
};

export default function Home() {
  const [jobDescription, setJobDescription] = useState<string>("");
  const [resumes, setResumes] = useState<File[]>([]);
  const [rankedResumes, setRankedResumes] = useState<[string, string, number][]>([]);
  const [detailedResults, setDetailedResults] = useState<ResumeResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedResume, setSelectedResume] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setResumes(Array.from(e.target.files));
    }
  };

  const handleSubmit = async () => {
    if (!jobDescription.trim()) {
      alert("Please enter a job description");
      return;
    }

    if (resumes.length === 0) {
      alert("Please upload at least one resume");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("job_description", jobDescription);
    resumes.forEach((resume) => formData.append("resumes", resume));

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${errorText}`);
      }

      const data = await response.json();
      setRankedResumes(data.ranked_resumes || []);
      setDetailedResults(data.detailed_results || []);
      setSelectedResume(null);
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred while processing your request");
    } finally {
      setLoading(false);
    }
  };

  const getResumeDetails = (filename: string): ResumeResult | undefined => {
    return detailedResults.find((result) => result.filename === filename);
  };

  const getChartData = (filename: string) => {
    const resumeData = getResumeDetails(filename);
    if (!resumeData) return null;

    return {
      labels: [
        "Keyword Match",
        "Semantic Match",
        "Skill Match",
        "Experience Match",
        "Education Match",
      ],
      datasets: [
        {
          label: "Score (%)",
          data: [
            resumeData.keyword_match,
            resumeData.semantic_match,
            resumeData.skill_match,
            resumeData.experience_match,
            resumeData.education_match,
          ],
          backgroundColor: [
            "rgba(255, 99, 132, 0.6)",
            "rgba(54, 162, 235, 0.6)",
            "rgba(255, 206, 86, 0.6)",
            "rgba(75, 192, 192, 0.6)",
            "rgba(153, 102, 255, 0.6)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 206, 86, 1)",
            "rgba(75, 192, 192, 1)",
            "rgba(153, 102, 255, 1)",
          ],
          borderWidth: 1,
        },
      ],
    };
  };

  return (
    <main className="flex flex-col items-center p-6 max-w-5xl mx-auto bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-gray-900">CV Manager : Your Resume Screening System</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Job Description</h2>
          <textarea
            className="border border-gray-300 p-3 w-full h-64 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800 bg-white"
            placeholder="Paste Job Description"
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-800 mb-3">Upload Resumes</h2>
          <div className="mb-4 w-full">
            <label className="flex flex-col items-center p-4 bg-blue-50 text-blue-500 rounded-lg border-2 border-blue-200 border-dashed cursor-pointer hover:bg-blue-100">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span className="mt-2 text-base">Select PDF Resumes</span>
              <input type="file" className="hidden" multiple onChange={handleFileChange} accept=".pdf" />
            </label>
          </div>
          
          {resumes.length > 0 && (
            <div className="p-3 bg-blue-50 rounded-md mb-4">
              <p className="font-medium text-blue-800">{resumes.length} resume(s) selected:</p>
              <ul className="text-sm text-blue-700 list-disc ml-5 mt-2">
                {resumes.map((file, index) => (
                  <li key={index}>{file.name}</li>
                ))}
              </ul>
            </div>
          )}
          <button
            onClick={handleSubmit}
            disabled={loading || !jobDescription || resumes.length === 0}
            className="w-full mt-2 bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {loading ? "Processing..." : "Analyze & Rank Resumes"}
          </button>
        </div>
      </div>

      {rankedResumes.length > 0 && (
        <div className="w-full mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Rankings</h2>
            <ul className="divide-y divide-gray-200">
              {rankedResumes.map(([filename, displayName, score], index) => (
                <li
                  key={filename}
                  className={`py-3 px-3 cursor-pointer hover:bg-blue-50 rounded-md flex justify-between items-center ${selectedResume === filename ? 'bg-blue-100' : ''}`}
                  onClick={() => setSelectedResume(filename)}
                >
                  <div className="flex items-center">
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm mr-2">
                      {index + 1}
                    </span>
                    <span className="font-medium text-black">{displayName}</span>
                  </div>
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full font-medium">
                    {score}%
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {selectedResume && (
            <div className="bg-white p-6 rounded-lg shadow-md col-span-2">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Resume Analysis</h2>
              
              {getResumeDetails(selectedResume) && (
                <>
                  <div className="text-sm text-gray-500 mb-4 p-2 bg-gray-100 rounded-md">
                    <strong>File:</strong> {getResumeDetails(selectedResume)?.filename}
                  </div>
                  
                  <div className="mb-6 bg-blue-50 p-4 rounded-md">
                    <h3 className="font-semibold text-blue-800 mb-2">Candidate Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="flex flex-col">
                        <span className="text-sm text-blue-600">Name</span>
                        <span className="font-medium text-blue-800 mb-2">{getResumeDetails(selectedResume)?.name || "Not detected"}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm text-blue-600">Email</span>
                        <span className="font-medium text-blue-800">{getResumeDetails(selectedResume)?.email || "Not detected"}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm text-blue-600">Phone</span>
                        <span className="font-medium text-blue-800">{getResumeDetails(selectedResume)?.phone || "Not detected"}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-sm text-blue-600">Experience</span>
                        <span className="font-medium text-blue-800">{getResumeDetails(selectedResume)?.years_experience || "0"} years</span>
                      </div>
                      <div className="flex flex-col col-span-2">
                        <span className="text-sm text-blue-600">Education</span>
                        <span className="font-medium text-blue-800">
                          {getResumeDetails(selectedResume)?.education?.join(", ") || "Not detected"}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <h3 className="font-semibold text-gray-800 mb-2">Score Breakdown</h3>
                    {getChartData(selectedResume) && (
                      <Bar 
                        data={getChartData(selectedResume)} 
                        options={{
                          scales: {
                            y: {
                              beginAtZero: true,
                              max: 100
                            }
                          }
                        }}
                      />
                    )}
                  </div>
                  
                  <div className="mt-6 grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-3 rounded-md">
                      <span className="text-sm text-gray-600">Overall Score</span>
                      <div className="text-2xl font-bold text-blue-600">
                        {getResumeDetails(selectedResume)?.final_score}%
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded-md">
                      <span className="text-sm text-gray-600">Experience Match</span>
                      <div className="text-2xl font-bold text-blue-600">
                        {getResumeDetails(selectedResume)?.experience_match}%
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      )}
    </main>
  );
}