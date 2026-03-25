import type { MetricBucket, ChartData } from "./types";

export function pivotMetrics(metrics: MetricBucket[]): ChartData[] {
  const byBucket = new Map<string, ChartData>();
  for (const m of metrics) {
    const key = m.bucket;
    if (!byBucket.has(key)) byBucket.set(key, { bucket: key });
    const entry = byBucket.get(key)!;
    if (m.metric_name === "temperature") entry.temperature = m.avg_value;
    else if (m.metric_name === "humidity") entry.humidity = m.avg_value;
    else if (m.metric_name === "wind_speed") entry.wind_speed = m.avg_value;
  }
  return Array.from(byBucket.values()).sort((a, b) =>
    a.bucket.localeCompare(b.bucket),
  );
}
