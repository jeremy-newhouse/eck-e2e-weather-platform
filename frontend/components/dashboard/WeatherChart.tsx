"use client";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { ChartData } from "@/lib/types";

interface WeatherChartProps {
  data: ChartData[];
}

function formatBucket(bucket: string): string {
  return new Date(bucket).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function WeatherChart({ data }: WeatherChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="bucket" tickFormatter={formatBucket} />
        <YAxis
          yAxisId="temp"
          label={{ value: "°C", angle: -90, position: "insideLeft" }}
        />
        <YAxis
          yAxisId="other"
          orientation="right"
          label={{ value: "% / m/s", angle: 90, position: "insideRight" }}
        />
        <Tooltip
          labelFormatter={(label) => new Date(label as string).toLocaleString()}
          formatter={(value: number, name: string) => {
            if (name === "temperature")
              return [`${value.toFixed(1)}°C`, "Temperature"];
            if (name === "humidity")
              return [`${value.toFixed(0)}%`, "Humidity"];
            if (name === "wind_speed")
              return [`${value.toFixed(1)} m/s`, "Wind Speed"];
            return [value, name];
          }}
        />
        <Legend />
        <Line
          yAxisId="temp"
          type="monotone"
          dataKey="temperature"
          stroke="#3b82f6"
          name="temperature"
          dot={false}
        />
        <Line
          yAxisId="other"
          type="monotone"
          dataKey="humidity"
          stroke="#10b981"
          name="humidity"
          dot={false}
        />
        <Line
          yAxisId="other"
          type="monotone"
          dataKey="wind_speed"
          stroke="#f59e0b"
          name="wind_speed"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
