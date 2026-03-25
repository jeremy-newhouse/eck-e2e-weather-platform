"use client";
import { useState, useEffect } from "react";
import { useMetrics } from "@/hooks/useMetrics";
import { pivotMetrics } from "@/lib/utils";
import RangeSelector from "./RangeSelector";
import WeatherChart from "./WeatherChart";
import type { MetricRange } from "@/lib/types";
import Link from "next/link";

export default function DashboardContent() {
  const [selectedRange, setSelectedRange] = useState<MetricRange>("1h");
  const [city, setCity] = useState<string | null>(null);

  useEffect(() => {
    const lastCity = localStorage.getItem("weatherPlatform:lastCity");
    if (lastCity) setCity(lastCity);
  }, []);

  const { data, isLoading, isError } = useMetrics(city, selectedRange);

  if (!city) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">
          Search for a city on the home page first.
        </p>
        <Link href="/" className="text-blue-600 hover:underline">
          Go to Home
        </Link>
      </div>
    );
  }

  const chartData = data ? pivotMetrics(data.metrics) : [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Weather Metrics — {city}
        </h1>
        <RangeSelector selected={selectedRange} onSelect={setSelectedRange} />
      </div>

      {isLoading && (
        <div className="h-96 bg-gray-100 rounded-xl animate-pulse flex items-center justify-center">
          <span className="text-gray-400">Loading metrics...</span>
        </div>
      )}

      {isError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          Failed to load metrics. Please try again.
        </div>
      )}

      {!isLoading && !isError && chartData.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No metrics data yet for {city}. Search for the city first to generate
          data.
        </div>
      )}

      {!isLoading && !isError && chartData.length > 0 && (
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <WeatherChart data={chartData} />
        </div>
      )}
    </div>
  );
}
