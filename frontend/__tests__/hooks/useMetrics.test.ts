import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement } from "react";
import type { ReactNode } from "react";
import { useMetrics } from "@/hooks/useMetrics";
import * as api from "@/lib/api";
import type { MetricsResponse } from "@/lib/types";

jest.mock("@/lib/api");

const mockMetricsData: MetricsResponse = {
  city: "London",
  range: "1h",
  metrics: [
    {
      bucket: "2026-03-25T12:00:00Z",
      metric_name: "temperature",
      avg_value: 15.5,
    },
    { bucket: "2026-03-25T12:00:00Z", metric_name: "humidity", avg_value: 80 },
  ],
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return createElement(
      QueryClientProvider,
      { client: queryClient },
      children,
    );
  };
}

describe("useMetrics", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("is disabled when city is null", () => {
    const { result } = renderHook(() => useMetrics(null, "1h"), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe("idle");
    expect(result.current.data).toBeUndefined();
  });

  it("calls getMetrics when city is provided", async () => {
    const getMetricsMock = jest
      .spyOn(api, "getMetrics")
      .mockResolvedValueOnce(mockMetricsData);

    const { result } = renderHook(() => useMetrics("London", "1h"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(getMetricsMock).toHaveBeenCalledWith("London", "1h");
    expect(result.current.data).toEqual(mockMetricsData);
  });

  it("returns error on API failure", async () => {
    jest
      .spyOn(api, "getMetrics")
      .mockRejectedValueOnce(new Error("Metrics service unavailable"));

    const { result } = renderHook(() => useMetrics("London", "1h"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeInstanceOf(Error);
    expect((result.current.error as Error).message).toBe(
      "Metrics service unavailable",
    );
  });

  it("uses different query keys for different ranges", async () => {
    const getMetricsMock = jest
      .spyOn(api, "getMetrics")
      .mockResolvedValue(mockMetricsData);

    const wrapper = createWrapper();

    const { result: result1h } = renderHook(() => useMetrics("London", "1h"), {
      wrapper,
    });
    const { result: result24h } = renderHook(
      () => useMetrics("London", "24h"),
      { wrapper },
    );

    await waitFor(() => expect(result1h.current.isSuccess).toBe(true));
    await waitFor(() => expect(result24h.current.isSuccess).toBe(true));

    expect(getMetricsMock).toHaveBeenCalledWith("London", "1h");
    expect(getMetricsMock).toHaveBeenCalledWith("London", "24h");
  });
});
