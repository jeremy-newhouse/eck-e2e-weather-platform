import { render, screen, fireEvent } from "@testing-library/react";
import ChatInput from "@/components/chat/ChatInput";

const mockOnSend = jest.fn();

describe("ChatInput", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders input and send button", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);
    expect(
      screen.getByPlaceholderText("Ask about the weather..."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
  });

  it("send button disabled when loading=true", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={true} />);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("send button disabled when input is empty", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("onSend called with trimmed message on submit", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);
    const input = screen.getByPlaceholderText("Ask about the weather...");
    fireEvent.change(input, { target: { value: "  What is the weather?  " } });
    fireEvent.submit(screen.getByRole("button").closest("form")!);
    expect(mockOnSend).toHaveBeenCalledWith("What is the weather?");
  });

  it("input cleared after submit", () => {
    render(<ChatInput onSend={mockOnSend} isLoading={false} />);
    const input = screen.getByPlaceholderText("Ask about the weather...");
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.submit(screen.getByRole("button").closest("form")!);
    expect(input).toHaveValue("");
  });
});
