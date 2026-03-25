import { render } from "@testing-library/react";
import WeatherChart from "@/components/dashboard/WeatherChart";
import type { ChartData } from "@/lib/types";

// Recharts uses ResizeObserver under the hood via ResponsiveContainer
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

describe("WeatherChart", () => {
  it("renders without crashing with empty data", () => {
    const { container } = render(<WeatherChart data={[]} />);
    expect(container.firstChild).not.toBeNull();
  });

  it("renders with chart data", () => {
    const data: ChartData[] = [
      {
        bucket: "2026-03-25T12:00:00Z",
        temperature: 20.5,
        humidity: 75,
        wind_speed: 3.2,
      },
      {
        bucket: "2026-03-25T13:00:00Z",
        temperature: 22.0,
        humidity: 70,
        wind_speed: 2.8,
      },
    ];

    const { container } = render(<WeatherChart data={data} />);
    expect(container.firstChild).not.toBeNull();
  });
});
