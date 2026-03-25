import { getWeather, getMetrics, sendChat } from "@/lib/api";
import type { WeatherData, MetricsResponse, ChatResponse } from "@/lib/types";

const mockWeather: WeatherData = {
  city: "London",
  temperature: 15.5,
  humidity: 80,
  wind_speed: 3.2,
  description: "clear sky",
  timestamp: "2026-03-25T12:00:00Z",
};

const mockMetrics: MetricsResponse = {
  city: "London",
  range: "1h",
  metrics: [],
};

const mockChatResponse: ChatResponse = {
  session_id: "abc123",
  role: "assistant",
  content: "The weather is nice.",
  created_at: "2026-03-25T12:00:00Z",
};

describe("lib/api", () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    global.fetch = jest.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    jest.resetAllMocks();
  });

  describe("getWeather", () => {
    it("returns weather data on success", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockWeather,
      });

      const result = await getWeather("London");
      expect(result).toEqual(mockWeather);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/weather/London"),
        expect.objectContaining({ cache: "no-store" }),
      );
    });

    it('throws "City not found" on 404', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({}),
      });

      await expect(getWeather("UnknownCity")).rejects.toThrow("City not found");
    });

    it('throws "Weather service unavailable" on other errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(getWeather("London")).rejects.toThrow(
        "Weather service unavailable",
      );
    });

    it("encodes city name in URL", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockWeather,
      });

      await getWeather("New York");
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("New%20York"),
        expect.anything(),
      );
    });
  });

  describe("getMetrics", () => {
    it("returns metrics data on success", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMetrics,
      });

      const result = await getMetrics("London", "1h");
      expect(result).toEqual(mockMetrics);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/metrics/London?range=1h"),
        expect.objectContaining({ cache: "no-store" }),
      );
    });

    it("throws on error response", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(getMetrics("London", "1h")).rejects.toThrow(
        "Metrics service unavailable",
      );
    });
  });

  describe("sendChat", () => {
    it("returns chat response on success", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockChatResponse,
      });

      const result = await sendChat({ message: "Hello" });
      expect(result).toEqual(mockChatResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/chat"),
        expect.objectContaining({
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }),
      );
    });

    it("throws on error response", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(sendChat({ message: "Hello" })).rejects.toThrow(
        "Chat service unavailable",
      );
    });

    it("serializes request body as JSON", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockChatResponse,
      });

      await sendChat({ message: "Hello", city: "London", session_id: "abc" });
      const callArgs = (global.fetch as jest.Mock).mock.calls[0];
      const body = JSON.parse(callArgs[1].body as string) as {
        message: string;
        city: string;
        session_id: string;
      };
      expect(body.message).toBe("Hello");
      expect(body.city).toBe("London");
      expect(body.session_id).toBe("abc");
    });
  });
});
