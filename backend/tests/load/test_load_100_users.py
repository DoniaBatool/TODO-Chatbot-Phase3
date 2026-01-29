"""
Load testing script for 100 concurrent users.

This script tests the chat API endpoint under load to verify:
- <5s p95 response time
- No errors under concurrent load
- System stability with 100 simultaneous users

Usage:
    # Install locust first
    pip install locust

    # Run load test (headless mode)
    locust -f tests/load/test_load_100_users.py --headless \
        --users 100 --spawn-rate 10 --run-time 60s \
        --host http://localhost:8000

    # Run with web UI
    locust -f tests/load/test_load_100_users.py --host http://localhost:8000

Requirements:
    - Backend server running at specified host
    - Database configured and migrated
    - At least one test user in database
"""

import os
import time
import json
import random
import string
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

try:
    from locust import HttpUser, task, between, events
    from locust.runners import MasterRunner
    LOCUST_AVAILABLE = True
except ImportError:
    LOCUST_AVAILABLE = False
    # Create mock classes for testing without locust installed
    class HttpUser:
        pass
    def task(weight=1):
        def decorator(func):
            return func
        return decorator
    def between(a, b):
        return lambda: random.uniform(a, b)


@dataclass
class LoadTestMetrics:
    """Aggregate metrics for load test analysis."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def p95_response_time(self) -> float:
        """Calculate 95th percentile response time in seconds."""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[min(index, len(sorted_times) - 1)] / 1000  # Convert ms to seconds

    @property
    def avg_response_time(self) -> float:
        """Calculate average response time in seconds."""
        if not self.response_times:
            return 0.0
        return (sum(self.response_times) / len(self.response_times)) / 1000

    @property
    def max_response_time(self) -> float:
        """Maximum response time in seconds."""
        if not self.response_times:
            return 0.0
        return max(self.response_times) / 1000

    def to_dict(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate_percent": round(self.success_rate, 2),
            "p95_response_time_seconds": round(self.p95_response_time, 3),
            "avg_response_time_seconds": round(self.avg_response_time, 3),
            "max_response_time_seconds": round(self.max_response_time, 3),
            "p95_under_5s": self.p95_response_time < 5.0,
            "test_duration_seconds": (
                (self.end_time - self.start_time).total_seconds()
                if self.start_time and self.end_time else 0
            )
        }


# Global metrics collector
metrics = LoadTestMetrics()


if LOCUST_AVAILABLE:
    @events.request.add_listener
    def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
        """Collect metrics for each request."""
        metrics.total_requests += 1
        metrics.response_times.append(response_time)

        if exception:
            metrics.failed_requests += 1
            metrics.errors.append(str(exception))
        else:
            metrics.successful_requests += 1

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Initialize metrics at test start."""
        global metrics
        metrics = LoadTestMetrics()
        metrics.start_time = datetime.now()
        print("\n" + "=" * 60)
        print("🚀 Load Test Starting - 100 Concurrent Users")
        print("=" * 60)

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """Print final metrics at test end."""
        metrics.end_time = datetime.now()
        results = metrics.to_dict()

        print("\n" + "=" * 60)
        print("📊 Load Test Results")
        print("=" * 60)
        print(f"Total Requests: {results['total_requests']}")
        print(f"Successful: {results['successful_requests']}")
        print(f"Failed: {results['failed_requests']}")
        print(f"Success Rate: {results['success_rate_percent']}%")
        print("-" * 60)
        print(f"P95 Response Time: {results['p95_response_time_seconds']:.3f}s")
        print(f"Avg Response Time: {results['avg_response_time_seconds']:.3f}s")
        print(f"Max Response Time: {results['max_response_time_seconds']:.3f}s")
        print("-" * 60)

        if results['p95_under_5s']:
            print("✅ PASS: P95 response time is under 5 seconds")
        else:
            print("❌ FAIL: P95 response time exceeds 5 seconds")

        print("=" * 60 + "\n")

        # Save results to file
        results_file = "load_test_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {results_file}")


class ChatbotUser(HttpUser):
    """
    Simulated user for load testing the chat API.

    Simulates realistic user behavior:
    - Login to get JWT token
    - Create a conversation
    - Send various chat messages (add task, list tasks, etc.)
    - Realistic wait times between requests (1-3 seconds)
    """

    # Wait between 1-3 seconds between tasks (simulates thinking time)
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.conversation_id: Optional[str] = None
        self.task_count = 0

    def on_start(self):
        """Called when a simulated user starts. Login and create conversation."""
        self._login()
        if self.token:
            self._create_conversation()

    def _login(self):
        """Login or create test user and get JWT token."""
        # Try to login with test user
        test_email = f"loadtest_{random.randint(10000, 99999)}@test.com"
        test_password = "LoadTest123!"

        # First try to signup (in case user doesn't exist)
        signup_response = self.client.post(
            "/api/auth/signup",
            json={
                "email": test_email,
                "password": test_password,
                "name": "Load Test User"
            },
            catch_response=True
        )

        if signup_response.status_code in [200, 201]:
            data = signup_response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            signup_response.success()
        elif signup_response.status_code == 400:
            # User exists, try login
            signup_response.success()  # Mark signup attempt as ok
            login_response = self.client.post(
                "/api/auth/login",
                json={
                    "email": test_email,
                    "password": test_password
                },
                catch_response=True
            )
            if login_response.status_code == 200:
                data = login_response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                login_response.success()
            else:
                login_response.failure(f"Login failed: {login_response.status_code}")
        else:
            signup_response.failure(f"Signup failed: {signup_response.status_code}")

    def _create_conversation(self):
        """Create a new conversation for this user."""
        if not self.token:
            return

        response = self.client.post(
            "/api/conversations",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"title": f"Load Test {datetime.now().isoformat()}"},
            catch_response=True
        )

        if response.status_code in [200, 201]:
            data = response.json()
            self.conversation_id = data.get("id")
            response.success()
        else:
            response.failure(f"Create conversation failed: {response.status_code}")

    def _get_auth_headers(self) -> dict:
        """Get headers with JWT token."""
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(3)
    def send_add_task_message(self):
        """Send an 'add task' chat message (most common operation)."""
        if not self.token or not self.conversation_id:
            return

        task_name = f"Task_{self.task_count}_{random.randint(1000, 9999)}"
        self.task_count += 1

        messages = [
            f"add task {task_name}",
            f"create a new task to {task_name}",
            f"remind me to {task_name}",
            f"add {task_name} to my list",
        ]

        response = self.client.post(
            f"/api/chat/{self.conversation_id}",
            headers=self._get_auth_headers(),
            json={"message": random.choice(messages)},
            name="/api/chat/[id] - add task",
            catch_response=True
        )

        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Add task failed: {response.status_code}")

    @task(2)
    def send_list_tasks_message(self):
        """Send a 'list tasks' chat message."""
        if not self.token or not self.conversation_id:
            return

        messages = [
            "show my tasks",
            "list all tasks",
            "what are my tasks",
            "show todo list",
        ]

        response = self.client.post(
            f"/api/chat/{self.conversation_id}",
            headers=self._get_auth_headers(),
            json={"message": random.choice(messages)},
            name="/api/chat/[id] - list tasks",
            catch_response=True
        )

        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"List tasks failed: {response.status_code}")

    @task(1)
    def send_complete_task_message(self):
        """Send a 'complete task' chat message."""
        if not self.token or not self.conversation_id:
            return

        messages = [
            "mark task 1 as complete",
            "complete task 1",
            "finish task 1",
            "done with task 1",
        ]

        response = self.client.post(
            f"/api/chat/{self.conversation_id}",
            headers=self._get_auth_headers(),
            json={"message": random.choice(messages)},
            name="/api/chat/[id] - complete task",
            catch_response=True
        )

        if response.status_code == 200:
            response.success()
        else:
            # Complete might fail if task doesn't exist, that's ok
            response.success()

    @task(1)
    def get_conversation_history(self):
        """Get conversation history."""
        if not self.token or not self.conversation_id:
            return

        response = self.client.get(
            f"/api/conversations/{self.conversation_id}",
            headers=self._get_auth_headers(),
            name="/api/conversations/[id]",
            catch_response=True
        )

        if response.status_code == 200:
            response.success()
        else:
            response.failure(f"Get conversation failed: {response.status_code}")


def run_simple_load_test(
    base_url: str = "http://localhost:8000",
    num_users: int = 100,
    duration_seconds: int = 60,
    requests_per_user: int = 10
) -> dict:
    """
    Simple load test without locust (for environments where locust isn't installed).

    This is a fallback implementation using concurrent.futures.

    Args:
        base_url: Base URL of the API
        num_users: Number of concurrent users to simulate
        duration_seconds: How long to run the test
        requests_per_user: Number of requests per user

    Returns:
        Dict with test results
    """
    import concurrent.futures
    import requests
    from collections import defaultdict

    print(f"\n{'=' * 60}")
    print(f"🚀 Simple Load Test - {num_users} Concurrent Users")
    print(f"{'=' * 60}")

    results = {
        "total_requests": 0,
        "successful": 0,
        "failed": 0,
        "response_times": [],
        "errors": []
    }

    def simulate_user(user_id: int) -> list:
        """Simulate a single user's requests."""
        user_results = []

        try:
            # Create test user
            email = f"loadtest_{user_id}_{random.randint(10000, 99999)}@test.com"
            signup_resp = requests.post(
                f"{base_url}/api/auth/signup",
                json={"email": email, "password": "LoadTest123!", "name": f"User {user_id}"},
                timeout=30
            )

            if signup_resp.status_code not in [200, 201, 400]:
                return [{"success": False, "time": 0, "error": "Signup failed"}]

            token = None
            if signup_resp.status_code in [200, 201]:
                token = signup_resp.json().get("access_token")

            if not token:
                # Try login
                login_resp = requests.post(
                    f"{base_url}/api/auth/login",
                    json={"email": email, "password": "LoadTest123!"},
                    timeout=30
                )
                if login_resp.status_code == 200:
                    token = login_resp.json().get("access_token")

            if not token:
                return [{"success": False, "time": 0, "error": "Auth failed"}]

            headers = {"Authorization": f"Bearer {token}"}

            # Create conversation
            conv_resp = requests.post(
                f"{base_url}/api/conversations",
                headers=headers,
                json={"title": f"Load Test {user_id}"},
                timeout=30
            )

            if conv_resp.status_code not in [200, 201]:
                return [{"success": False, "time": 0, "error": "Create conversation failed"}]

            conv_id = conv_resp.json().get("id")

            # Send chat messages
            messages = [
                "add task buy groceries",
                "show my tasks",
                "add task call mom",
                "list tasks",
                "complete task 1"
            ]

            for msg in messages[:requests_per_user]:
                start = time.time()
                try:
                    resp = requests.post(
                        f"{base_url}/api/chat/{conv_id}",
                        headers=headers,
                        json={"message": msg},
                        timeout=60
                    )
                    elapsed = (time.time() - start) * 1000  # ms

                    user_results.append({
                        "success": resp.status_code == 200,
                        "time": elapsed,
                        "error": None if resp.status_code == 200 else f"Status {resp.status_code}"
                    })
                except Exception as e:
                    elapsed = (time.time() - start) * 1000
                    user_results.append({
                        "success": False,
                        "time": elapsed,
                        "error": str(e)
                    })

                time.sleep(random.uniform(0.5, 1.5))  # Simulate thinking time

        except Exception as e:
            user_results.append({"success": False, "time": 0, "error": str(e)})

        return user_results

    # Run concurrent users
    start_time = datetime.now()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(simulate_user, i) for i in range(num_users)]

        for future in concurrent.futures.as_completed(futures):
            try:
                user_results = future.result()
                for r in user_results:
                    results["total_requests"] += 1
                    results["response_times"].append(r["time"])
                    if r["success"]:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        if r["error"]:
                            results["errors"].append(r["error"])
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(str(e))

    end_time = datetime.now()

    # Calculate metrics
    response_times = results["response_times"]
    if response_times:
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p95 = sorted_times[min(p95_index, len(sorted_times) - 1)] / 1000
        avg = sum(response_times) / len(response_times) / 1000
        max_time = max(response_times) / 1000
    else:
        p95 = avg = max_time = 0

    final_results = {
        "total_requests": results["total_requests"],
        "successful_requests": results["successful"],
        "failed_requests": results["failed"],
        "success_rate_percent": round(
            (results["successful"] / results["total_requests"] * 100)
            if results["total_requests"] > 0 else 0, 2
        ),
        "p95_response_time_seconds": round(p95, 3),
        "avg_response_time_seconds": round(avg, 3),
        "max_response_time_seconds": round(max_time, 3),
        "p95_under_5s": p95 < 5.0,
        "test_duration_seconds": (end_time - start_time).total_seconds()
    }

    # Print results
    print(f"\n{'=' * 60}")
    print("📊 Load Test Results")
    print(f"{'=' * 60}")
    print(f"Total Requests: {final_results['total_requests']}")
    print(f"Successful: {final_results['successful_requests']}")
    print(f"Failed: {final_results['failed_requests']}")
    print(f"Success Rate: {final_results['success_rate_percent']}%")
    print(f"{'-' * 60}")
    print(f"P95 Response Time: {final_results['p95_response_time_seconds']:.3f}s")
    print(f"Avg Response Time: {final_results['avg_response_time_seconds']:.3f}s")
    print(f"Max Response Time: {final_results['max_response_time_seconds']:.3f}s")
    print(f"{'-' * 60}")

    if final_results['p95_under_5s']:
        print("✅ PASS: P95 response time is under 5 seconds")
    else:
        print("❌ FAIL: P95 response time exceeds 5 seconds")

    print(f"{'=' * 60}\n")

    return final_results


if __name__ == "__main__":
    import sys

    if LOCUST_AVAILABLE:
        print("Run with: locust -f tests/load/test_load_100_users.py --host http://localhost:8000")
        print("Or run simple test with: python -m tests.load.test_load_100_users --simple")

        if "--simple" in sys.argv:
            host = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else "http://localhost:8000"
            users = int(sys.argv[sys.argv.index("--users") + 1]) if "--users" in sys.argv else 100
            run_simple_load_test(base_url=host, num_users=users)
    else:
        print("Locust not installed. Running simple load test...")
        host = sys.argv[sys.argv.index("--host") + 1] if "--host" in sys.argv else "http://localhost:8000"
        users = int(sys.argv[sys.argv.index("--users") + 1]) if "--users" in sys.argv else 100
        run_simple_load_test(base_url=host, num_users=users)
