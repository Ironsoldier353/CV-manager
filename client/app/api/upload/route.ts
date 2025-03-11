import { NextResponse } from "next/server";
import axios from "axios";

export async function POST(req: Request) {
  try {
    const formData = await req.formData();
    const backendFormData = new FormData();

    backendFormData.append("job_description", formData.get("job_description") as string);
    formData.getAll("resumes").forEach((file) => backendFormData.append("resumes", file));

    // Send request to FastAPI
    const backendResponse = await axios.post("http://127.0.0.1:8000/rank-resumes/", backendFormData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    // console.log("Backend Response:", backendResponse.data);
    
    return NextResponse.json(backendResponse.data);
  } catch (error: unknown) {
    console.error("Error sending request to FastAPI:", error);
    return NextResponse.json({ error: "Failed to process resumes" }, { status: 500 });
  }
}
