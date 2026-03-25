import type {
  WeatherData,
  MetricsResponse,
  ChatRequest,
  ChatResponse,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getWeather(city: string): Promise<WeatherData> {
  const res = await fetch(
    `${API_URL}/api/weather/${encodeURIComponent(city)}`,
    { cache: "no-store" },
  );
  if (res.status === 404) throw new Error("City not found");
  if (!res.ok) throw new Error("Weather service unavailable");
  return res.json() as Promise<WeatherData>;
}

export async function getMetrics(
  city: string,
  range: string,
): Promise<MetricsResponse> {
  const res = await fetch(
    `${API_URL}/api/metrics/${encodeURIComponent(city)}?range=${range}`,
    { cache: "no-store" },
  );
  if (!res.ok) throw new Error("Metrics service unavailable");
  return res.json() as Promise<MetricsResponse>;
}

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error("Chat service unavailable");
  return res.json() as Promise<ChatResponse>;
}
