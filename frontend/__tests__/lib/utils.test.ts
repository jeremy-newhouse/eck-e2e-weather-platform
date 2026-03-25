import { pivotMetrics } from "@/lib/utils";
import type { MetricBucket } from "@/lib/types";

describe("lib/utils", () => {
  describe("pivotMetrics", () => {
    it("returns an empty array for empty input", () => {
      expect(pivotMetrics([])).toEqual([]);
    });

    it("correctly groups metrics by bucket", () => {
      const metrics: MetricBucket[] = [
        {
          bucket: "2026-03-25T12:00:00Z",
          metric_name: "temperature",
          avg_value: 20.5,
        },
        {
          bucket: "2026-03-25T12:00:00Z",
          metric_name: "humidity",
          avg_value: 75,
        },
        {
          bucket: "2026-03-25T12:00:00Z",
          metric_name: "wind_speed",
          avg_value: 3.2,
        },
        {
          bucket: "2026-03-25T13:00:00Z",
          metric_name: "temperature",
          avg_value: 22.0,
        },
        {
          bucket: "2026-03-25T13:00:00Z",
          metric_name: "humidity",
          avg_value: 70,
        },
      ];

      const result = pivotMetrics(metrics);

      expect(result).toHaveLength(2);
      expect(result[0]).toEqual({
        bucket: "2026-03-25T12:00:00Z",
        temperature: 20.5,
        humidity: 75,
        wind_speed: 3.2,
      });
      expect(result[1]).toEqual({
        bucket: "2026-03-25T13:00:00Z",
        temperature: 22.0,
        humidity: 70,
      });
    });

    it("sorts results by bucket ascending", () => {
      const metrics: MetricBucket[] = [
        {
          bucket: "2026-03-25T13:00:00Z",
          metric_name: "temperature",
          avg_value: 22.0,
        },
        {
          bucket: "2026-03-25T11:00:00Z",
          metric_name: "temperature",
          avg_value: 18.0,
        },
        {
          bucket: "2026-03-25T12:00:00Z",
          metric_name: "temperature",
          avg_value: 20.0,
        },
      ];

      const result = pivotMetrics(metrics);

      expect(result[0].bucket).toBe("2026-03-25T11:00:00Z");
      expect(result[1].bucket).toBe("2026-03-25T12:00:00Z");
      expect(result[2].bucket).toBe("2026-03-25T13:00:00Z");
    });

    it("ignores unknown metric names", () => {
      const metrics: MetricBucket[] = [
        {
          bucket: "2026-03-25T12:00:00Z",
          metric_name: "pressure",
          avg_value: 1013,
        },
      ];

      const result = pivotMetrics(metrics);

      expect(result).toHaveLength(1);
      expect(result[0]).toEqual({ bucket: "2026-03-25T12:00:00Z" });
    });
  });
});
