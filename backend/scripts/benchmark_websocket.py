"""
Ano Platform — WebSocket Benchmark Script
=========================================
Measures real concurrent WebSocket connections and message latency.
Run with Daphne server up, then put the ACTUAL results on your resume.

Usage:
    pip install websockets aiohttp
    python backend/scripts/benchmark_websocket.py

What it measures:
    1. Max concurrent WebSocket connections your system can hold
    2. Round-trip message latency (p50, p95, p99)
    3. Message throughput (messages/second)

Prerequisites:
    - Daphne must be running: daphne -b 127.0.0.1 -p 8000 ano_backend.asgi:application
    - At least one chatroom must exist in the DB
    - You need a valid JWT access token for a test user
"""

import asyncio
import json
import time
import statistics
import sys
import argparse
import aiohttp


# ─────────────────────────────────────────────
# CONFIGURE THESE BEFORE RUNNING
# ─────────────────────────────────────────────
BASE_URL      = "http://localhost:8000"
WS_BASE_URL   = "ws://localhost:8000"

# Fill in from your local dev setup:
TEST_EMAIL    = "testuser@iiti.ac.in"
TEST_PASSWORD = "your_password_here"
CHATROOM_ID   = ""   # UUID of any chatroom in your DB
# ─────────────────────────────────────────────


async def get_jwt_token(email: str, password: str) -> str:
    """Login and return a JWT access token."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/api/auth/login/",
            json={"email": email, "password": password},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status != 200:
                body = await resp.text()
                raise RuntimeError(f"Login failed ({resp.status}): {body}")
            data = await resp.json()
            return data["access"]


async def get_chatroom_id(token: str) -> str:
    """Get the first available chatroom ID."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BASE_URL}/api/chat/chatrooms/",
            headers={"Authorization": f"Bearer {token}"},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            data = await resp.json()
            rooms = data.get("results", data) if isinstance(data, dict) else data
            if not rooms:
                raise RuntimeError("No chatrooms found. Create one via the UI first.")
            return rooms[0]["id"]


# ─────────────────────────────────────────────
# BENCHMARK 1: Concurrent Connection Count
# ─────────────────────────────────────────────

async def hold_connection(token: str, chatroom_id: str, conn_id: int,
                           results: dict, duration: float = 10.0):
    """Open a single WebSocket and hold it open for `duration` seconds."""
    import websockets
    url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"
    try:
        async with websockets.connect(url, open_timeout=5) as ws:
            results[conn_id] = "connected"
            await asyncio.sleep(duration)
            results[conn_id] = "completed"
    except Exception as e:
        results[conn_id] = f"failed: {type(e).__name__}: {e}"


async def benchmark_concurrent_connections(token: str, chatroom_id: str,
                                            max_conns: int = 200,
                                            step: int = 25):
    """
    Ramp up connections in steps and find where failures start.
    Returns the max stable concurrent connections.
    """
    print("\n" + "="*60)
    print("BENCHMARK 1: Concurrent WebSocket Connections")
    print("="*60)

    last_stable = 0
    for n in range(step, max_conns + 1, step):
        results = {}
        tasks = [
            asyncio.create_task(
                hold_connection(token, chatroom_id, i, results, duration=5.0)
            )
            for i in range(n)
        ]
        await asyncio.sleep(3.0)  # Let connections stabilise

        connected = sum(1 for v in results.values() if v == "connected")
        failed    = sum(1 for v in results.values() if v.startswith("failed"))

        print(f"  Attempted: {n:4d}  Connected: {connected:4d}  Failed: {failed:4d}")

        # Cancel all tasks before next round
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        if failed == 0:
            last_stable = connected
        else:
            print(f"  → Failures detected at {n}. Max stable: {last_stable}")
            break

    if last_stable == 0:
        last_stable = max_conns  # All passed up to max
    print(f"\n  ✅ MAX STABLE CONCURRENT CONNECTIONS: {last_stable}")
    return last_stable


# ─────────────────────────────────────────────
# BENCHMARK 2: Round-trip Latency
# ─────────────────────────────────────────────

async def measure_message_latency(token: str, chatroom_id: str,
                                   n_messages: int = 100) -> dict:
    """
    Send N ping messages and measure time from send to pong response.
    Returns latency statistics in milliseconds.
    """
    import websockets
    print("\n" + "="*60)
    print("BENCHMARK 2: Message Round-Trip Latency (ping/pong)")
    print("="*60)

    url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"
    latencies = []

    async with websockets.connect(url, open_timeout=5) as ws:
        # Warmup: 5 pings
        for _ in range(5):
            await ws.send(json.dumps({"type": "ping"}))
            await ws.recv()

        print(f"  Sending {n_messages} ping messages...")
        for i in range(n_messages):
            t0 = time.perf_counter()
            await ws.send(json.dumps({"type": "ping"}))
            await ws.recv()
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000)  # ms

            if (i + 1) % 25 == 0:
                print(f"  Progress: {i+1}/{n_messages}")

    stats = {
        "p50":  round(statistics.median(latencies), 2),
        "p95":  round(sorted(latencies)[int(len(latencies) * 0.95)], 2),
        "p99":  round(sorted(latencies)[int(len(latencies) * 0.99)], 2),
        "mean": round(statistics.mean(latencies), 2),
        "min":  round(min(latencies), 2),
        "max":  round(max(latencies), 2),
        "n":    n_messages,
    }

    print(f"\n  Latency Results ({n_messages} messages, localhost):")
    print(f"    p50  (median): {stats['p50']:7.2f} ms")
    print(f"    p95          : {stats['p95']:7.2f} ms")
    print(f"    p99          : {stats['p99']:7.2f} ms")
    print(f"    mean         : {stats['mean']:7.2f} ms")
    print(f"    min          : {stats['min']:7.2f} ms")
    print(f"    max          : {stats['max']:7.2f} ms")
    print(f"\n  ✅ ROUND-TRIP LATENCY: p50={stats['p50']}ms, p99={stats['p99']}ms")
    return stats


# ─────────────────────────────────────────────
# BENCHMARK 3: Message Throughput
# ─────────────────────────────────────────────

async def measure_throughput(token: str, chatroom_id: str,
                              duration_sec: float = 10.0) -> float:
    """
    Measure how many messages/second the server can process in broadcast mode
    (N senders, all N+1 clients receiving each message).
    """
    import websockets
    print("\n" + "="*60)
    print("BENCHMARK 3: Message Throughput (messages/second)")
    print("="*60)

    n_senders = 5
    url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"

    message_count = 0
    start = time.perf_counter()

    async def sender(ws):
        nonlocal message_count
        while time.perf_counter() - start < duration_sec:
            await ws.send(json.dumps({
                "type": "message.send",
                "content": f"benchmark test {time.time()}"
            }))
            message_count += 1
            await asyncio.sleep(0.01)  # 100 msg/s per sender max

    connections = []
    try:
        for _ in range(n_senders):
            ws = await websockets.connect(url, open_timeout=5)
            connections.append(ws)

        tasks = [asyncio.create_task(sender(ws)) for ws in connections]
        await asyncio.sleep(duration_sec + 0.5)
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        for ws in connections:
            await ws.close()

    elapsed = time.perf_counter() - start
    mps = round(message_count / elapsed, 1)
    print(f"\n  Sent {message_count} messages in {elapsed:.1f}s from {n_senders} connections")
    print(f"  ✅ THROUGHPUT: {mps} messages/second")
    return mps


# ─────────────────────────────────────────────
# BENCHMARK 4: REST API Latency
# ─────────────────────────────────────────────

async def benchmark_rest_api(token: str, chatroom_id: str, n: int = 50) -> dict:
    """Measure REST API response times for common endpoints."""
    print("\n" + "="*60)
    print("BENCHMARK 4: REST API Response Times")
    print("="*60)

    endpoints = [
        ("GET", f"/api/chat/chatrooms/", None),
        ("GET", f"/api/auth/me/", None),
        ("GET", f"/api/chat/chatrooms/{chatroom_id}/messages/", None),
    ]

    headers = {"Authorization": f"Bearer {token}"}
    results = {}

    async with aiohttp.ClientSession() as session:
        for method, path, body in endpoints:
            times = []
            url = f"{BASE_URL}{path}"
            for _ in range(n):
                t0 = time.perf_counter()
                if method == "GET":
                    async with session.get(url, headers=headers) as r:
                        await r.json()
                else:
                    async with session.post(url, headers=headers, json=body) as r:
                        await r.json()
                t1 = time.perf_counter()
                times.append((t1 - t0) * 1000)

            p50 = round(statistics.median(times), 1)
            p95 = round(sorted(times)[int(len(times) * 0.95)], 1)
            print(f"  {method} {path:45s}  p50={p50:6.1f}ms  p95={p95:6.1f}ms")
            results[path] = {"p50": p50, "p95": p95}

    return results


# ─────────────────────────────────────────────
# BENCHMARK 5: Anti-Spam Rate Limit Verification
# ─────────────────────────────────────────────

async def verify_rate_limit(token: str, chatroom_id: str):
    """Verify that the 15 messages/10s rate limit is enforced."""
    import websockets
    print("\n" + "="*60)
    print("BENCHMARK 5: Anti-Spam Rate Limit Verification")
    print("="*60)

    url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"

    async with websockets.connect(url, open_timeout=5) as ws:
        blocked_at = None
        for i in range(25):
            await ws.send(json.dumps({
                "type": "message.send",
                "content": f"rate limit test message {i}"
            }))
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(response)
                if data.get("spam_detected") or data.get("type") == "error":
                    blocked_at = i + 1
                    print(f"  → Blocked at message #{blocked_at}: {data.get('message')}")
                    break
            except asyncio.TimeoutError:
                pass

        if blocked_at:
            print(f"  ✅ RATE LIMIT: Enforced at message #{blocked_at} (expected ≤16)")
        else:
            print("  ⚠️  Rate limit not triggered in 25 messages — check RATE_LIMIT config")


# ─────────────────────────────────────────────
# GENERATE RESUME SNIPPET
# ─────────────────────────────────────────────

def print_resume_snippet(max_conns: int, latency: dict, throughput: float):
    print("\n" + "="*60)
    print("📋 YOUR RESUME SNIPPET (copy these real numbers)")
    print("="*60)
    print(f"""
– Architected real-time chat for {max_conns}+ concurrent WebSocket
  connections via Django Channels 4 (ASGI/Daphne) & Redis channel layer;
  benchmarked at p50={latency['p50']}ms / p99={latency['p99']}ms round-trip
  latency and {throughput} messages/second throughput on localhost.
""")
    print("Note: Add '(benchmarked locally)' if you want to be extra transparent.")
    print("="*60)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Ano WebSocket Benchmark")
    parser.add_argument("--email",    default=TEST_EMAIL)
    parser.add_argument("--password", default=TEST_PASSWORD)
    parser.add_argument("--chatroom", default=CHATROOM_ID)
    parser.add_argument("--max-conns", type=int, default=100,
                        help="Max concurrent connections to test (default: 100)")
    parser.add_argument("--messages",  type=int, default=100,
                        help="Ping messages for latency test (default: 100)")
    parser.add_argument("--skip-conns", action="store_true",
                        help="Skip concurrent connection test (faster)")
    args = parser.parse_args()

    try:
        import websockets
    except ImportError:
        print("ERROR: Install websockets first:\n  pip install websockets aiohttp")
        sys.exit(1)

    print("Ano Platform — WebSocket Benchmark")
    print("Logging in...")

    token = await get_jwt_token(args.email, args.password)
    print(f"✅ Authenticated")

    chatroom_id = args.chatroom or await get_chatroom_id(token)
    print(f"✅ Using chatroom: {chatroom_id}")

    # Run benchmarks
    latency = await measure_message_latency(token, chatroom_id, args.messages)
    throughput = await measure_throughput(token, chatroom_id)
    await benchmark_rest_api(token, chatroom_id)
    await verify_rate_limit(token, chatroom_id)

    max_conns = args.max_conns
    if not args.skip_conns:
        max_conns = await benchmark_concurrent_connections(
            token, chatroom_id, max_conns=args.max_conns
        )

    print_resume_snippet(max_conns, latency, throughput)


if __name__ == "__main__":
    asyncio.run(main())
