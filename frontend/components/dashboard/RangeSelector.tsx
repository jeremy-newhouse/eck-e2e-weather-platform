"use client";
import type { MetricRange } from "@/lib/types";

const RANGES: MetricRange[] = ["1h", "6h", "24h", "7d"];

interface RangeSelectorProps {
  selected: MetricRange;
  onSelect: (range: MetricRange) => void;
}

export default function RangeSelector({
  selected,
  onSelect,
}: RangeSelectorProps) {
  return (
    <div className="flex gap-2">
      {RANGES.map((range) => (
        <button
          key={range}
          onClick={() => onSelect(range)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            selected === range
              ? "bg-blue-600 text-white"
              : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
        >
          {range}
        </button>
      ))}
    </div>
  );
}
