"use client";
import { useState, useEffect } from "react";
import { useChat } from "@/hooks/useChat";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const GREETING: Message = {
  role: "assistant",
  content: "Hello! Ask me anything about the weather.",
};

export default function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [city, setCity] = useState<string | undefined>(undefined);
  const chatMutation = useChat();

  useEffect(() => {
    const storedSession = localStorage.getItem("chatSessionId");
    if (storedSession) setSessionId(storedSession);
    const lastCity = localStorage.getItem("weatherPlatform:lastCity");
    if (lastCity) setCity(lastCity);
  }, []);

  const handleSend = async (message: string) => {
    setMessages((prev) => [...prev, { role: "user", content: message }]);

    try {
      const response = await chatMutation.mutateAsync({
        session_id: sessionId,
        message,
        city,
      });

      if (!sessionId && response.session_id) {
        setSessionId(response.session_id);
        localStorage.setItem("chatSessionId", response.session_id);
      }

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.content },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I could not connect to the weather assistant. Please try again.",
        },
      ]);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-180px)] max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-4">
        Weather Assistant
      </h1>
      <div className="flex-1 flex flex-col bg-white border border-gray-200 rounded-xl p-4 min-h-0">
        <MessageList messages={messages} />
        <ChatInput onSend={handleSend} isLoading={chatMutation.isPending} />
      </div>
    </div>
  );
}
