import { NextResponse } from "next/server";
import axios from "axios";

export async function POST(request: { formData: () => any; }) {
  try {
    const formData = await request.formData();
    
    // Forward the request to your FastAPI backend
    const backendResponse = await fetch('http://localhost:8000/rank-resumes/', {
      method: 'POST',
      body: formData,
    });
    
    if (!backendResponse.ok) {
      console.error('Backend error:', backendResponse.status, backendResponse.statusText);
      return new Response(
        JSON.stringify({ error: 'Error connecting to backend service' }), 
        { status: backendResponse.status, headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    const data = await backendResponse.json();
    return new Response(JSON.stringify(data), {
      headers: { 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('API route error:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error', details: error.message }), 
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}