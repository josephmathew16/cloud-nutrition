# cloud-nutrition

# Frontend – API Integration (Team Member 2)

## Function Endpoint

`https://diet-analysis-function-app-grp7-gedbcqgtbzbehybd.westus-01.azurewebsites.net/api/process`

## Files

- `src/api/fetchData.js` – fetch Azure Function response
- `src/utils/transformData.js` – process JSON for Chart.js
- `index.html` – demo page with filters, refresh, and metadata (test purpose for Task 2)

## Features

- Fetch and transform data for visualization
- Filter and refresh controls
- Metadata display (dataset name, timestamp)
- JSON preview for verification

## Data Flow

Azure Blob Storage → Azure Function → fetchData.js → transformData.js → Chart.js
