"use client";
import { useState } from "react";
import { useWeather } from "@/hooks/useWeather";
import WeatherCard from "./WeatherCard";

export default function SearchContainer() {
  const [inputValue, setInputValue] = useState("");
  const [city, setCity] = useState<string | null>(null);
  const { data, isLoading, isError, error } = useWeather(city);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      setCity(inputValue.trim());
      if (typeof window !== "undefined" && inputValue.trim()) {
        localStorage.setItem("weatherPlatform:lastCity", inputValue.trim());
      }
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="flex gap-3 mb-6">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter city name..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {isLoading ? "Searching..." : "Search"}
        </button>
      </form>

      {isError && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error?.message === "City not found"
            ? "City not found. Try another name."
            : "Weather service unavailable."}
        </div>
      )}

      {data && <WeatherCard weather={data} />}
    </div>
  );
}
