import { NextResponse } from "next/server";
import { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();

    // Forward the request to your FastAPI backend
    const backendResponse = await fetch('http://localhost:8000/rank-resumes/', {
      method: 'POST',
      body: formData,
    });

    if (!backendResponse.ok) {
      console.error('Backend error:', backendResponse.status, backendResponse.statusText);
      const errorText = await backendResponse.text();
      return NextResponse.json(
        { error: 'Error connecting to backend service', details: errorText },
        { status: backendResponse.status }
      );
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('API route error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}