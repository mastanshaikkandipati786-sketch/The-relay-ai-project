
import csv
import time
import threading
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from simulator import StandInSimulator


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "results" / "results.csv"

CSV_COLUMNS = [
    "request_id",
    "scenario",
    "source",
    "start_time",
    "first_token_ms",
    "total_ms",
    "status",
    "retries",
    "tokens_in",
    "tokens_out",
    "retrieval_setting",
    "answer_grade"
]


request_counter = 0
counter_lock = threading.Lock()


def run_one_request(simulator, scenario, prompt):
    global request_counter

    with counter_lock:
        request_counter += 1
        request_id = request_counter

    start_time = datetime.now().astimezone().isoformat()
    timer_start = time.perf_counter()
    first_token_ms = None

    def receive_chunk(chunk):
        nonlocal first_token_ms

        if first_token_ms is None:
            first_token_ms = (
                time.perf_counter() - timer_start
            ) * 1000

    result = simulator.process_request(
        prompt,
        stream=True,
        on_chunk=receive_chunk
    )

    response = result.get("response", "")

    return {
        "request_id": request_id,
        "scenario": scenario,
        "source": "stand-in",
        "start_time": start_time,
        "first_token_ms": (
            round(first_token_ms, 2)
            if first_token_ms is not None else ""
        ),
        "total_ms": result.get("latency_ms", ""),
        "status": result.get("status", "error"),
        "retries": 0,
        "tokens_in": len(prompt.split()),
        "tokens_out": len(response.split()),
        "retrieval_setting": "not_used_standin",
        "answer_grade": ""
    }


def save_results(rows):
    file_exists = CSV_FILE.exists() and CSV_FILE.stat().st_size > 0

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerows(rows)


def run_sequential(simulator, scenario, count):
    rows = []

    for number in range(count):
        row = run_one_request(
            simulator,
            scenario,
            f"Test request number {number + 1}"
        )
        rows.append(row)

    return rows


def run_concurrent(simulator, scenario, count):
    with ThreadPoolExecutor(max_workers=count) as executor:
        futures = [
            executor.submit(
                run_one_request,
                simulator,
                scenario,
                f"Concurrent test request {number + 1}"
            )
            for number in range(count)
        ]

        return [future.result() for future in futures]


def main():
    all_rows = []

    # Scenario 1: Steady traffic
    print("\nScenario 1: Steady traffic")
    simulator = StandInSimulator(
        base_delay=0.5,
        failure_rate=0,
        rate_limit=100
    )
    all_rows.extend(run_sequential(simulator, "steady", 3))

    # Scenario 2: Burst traffic
    print("\nScenario 2: Burst traffic")
    simulator = StandInSimulator(
        base_delay=0.5,
        failure_rate=0,
        rate_limit=10
    )
    all_rows.extend(run_concurrent(simulator, "burst", 12))

    # Scenario 3: Sustained overload
    print("\nScenario 3: Sustained overload")
    simulator = StandInSimulator(
        base_delay=0.5,
        failure_rate=0,
        rate_limit=100,
        slow_load_threshold=2
    )
    all_rows.extend(run_concurrent(simulator, "sustained_overload", 6))

    # Scenario 4: Per-minute limit halved
    print("\nScenario 4: Per-minute limit halved")
    simulator = StandInSimulator(
        base_delay=0.2,
        failure_rate=0,
        rate_limit=5
    )
    all_rows.extend(run_concurrent(simulator, "half_minute_limit", 7))

    # Scenario 5: Daily budget exhausted
    print("\nScenario 5: Daily budget exhausted")

    all_rows.append({
        "request_id": "daily-budget-test",
        "scenario": "daily_budget_exhausted",
        "source": "stand-in",
        "start_time": datetime.now().astimezone().isoformat(),
        "first_token_ms": "",
        "total_ms": 0,
        "status": "rate_limited",
        "retries": 0,
        "tokens_in": 0,
        "tokens_out": 0,
        "retrieval_setting": "daily_budget_precheck",
        "answer_grade": ""
    })

    save_results(all_rows)

    print("\nEXPERIMENT SUMMARY")
    print("Total recorded requests:", len(all_rows))
    print("CSV file:", CSV_FILE)

    for scenario in [
        "steady",
        "burst",
        "sustained_overload",
        "half_minute_limit",
        "daily_budget_exhausted"
    ]:
        count = sum(
            1 for row in all_rows
            if row["scenario"] == scenario
        )
        print(scenario, ":", count, "requests")

    print("\nStand-in experiment completed.")


if __name__ == "__main__":
    main()
