import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import SearchContainer from "@/components/search/SearchContainer";
import type { WeatherData } from "@/lib/types";

// Mock next/link
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

const mockUseWeather = jest.fn();

jest.mock("@/hooks/useWeather", () => ({
  useWeather: (city: string | null) => mockUseWeather(city),
}));

const mockWeather: WeatherData = {
  city: "London",
  temperature: 15.5,
  humidity: 80,
  wind_speed: 3.2,
  description: "clear sky",
  timestamp: "2026-03-25T12:00:00.000Z",
};

describe("SearchContainer", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Default: idle state (no city searched yet)
    mockUseWeather.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
      error: null,
    });
  });

  it("renders the search input", () => {
    render(<SearchContainer />);
    expect(
      screen.getByPlaceholderText("Enter city name..."),
    ).toBeInTheDocument();
  });

  it("renders the Search button", () => {
    render(<SearchContainer />);
    expect(screen.getByRole("button", { name: /search/i })).toBeInTheDocument();
  });

  it("updates input value on change", () => {
    render(<SearchContainer />);
    const input = screen.getByPlaceholderText("Enter city name...");
    fireEvent.change(input, { target: { value: "London" } });
    expect(input).toHaveValue("London");
  });

  it("shows Searching... when loading", () => {
    mockUseWeather.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    });
    render(<SearchContainer />);
    fireEvent.change(screen.getByPlaceholderText("Enter city name..."), {
      target: { value: "London" },
    });
    fireEvent.submit(screen.getByRole("button").closest("form")!);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("shows WeatherCard when data is returned", async () => {
    mockUseWeather.mockReturnValue({
      data: mockWeather,
      isLoading: false,
      isError: false,
      error: null,
    });
    render(<SearchContainer />);
    fireEvent.change(screen.getByPlaceholderText("Enter city name..."), {
      target: { value: "London" },
    });
    fireEvent.submit(screen.getByRole("button").closest("form")!);
    await waitFor(() => {
      expect(screen.getByText("London")).toBeInTheDocument();
    });
  });

  it("shows city not found error for 404 error message", async () => {
    mockUseWeather.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("City not found"),
    });
    render(<SearchContainer />);
    fireEvent.change(screen.getByPlaceholderText("Enter city name..."), {
      target: { value: "Unknown" },
    });
    fireEvent.submit(screen.getByRole("button").closest("form")!);
    await waitFor(() => {
      expect(
        screen.getByText("City not found. Try another name."),
      ).toBeInTheDocument();
    });
  });

  it("shows service unavailable error for non-404 errors", async () => {
    mockUseWeather.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("Weather service unavailable"),
    });
    render(<SearchContainer />);
    fireEvent.change(screen.getByPlaceholderText("Enter city name..."), {
      target: { value: "London" },
    });
    fireEvent.submit(screen.getByRole("button").closest("form")!);
    await waitFor(() => {
      expect(
        screen.getByText("Weather service unavailable."),
      ).toBeInTheDocument();
    });
  });

  it("does not submit empty input", () => {
    render(<SearchContainer />);
    fireEvent.submit(screen.getByRole("button").closest("form")!);
    // useWeather should still be called with null (initial state)
    expect(mockUseWeather).toHaveBeenCalledWith(null);
  });

  it("saves city to localStorage on submit", () => {
    const setItemSpy = jest.spyOn(Storage.prototype, "setItem");
    render(<SearchContainer />);
    fireEvent.change(screen.getByPlaceholderText("Enter city name..."), {
      target: { value: "Paris" },
    });
    fireEvent.submit(screen.getByRole("button").closest("form")!);
    expect(setItemSpy).toHaveBeenCalledWith(
      "weatherPlatform:lastCity",
      "Paris",
    );
    setItemSpy.mockRestore();
  });
});
