import { render } from "@testing-library/react";
import WeatherChart from "@/components/dashboard/WeatherChart";
import type { ChartData } from "@/lib/types";

// Recharts uses ResizeObserver under the hood via ResponsiveContainer
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Capture formatter/tickFormatter callbacks from recharts components
type FormatterFn = (value: number, name: string) => [string | number, string];
type LabelFormatterFn = (label: string) => string;
type TickFormatterFn = (value: string) => string;

let capturedFormatter: FormatterFn | null = null;
let capturedLabelFormatter: LabelFormatterFn | null = null;
let capturedTickFormatter: TickFormatterFn | null = null;

jest.mock("recharts", () => {
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div>{children}</div>
    ),
    LineChart: ({ children }: { children: React.ReactNode }) => (
      <div>{children}</div>
    ),
    Line: () => null,
    XAxis: ({ tickFormatter }: { tickFormatter?: TickFormatterFn }) => {
      if (tickFormatter) capturedTickFormatter = tickFormatter;
      return null;
    },
    YAxis: () => null,
    CartesianGrid: () => null,
    Tooltip: ({
      formatter,
      labelFormatter,
    }: {
      formatter?: FormatterFn;
      labelFormatter?: LabelFormatterFn;
    }) => {
      if (formatter) capturedFormatter = formatter;
      if (labelFormatter) capturedLabelFormatter = labelFormatter;
      return null;
    },
    Legend: () => null,
  };
});

describe("WeatherChart", () => {
  beforeEach(() => {
    capturedFormatter = null;
    capturedLabelFormatter = null;
    capturedTickFormatter = null;
  });

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

  it("formatBucket (XAxis tickFormatter) formats an ISO date to a time string", () => {
    render(<WeatherChart data={[]} />);
    expect(capturedTickFormatter).not.toBeNull();
    const result = capturedTickFormatter!("2026-03-25T12:30:00Z");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("Tooltip labelFormatter formats an ISO label to a locale string", () => {
    render(<WeatherChart data={[]} />);
    expect(capturedLabelFormatter).not.toBeNull();
    const result = capturedLabelFormatter!("2026-03-25T12:00:00Z");
    expect(typeof result).toBe("string");
    expect(result.length).toBeGreaterThan(0);
  });

  it("Tooltip formatter formats temperature values with °C", () => {
    render(<WeatherChart data={[]} />);
    expect(capturedFormatter).not.toBeNull();
    const [formattedValue, label] = capturedFormatter!(20.5, "temperature");
    expect(formattedValue).toBe("20.5°C");
    expect(label).toBe("Temperature");
  });

  it("Tooltip formatter formats humidity values with %", () => {
    render(<WeatherChart data={[]} />);
    expect(capturedFormatter).not.toBeNull();
    const [formattedValue, label] = capturedFormatter!(75, "humidity");
    expect(formattedValue).toBe("75%");
    expect(label).toBe("Humidity");
  });

  it("Tooltip formatter formats wind_speed values with m/s", () => {
    render(<WeatherChart data={[]} />);
    expect(capturedFormatter).not.toBeNull();
    const [formattedValue, label] = capturedFormatter!(3.2, "wind_speed");
    expect(formattedValue).toBe("3.2 m/s");
    expect(label).toBe("Wind Speed");
  });

  it("Tooltip formatter returns raw value for unknown metric names", () => {
    render(<WeatherChart data={[]} />);
    expect(capturedFormatter).not.toBeNull();
    const [formattedValue, label] = capturedFormatter!(42, "pressure");
    expect(formattedValue).toBe(42);
    expect(label).toBe("pressure");
  });
});
