
import csv
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "results" / "results.csv"

with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

print("\n========== CSV VALIDATION ==========")
print("Total data rows:", len(rows))
print("Total columns:", len(reader.fieldnames))
print("Column names:", reader.fieldnames)

for source in ["stand-in", "real"]:
    source_rows = [r for r in rows if r["source"] == source]

    print(f"\n========== {source.upper()} RESULTS ==========")
    print("Total requests:", len(source_rows))

    statuses = Counter(r["status"] for r in source_rows)
    for status, count in statuses.items():
        print(status, ":", count)

    successful = [
        float(r["total_ms"])
        for r in source_rows
        if r["status"] == "ok" and r["total_ms"]
    ]

    if successful:
        successful.sort()

        def percentile(values, p):
            position = (len(values) - 1) * p
            lower = int(position)
            upper = min(lower + 1, len(values) - 1)
            fraction = position - lower
            return values[lower] + (
                values[upper] - values[lower]
            ) * fraction

        print("Successful requests:", len(successful))
        print("Average latency:", round(sum(successful) / len(successful), 2), "ms")
        print("p50:", round(percentile(successful, 0.50), 2), "ms")
        print("p95:", round(percentile(successful, 0.95), 2), "ms")
        print("p99:", round(percentile(successful, 0.99), 2), "ms")

    total = len(source_rows)

    if total:
        print("Success rate:", round(statuses["ok"] / total * 100, 2), "%")
        print("Rate-limit rate:", round(statuses["rate_limited"] / total * 100, 2), "%")
        print("Error rate:", round(statuses["error"] / total * 100, 2), "%")
        print("Timeout rate:", round(statuses["timeout"] / total * 100, 2), "%")

print("\n========== ANALYSIS COMPLETE ==========")
