import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RangeSelector from "@/components/dashboard/RangeSelector";
import type { MetricRange } from "@/lib/types";

describe("RangeSelector", () => {
  const defaultProps = {
    selected: "1h" as MetricRange,
    onSelect: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders 4 range buttons", () => {
    render(<RangeSelector {...defaultProps} />);
    expect(screen.getByRole("button", { name: "1h" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "6h" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "24h" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "7d" })).toBeInTheDocument();
  });

  it("calls onSelect with the correct range when a button is clicked", async () => {
    const user = userEvent.setup();
    render(<RangeSelector {...defaultProps} />);

    await user.click(screen.getByRole("button", { name: "6h" }));
    expect(defaultProps.onSelect).toHaveBeenCalledWith("6h");

    await user.click(screen.getByRole("button", { name: "7d" }));
    expect(defaultProps.onSelect).toHaveBeenCalledWith("7d");
  });

  it("highlights the selected range button", () => {
    render(<RangeSelector selected="24h" onSelect={jest.fn()} />);
    const selectedButton = screen.getByRole("button", { name: "24h" });
    const unselectedButton = screen.getByRole("button", { name: "1h" });

    expect(selectedButton.className).toContain("bg-blue-600");
    expect(selectedButton.className).toContain("text-white");
    expect(unselectedButton.className).toContain("bg-gray-100");
    expect(unselectedButton.className).toContain("text-gray-700");
  });
});
