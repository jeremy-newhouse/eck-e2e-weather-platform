import { renderHook, act, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement } from "react";
import type { ReactNode } from "react";
import { useChat } from "@/hooks/useChat";
import * as api from "@/lib/api";
import type { ChatResponse } from "@/lib/types";

jest.mock("@/lib/api");

const mockChatResponse: ChatResponse = {
  session_id: "sess-abc123",
  role: "assistant",
  content: "The weather is sunny today.",
  created_at: "2026-03-25T12:00:00Z",
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

describe("useChat", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("starts in idle state", () => {
    const { result } = renderHook(() => useChat(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isPending).toBe(false);
    expect(result.current.isIdle).toBe(true);
    expect(result.current.data).toBeUndefined();
  });

  it("calls sendChat mutation and returns response on success", async () => {
    const sendChatMock = jest
      .spyOn(api, "sendChat")
      .mockResolvedValueOnce(mockChatResponse);

    const { result } = renderHook(() => useChat(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({
        message: "What's the weather?",
        city: "London",
      });
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(sendChatMock).toHaveBeenCalledWith({
      message: "What's the weather?",
      city: "London",
    });
    expect(result.current.data).toEqual(mockChatResponse);
  });

  it("returns error on API failure", async () => {
    jest
      .spyOn(api, "sendChat")
      .mockRejectedValueOnce(new Error("Chat service unavailable"));

    const { result } = renderHook(() => useChat(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      try {
        await result.current.mutateAsync({ message: "Hello" });
      } catch {
        // expected to throw
      }
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.error).toBeInstanceOf(Error);
    expect((result.current.error as Error).message).toBe(
      "Chat service unavailable",
    );
  });

  it("sends chat request without optional fields", async () => {
    const sendChatMock = jest
      .spyOn(api, "sendChat")
      .mockResolvedValueOnce(mockChatResponse);

    const { result } = renderHook(() => useChat(), {
      wrapper: createWrapper(),
    });

    await act(async () => {
      await result.current.mutateAsync({ message: "Hello" });
    });

    expect(sendChatMock).toHaveBeenCalledWith({ message: "Hello" });
  });
});
