import { render, screen } from "@testing-library/react";
import WeatherCard from "@/components/search/WeatherCard";
import type { WeatherData } from "@/lib/types";

jest.mock("next/link", () => {
  const MockLink = ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>;
  MockLink.displayName = "MockLink";
  return MockLink;
});

const mockWeather: WeatherData = {
  city: "London",
  temperature: 15.5,
  humidity: 80,
  wind_speed: 3.2,
  description: "clear sky",
  timestamp: "2026-03-25T12:00:00.000Z",
};

describe("WeatherCard", () => {
  it("renders city name", () => {
    render(<WeatherCard weather={mockWeather} />);
    expect(screen.getByText("London")).toBeInTheDocument();
  });

  it("renders temperature with one decimal place", () => {
    render(<WeatherCard weather={mockWeather} />);
    expect(screen.getByText("15.5°C")).toBeInTheDocument();
  });

  it("renders humidity", () => {
    render(<WeatherCard weather={mockWeather} />);
    expect(screen.getByText("80%")).toBeInTheDocument();
  });

  it("renders wind speed", () => {
    render(<WeatherCard weather={mockWeather} />);
    expect(screen.getByText("3.2 m/s")).toBeInTheDocument();
  });

  it("renders weather description", () => {
    render(<WeatherCard weather={mockWeather} />);
    expect(screen.getByText("clear sky")).toBeInTheDocument();
  });

  it("renders Temperature label", () => {
    render(<WeatherCard weather={mockWeather} />);
    expect(screen.getByText("Temperature")).toBeInTheDocument();
  });

  it("renders Humidity label", () => {
    render(<WeatherCard weather={mockWeather} />);
    expect(screen.getByText("Humidity")).toBeInTheDocument();
  });

  it("renders Wind Speed label", () => {
    render(<WeatherCard weather={mockWeather} />);
    expect(screen.getByText("Wind Speed")).toBeInTheDocument();
  });

  it("renders View Dashboard link", () => {
    render(<WeatherCard weather={mockWeather} />);
    const dashboardLink = screen.getByRole("link", { name: /view dashboard/i });
    expect(dashboardLink).toHaveAttribute("href", "/dashboard");
  });

  it("renders Ask the AI link", () => {
    render(<WeatherCard weather={mockWeather} />);
    const chatLink = screen.getByRole("link", { name: /ask the ai/i });
    expect(chatLink).toHaveAttribute("href", "/chat");
  });

  it("formats temperature with toFixed(1) for whole numbers", () => {
    const weather: WeatherData = { ...mockWeather, temperature: 20 };
    render(<WeatherCard weather={weather} />);
    expect(screen.getByText("20.0°C")).toBeInTheDocument();
  });

  it("formats humidity with toFixed(0)", () => {
    const weather: WeatherData = { ...mockWeather, humidity: 75.7 };
    render(<WeatherCard weather={weather} />);
    expect(screen.getByText("76%")).toBeInTheDocument();
  });
});
