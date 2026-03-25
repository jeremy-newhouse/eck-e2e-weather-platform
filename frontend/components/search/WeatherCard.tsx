"use client";
import Link from "next/link";
import type { WeatherData } from "@/lib/types";

interface WeatherCardProps {
  weather: WeatherData;
}

export default function WeatherCard({ weather }: WeatherCardProps) {
  return (
    <div className="p-6 bg-white border border-gray-200 rounded-xl shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">{weather.city}</h2>
        <span className="text-gray-500 text-sm">
          {new Date(weather.timestamp).toLocaleString()}
        </span>
      </div>
      <p className="text-gray-600 mb-4 capitalize">{weather.description}</p>
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {weather.temperature.toFixed(1)}°C
          </div>
          <div className="text-xs text-gray-500 mt-1">Temperature</div>
        </div>
        <div className="text-center p-3 bg-emerald-50 rounded-lg">
          <div className="text-2xl font-bold text-emerald-600">
            {weather.humidity.toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Humidity</div>
        </div>
        <div className="text-center p-3 bg-amber-50 rounded-lg">
          <div className="text-2xl font-bold text-amber-600">
            {weather.wind_speed.toFixed(1)} m/s
          </div>
          <div className="text-xs text-gray-500 mt-1">Wind Speed</div>
        </div>
      </div>
      <div className="flex gap-3">
        <Link
          href="/dashboard"
          className="flex-1 text-center py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
        >
          View Dashboard
        </Link>
        <Link
          href="/chat"
          className="flex-1 text-center py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
        >
          Ask the AI
        </Link>
      </div>
    </div>
  );
}
