import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ChatContainer from "@/components/chat/ChatContainer";

// jsdom does not implement scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn();

const mockMutateAsync = jest.fn();

jest.mock("@/hooks/useChat", () => ({
  useChat: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  }),
}));

describe("ChatContainer", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it("shows greeting message on mount", () => {
    render(<ChatContainer />);
    expect(
      screen.getByText("Hello! Ask me anything about the weather."),
    ).toBeInTheDocument();
  });

  it("sends message and shows response", async () => {
    mockMutateAsync.mockResolvedValue({
      session_id: "session-abc",
      role: "assistant",
      content: "It is 20°C in London.",
      created_at: "2026-03-25T12:00:00.000Z",
    });

    render(<ChatContainer />);
    const input = screen.getByPlaceholderText("Ask about the weather...");
    await userEvent.type(input, "London weather");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => {
      expect(screen.getByText("London weather")).toBeInTheDocument();
      expect(screen.getByText("It is 20°C in London.")).toBeInTheDocument();
    });
  });

  it("stores session ID in localStorage on first response", async () => {
    mockMutateAsync.mockResolvedValue({
      session_id: "new-session-id",
      role: "assistant",
      content: "The weather is nice.",
      created_at: "2026-03-25T12:00:00.000Z",
    });

    const setItemSpy = jest.spyOn(Storage.prototype, "setItem");
    render(<ChatContainer />);
    const input = screen.getByPlaceholderText("Ask about the weather...");
    await userEvent.type(input, "Hello");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => {
      expect(setItemSpy).toHaveBeenCalledWith(
        "chatSessionId",
        "new-session-id",
      );
    });

    setItemSpy.mockRestore();
  });

  it("shows error message when mutation fails", async () => {
    mockMutateAsync.mockRejectedValue(new Error("Chat service unavailable"));

    render(<ChatContainer />);
    const input = screen.getByPlaceholderText("Ask about the weather...");
    await userEvent.type(input, "What is the weather?");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    await waitFor(() => {
      expect(
        screen.getByText(
          "Sorry, I could not connect to the weather assistant. Please try again.",
        ),
      ).toBeInTheDocument();
    });
  });
});
