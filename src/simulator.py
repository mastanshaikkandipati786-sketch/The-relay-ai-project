
import time
import random
import threading


class StandInSimulator:

    def __init__(
        self,
        base_delay=1.0,
        failure_rate=0.05,
        rate_limit=10,
        slow_load_threshold=5
    ):
        self.base_delay = base_delay
        self.failure_rate = failure_rate
        self.rate_limit = rate_limit
        self.slow_load_threshold = slow_load_threshold

        self.request_times = []
        self.active_requests = 0
        self.lock = threading.Lock()

    def process_request(self, prompt, stream=False, on_chunk=None):
        start = time.perf_counter()

        with self.lock:
            now = time.time()

            self.request_times = [
                t for t in self.request_times
                if now - t < 60
            ]

            if len(self.request_times) >= self.rate_limit:
                return {
                    "status": "rate_limited",
                    "message": "429: Rate limit exceeded",
                    "latency_ms": round(
                        (time.perf_counter() - start) * 1000, 2
                    )
                }

            self.request_times.append(now)
            self.active_requests += 1
            current_load = self.active_requests

        try:
            delay = self.base_delay

            if current_load > self.slow_load_threshold:
                delay *= 1 + (
                    current_load - self.slow_load_threshold
                )

            time.sleep(delay)

            if random.random() < self.failure_rate:
                return {
                    "status": "error",
                    "message": "Simulated service failure",
                    "latency_ms": round(
                        (time.perf_counter() - start) * 1000, 2
                    )
                }

            response_text = (
                "This is a simulated response from the stand-in service. "
                "It imitates a hosted language model response."
            )

            if stream:
                chunks = response_text.split()
                collected = []

                for chunk in chunks:
                    collected.append(chunk)

                    if on_chunk is not None:
                        on_chunk(chunk)

                    time.sleep(0.05)

                response_text = " ".join(collected)

            return {
                "status": "ok",
                "response": response_text,
                "latency_ms": round(
                    (time.perf_counter() - start) * 1000, 2
                )
            }

        finally:
            with self.lock:
                self.active_requests -= 1


if __name__ == "__main__":
    simulator = StandInSimulator()

    first_token_time = None
    start = time.perf_counter()

    def receive_chunk(chunk):
        global first_token_time

        if first_token_time is None:
            first_token_time = (
                time.perf_counter() - start
            ) * 1000

        print(chunk, end=" ", flush=True)

    print("Testing stand-in streaming...\n")

    result = simulator.process_request(
        "Explain attention",
        stream=True,
        on_chunk=receive_chunk
    )

    print("\n\nResult:", result["status"])
    print("First token latency:", round(first_token_time, 2), "ms")
    print("Total latency:", result["latency_ms"], "ms")
