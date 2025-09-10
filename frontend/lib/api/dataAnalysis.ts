const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function analyzeData(query: string, dataFile?: string) {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      data_file: dataFile
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to analyze data");
  }

  // Check if response is streaming
  const contentType = response.headers.get("content-type");
  if (contentType?.includes("text/event-stream")) {
    return { stream: response.body };
  }

  return response.json();
}

export async function uploadCSV(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to upload file");
  }

  return response.json();
}