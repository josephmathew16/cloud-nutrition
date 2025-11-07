// function_app/frontend/src/api/fetchData.js

const API_URL =
  "https://diet-analysis-function-app-grp7-gedbcqgtbzbehybd.westus-01.azurewebsites.net/api/process";

export async function getDietInsights() {
  console.log("Calling Azure Function:", API_URL);

  const res = await fetch(API_URL);

  // For debugging in console
  console.log("Function response status:", res.status);
  const text = await res.text();
  console.log("Raw response text:", text);

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${text}`);
  }

  const data = JSON.parse(text); // { message, result }

  // Return the normalized payload that Nara's transformData helpers expect
  return {
    datasetName: "All_Diets.csv",
    fetchedAt: new Date().toISOString(),
    records: data.result // array of { Diet_type, Protein(g), Carbs(g), Fat(g) }
  };
}
