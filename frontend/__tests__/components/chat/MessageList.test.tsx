import { render, screen } from "@testing-library/react";
import MessageList from "@/components/chat/MessageList";

// jsdom does not implement scrollIntoView
window.HTMLElement.prototype.scrollIntoView = jest.fn();

const messages = [
  { role: "user" as const, content: "What is the weather in London?" },
  { role: "assistant" as const, content: "It is sunny in London today." },
];

describe("MessageList", () => {
  it("renders all messages", () => {
    render(<MessageList messages={messages} />);
    expect(
      screen.getByText("What is the weather in London?"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("It is sunny in London today."),
    ).toBeInTheDocument();
  });

  it("user messages have correct styling class", () => {
    render(<MessageList messages={messages} />);
    const userBubble = screen
      .getByText("What is the weather in London?")
      .closest("div");
    expect(userBubble).toHaveClass("bg-blue-600");
  });

  it("assistant messages have correct styling class", () => {
    render(<MessageList messages={messages} />);
    const assistantBubble = screen
      .getByText("It is sunny in London today.")
      .closest("div");
    expect(assistantBubble).toHaveClass("bg-gray-100");
  });
});
