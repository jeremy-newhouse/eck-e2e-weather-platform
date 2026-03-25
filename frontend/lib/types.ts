export interface WeatherData {
  city: string;
  temperature: number;
  humidity: number;
  wind_speed: number;
  description: string;
  timestamp: string;
}

export interface MetricBucket {
  bucket: string;
  metric_name: string;
  avg_value: number;
}

export interface MetricsResponse {
  city: string;
  range: string;
  metrics: MetricBucket[];
}

export interface ChatRequest {
  session_id?: string;
  message: string;
  city?: string;
}

export interface ChatResponse {
  session_id: string;
  role: string;
  content: string;
  created_at: string;
}

export type MetricRange = "1h" | "6h" | "24h" | "7d";

export interface ChartData {
  bucket: string;
  temperature?: number;
  humidity?: number;
  wind_speed?: number;
}
