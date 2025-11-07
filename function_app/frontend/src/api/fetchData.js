export async function getDietInsights() {
  const endpoint =
    'https://diet-analysis-function-app-grp7-gedbcqgtbzbehybd.westus-01.azurewebsites.net/api/process';

  const res = await fetch(endpoint, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`[API] ${res.status} ${res.statusText} ${text}`);
  }

  const data = await res.json();
  return {
    datasetName: 'All_Diets.csv',
    fetchedAt: new Date().toISOString(),
    records: data.result ?? [],
  };
}

