"""Load testing script for chat endpoint.

Tests performance under concurrent load (100 requests).
Target: p95 response time < 3000ms

Usage:
    python tests/load_test.py
"""

import asyncio
import time
from typing import List
import httpx
import statistics


async def send_chat_request(client: httpx.AsyncClient, user_id: str, token: str) -> float:
    """Send a single chat request and return response time in ms."""
    start_time = time.time()

    try:
        response = await client.post(
            f"/api/{user_id}/chat",
            json={"message": "List my tasks"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )
        duration_ms = (time.time() - start_time) * 1000
        return duration_ms if response.status_code == 200 else -1
    except Exception as e:
        print(f"Request failed: {e}")
        return -1


async def run_load_test(
    base_url: str, user_id: str, token: str, num_requests: int = 100
):
    """Run load test with concurrent requests."""
    print(f"Starting load test: {num_requests} concurrent requests")
    print(f"Target: p95 < 3000ms, p99 < 5000ms")
    print("-" * 60)

    async with httpx.AsyncClient(base_url=base_url) as client:
        # Send concurrent requests
        tasks = [
            send_chat_request(client, user_id, token) for _ in range(num_requests)
        ]
        response_times = await asyncio.gather(*tasks)

        # Filter out failures
        successful_times = [t for t in response_times if t > 0]
        failed_count = len(response_times) - len(successful_times)

        if not successful_times:
            print("ERROR: All requests failed!")
            return

        # Calculate statistics
        avg_time = statistics.mean(successful_times)
        median_time = statistics.median(successful_times)
        min_time = min(successful_times)
        max_time = max(successful_times)

        # Calculate percentiles
        sorted_times = sorted(successful_times)
        p50 = sorted_times[int(len(sorted_times) * 0.50)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]

        # Print results
        print(f"\n{'Load Test Results':^60}")
        print("=" * 60)
        print(f"Total Requests:     {num_requests}")
        print(f"Successful:         {len(successful_times)} ({len(successful_times)/num_requests*100:.1f}%)")
        print(f"Failed:             {failed_count}")
        print()
        print(f"Response Times (ms):")
        print(f"  Min:              {min_time:.2f}")
        print(f"  p50 (Median):     {p50:.2f}")
        print(f"  p95:              {p95:.2f} {'✓ PASS' if p95 < 3000 else '✗ FAIL'}")
        print(f"  p99:              {p99:.2f}")
        print(f"  Max:              {max_time:.2f}")
        print(f"  Avg:              {avg_time:.2f}")
        print()

        # Performance verdict
        if p95 < 3000:
            print("✅ Performance target met (p95 < 3000ms)")
        else:
            print(f"⚠️  Performance target missed (p95: {p95:.2f}ms > 3000ms)")


if __name__ == "__main__":
    # Configuration (update these values)
    BASE_URL = "http://localhost:8000"
    USER_ID = "test-user-123"  # Replace with actual test user
    TOKEN = "your-jwt-token-here"  # Replace with actual JWT token

    print("\n" + "=" * 60)
    print(" Chat Endpoint Load Test ".center(60, "="))
    print("=" * 60 + "\n")

    asyncio.run(run_load_test(BASE_URL, USER_ID, TOKEN, num_requests=100))
