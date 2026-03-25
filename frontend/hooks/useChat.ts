"use client";
import { useMutation } from "@tanstack/react-query";
import { sendChat } from "@/lib/api";
import type { ChatRequest } from "@/lib/types";

export function useChat() {
  return useMutation({
    mutationFn: (request: ChatRequest) => sendChat(request),
  });
}
