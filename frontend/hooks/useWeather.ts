"use client";
import { useQuery } from "@tanstack/react-query";
import { getWeather } from "@/lib/api";

export function useWeather(city: string | null) {
  return useQuery({
    queryKey: ["weather", city],
    queryFn: () => getWeather(city!),
    enabled: !!city,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}
