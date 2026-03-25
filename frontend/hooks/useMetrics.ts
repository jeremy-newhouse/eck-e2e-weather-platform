"use client";
import { useQuery } from "@tanstack/react-query";
import { getMetrics } from "@/lib/api";
import type { MetricRange } from "@/lib/types";

export function useMetrics(city: string | null, range: MetricRange) {
  return useQuery({
    queryKey: ["metrics", city, range],
    queryFn: () => getMetrics(city!, range),
    enabled: !!city,
    staleTime: 60 * 1000,
    retry: false,
  });
}
