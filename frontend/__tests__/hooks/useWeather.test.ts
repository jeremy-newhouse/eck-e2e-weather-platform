import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement } from "react";
import type { ReactNode } from "react";
import { useWeather } from "@/hooks/useWeather";
import * as api from "@/lib/api";
import type { WeatherData } from "@/lib/types";

jest.mock("@/lib/api");

const mockWeatherData: WeatherData = {
  city: "London",
  temperature: 15.5,
  humidity: 80,
  wind_speed: 3.2,
  description: "clear sky",
  timestamp: "2026-03-25T12:00:00Z",
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

describe("useWeather", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("is disabled when city is null", () => {
    const { result } = renderHook(() => useWeather(null), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe("idle");
    expect(result.current.data).toBeUndefined();
  });

  it("calls getWeather when city is provided", async () => {
    const getWeatherMock = jest
      .spyOn(api, "getWeather")
      .mockResolvedValueOnce(mockWeatherData);

    const { result } = renderHook(() => useWeather("London"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(getWeatherMock).toHaveBeenCalledWith("London");
    expect(result.current.data).toEqual(mockWeatherData);
  });

  it("returns error on API failure", async () => {
    jest
      .spyOn(api, "getWeather")
      .mockRejectedValueOnce(new Error("City not found"));

    const { result } = renderHook(() => useWeather("Unknown"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeInstanceOf(Error);
    expect((result.current.error as Error).message).toBe("City not found");
  });

  it("updates when city changes from null to a value", async () => {
    const getWeatherMock = jest
      .spyOn(api, "getWeather")
      .mockResolvedValue(mockWeatherData);

    let city: string | null = null;
    const { result, rerender } = renderHook(() => useWeather(city), {
      wrapper: createWrapper(),
    });

    expect(result.current.fetchStatus).toBe("idle");
    expect(getWeatherMock).not.toHaveBeenCalled();

    city = "London";
    rerender();

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(getWeatherMock).toHaveBeenCalledWith("London");
  });
});
