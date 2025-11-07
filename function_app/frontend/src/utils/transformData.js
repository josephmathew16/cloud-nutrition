export function toChartSeries(records) {
  const labels = records.map((r) => r.Diet_type);
  const protein = records.map((r) => r['Protein(g)']);
  const carbs = records.map((r) => r['Carbs(g)']);
  const fat = records.map((r) => r['Fat(g)']);
  return { labels, protein, carbs, fat };
}

export function filterByDiet(records, include = []) {
  if (!include || include.length === 0) return records;
  const set = new Set(include);
  return records.filter((r) => set.has(r.Diet_type));
}

