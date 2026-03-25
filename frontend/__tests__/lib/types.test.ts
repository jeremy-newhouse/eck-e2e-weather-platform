import type {
  WeatherData,
  MetricBucket,
  MetricsResponse,
  ChatRequest,
  ChatResponse,
  MetricRange,
  ChartData,
} from "@/lib/types";

describe("lib/types", () => {
  it("WeatherData shape is assignable", () => {
    const w: WeatherData = {
      city: "London",
      temperature: 15.5,
      humidity: 80,
      wind_speed: 3.2,
      description: "clear sky",
      timestamp: "2026-03-25T12:00:00Z",
    };
    expect(w.city).toBe("London");
    expect(w.temperature).toBe(15.5);
    expect(w.humidity).toBe(80);
    expect(w.wind_speed).toBe(3.2);
    expect(w.description).toBe("clear sky");
    expect(w.timestamp).toBe("2026-03-25T12:00:00Z");
  });

  it("MetricBucket shape is assignable", () => {
    const mb: MetricBucket = {
      bucket: "2026-03-25T12:00:00Z",
      metric_name: "temperature",
      avg_value: 15.5,
    };
    expect(mb.metric_name).toBe("temperature");
  });

  it("MetricsResponse shape is assignable", () => {
    const mr: MetricsResponse = {
      city: "London",
      range: "1h",
      metrics: [],
    };
    expect(mr.city).toBe("London");
  });

  it("ChatRequest shape allows optional fields", () => {
    const req: ChatRequest = { message: "Hello" };
    expect(req.message).toBe("Hello");
    expect(req.session_id).toBeUndefined();
    expect(req.city).toBeUndefined();
  });

  it("ChatResponse shape is assignable", () => {
    const res: ChatResponse = {
      session_id: "abc123",
      role: "assistant",
      content: "The weather is nice.",
      created_at: "2026-03-25T12:00:00Z",
    };
    expect(res.role).toBe("assistant");
  });

  it("MetricRange accepts valid values", () => {
    const r1: MetricRange = "1h";
    const r2: MetricRange = "6h";
    const r3: MetricRange = "24h";
    const r4: MetricRange = "7d";
    expect([r1, r2, r3, r4]).toHaveLength(4);
  });

  it("ChartData shape allows optional metric fields", () => {
    const cd: ChartData = { bucket: "2026-03-25T12:00:00Z" };
    expect(cd.temperature).toBeUndefined();
    expect(cd.humidity).toBeUndefined();
    expect(cd.wind_speed).toBeUndefined();
  });
});
