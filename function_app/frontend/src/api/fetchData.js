// frontend/src/api/fetchData.js

const API_URL =
  "https://diet-analysis-function-app-grp7-gedbcqgtbzbehybd.westus-01.azurewebsites.net/api/process";

export async function getDietInsights() {
  try {
    console.log("Calling Azure Function:", API_URL);

    const res = await fetch(API_URL);

    // If the fetch itself failed (CORS/network), this next line might not even run.
    console.log("Function response status:", res.status);

    const text = await res.text();
    console.log("Raw response text from Function:", text);

    if (!res.ok) {
      // This will be caught in index.html and show "Error loading data..."
      throw new Error(`HTTP ${res.status}: ${text}`);
    }

    // If everything is OK, parse JSON and return
    return JSON.parse(text);
  } catch (err) {
    console.error("getDietInsights() error:", err);
    throw err;
  }
}
