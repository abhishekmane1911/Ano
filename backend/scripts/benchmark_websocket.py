#!/usr/bin/env python3
"""
Realistic WebSocket Benchmark for Ano Platform Chat System
- Uses existing test users (no registration).
- Caches tokens to avoid repeated logins.
- Supports --reset to flush Redis state (clears mutes, counters).
- Fixes throughput timing (no negative elapsed).
- Correctly counts broadcasts with multiple listeners.
"""

import asyncio
import json
import time
import statistics
import argparse
import uuid
import random
import string
from typing import List, Tuple

import aiohttp
import websockets
import redis.asyncio as redis

# -------------------------------------------------------------------
# CONFIGURATION – Change these to match your environment
# -------------------------------------------------------------------
BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
CHATROOM_ID = "bf1adad1-3768-46c1-814f-a0f4815b3292"  # Replace with your chatroom UUID

TEST_USERS = [
    "cse220001014@iiti.ac.in",
    "cse220001005@iiti.ac.in",
    "cse220001006@iiti.ac.in",
    "cse220001007@iiti.ac.in",
    "cse220001008@iiti.ac.in",
    "cse220001009@iiti.ac.in",
    "cse220001010@iiti.ac.in",
    "cse220001011@iiti.ac.in",
    "cse220001012@iiti.ac.in",
    "cse220001013@iiti.ac.in"
]
TEST_USER_PASSWORD = "TestPass123!"

CONNECTION_TEST_MAX = 200          # maximum concurrent connections to test
THROUGHPUT_MESSAGES_PER_SENDER = 15
THROUGHPUT_NUM_SENDERS = 10
THROUGHPUT_NUM_LISTENERS = 50
LATENCY_MESSAGES = 20
LATENCY_DELAY = 0.25               # seconds between latency messages (avoid burst)

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB_CACHE = 1                 # your cache DB (anti‑spam counters)
REDIS_DB_CHANNEL = 0               # channel layer DB (if used)

# -------------------------------------------------------------------
# Token cache (persists across runs if you keep the script loaded)
# -------------------------------------------------------------------
_token_cache = {}

async def get_jwt_token(session: aiohttp.ClientSession, email: str, password: str, force: bool = False) -> str:
    """Get JWT token; cache it unless force=True."""
    if not force and email in _token_cache:
        return _token_cache[email]
    async with session.post(f"{BASE_URL}/api/auth/login/",
                            json={"email": email, "password": password}) as resp:
        if resp.status != 200:
            body = await resp.text()
            raise RuntimeError(f"Login failed for {email}: {body}")
        data = await resp.json()
        _token_cache[email] = data["access"]
        return data["access"]

async def reset_redis_state():
    """Flush Redis databases used for cache and channel layer."""
    try:
        r_cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_CACHE, decode_responses=True)
        await r_cache.flushdb()
        print("  ✅ Flushed Redis cache DB (anti‑spam counters cleared)")
        r_channel = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_CHANNEL, decode_responses=True)
        await r_channel.flushdb()
        print("  ✅ Flushed Redis channel DB")
    except Exception as e:
        print(f"  ⚠️  Redis flush failed: {e} (proceeding anyway)")

async def get_chatroom_id(session: aiohttp.ClientSession, token: str) -> str:
    async with session.get(f"{BASE_URL}/api/chat/chatrooms/",
                           headers={"Authorization": f"Bearer {token}"}) as resp:
        data = await resp.json()
        rooms = data.get("results", data) if isinstance(data, dict) else data
        if not rooms:
            raise RuntimeError("No active chatrooms found. Create one first.")
        return rooms[0]["id"]

# -------------------------------------------------------------------
# Benchmark 1: Concurrent Connections
# -------------------------------------------------------------------
async def hold_connection(token: str, chatroom_id: str, conn_id: int, results: dict):
    url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"
    try:
        await asyncio.sleep(conn_id * 0.02)
        async with websockets.connect(url, open_timeout=5) as ws:
            results[conn_id] = "connected"
            while True:
                await ws.recv()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        results[conn_id] = f"failed: {type(e).__name__}"

async def benchmark_connections(tokens: List[str], chatroom_id: str, max_conns: int, step: int = 25):
    print("\n" + "="*60)
    print("BENCHMARK 1: Concurrent WebSocket Connections (multi-user)")
    print("="*60)

    last_stable = 0
    for n in range(step, max_conns + 1, step):
        results = {}
        tasks = []
        for i in range(n):
            token = tokens[i % len(tokens)]
            tasks.append(asyncio.create_task(hold_connection(token, chatroom_id, i, results)))
        wait_time = max(3.0, (n * 0.01) + 3.0)
        await asyncio.sleep(wait_time)

        connected = sum(1 for v in results.values() if v == "connected")
        failed = sum(1 for v in results.values() if v.startswith("failed"))
        print(f"  Attempted: {n:4d}  Connected: {connected:4d}  Failed: {failed:4d}")
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        if failed == 0:
            last_stable = connected
        else:
            print(f"  → Failures detected. (Check ulimit and server logs.)")
            break
        await asyncio.sleep(2)
    return last_stable

# -------------------------------------------------------------------
# Benchmark 2: End-to-End Latency (with delay to avoid burst)
# -------------------------------------------------------------------
async def measure_latency(token: str, chatroom_id: str, n_messages: int = LATENCY_MESSAGES, delay: float = LATENCY_DELAY) -> dict:
    print("\n" + "="*60)
    print("BENCHMARK 2: Real Message Round-Trip Latency (Anti-Spam Bypassed)")
    print("="*60)

    url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"
    latencies = []
    successful = 0
    blocked = 0

    try:
        async with websockets.connect(url, open_timeout=5) as ws:
            # Warm-up
            for _ in range(2):
                unique = uuid.uuid4().hex[:6]
                await ws.send(json.dumps({
                    "type": "message.send",
                    "content": f"latency_warmup {unique}"
                }))
                try:
                    await asyncio.wait_for(ws.recv(), timeout=2.0)
                except:
                    pass
                await asyncio.sleep(delay)

            for i in range(n_messages):
                unique = uuid.uuid4().hex[:6]
                content = f"BENCHMARK_BYPASS latency_test_{i}_{unique}"
                t0 = time.monotonic()
                await ws.send(json.dumps({"type": "message.send", "content": content}))
                try:
                    while True:
                        msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        data = json.loads(msg)
                        if data.get("type") == "message.receive":
                            msg_content = data.get("message", {}).get("content", "")
                            if content in msg_content:
                                t1 = time.monotonic()
                                latencies.append((t1 - t0) * 1000)
                                successful += 1
                                break
                        elif data.get("type") == "error":
                            blocked += 1
                            print(f"  ⚠️  Message blocked: {data.get('message')}")
                            break
                except asyncio.TimeoutError:
                    print(f"  ⚠️  Timeout on message {i}")
                await asyncio.sleep(delay)
    except Exception as e:
        print(f"  ⚠️  WebSocket error: {e}")

    if latencies:
        stats = {
            "p50": round(statistics.median(latencies), 2),
            "p99": round(sorted(latencies)[int(len(latencies) * 0.99)], 2),
            "min": round(min(latencies), 2),
            "max": round(max(latencies), 2),
            "count": len(latencies),
            "successful": successful,
            "blocked": blocked
        }
        print(f"  ✅ LATENCY (ms): p50={stats['p50']}, p99={stats['p99']}, min={stats['min']}, max={stats['max']}")
        print(f"  Successful: {successful}, Blocked: {blocked}")
        return stats
    else:
        print("  ❌ No successful messages received (all blocked?)")
        return {"p50": 0, "p99": 0, "count": 0}

# -------------------------------------------------------------------
# Benchmark 3: Throughput (fixed timing)
# -------------------------------------------------------------------
async def throughput_sender(ws, sender_id: int, test_id: str, n_messages: int) -> dict:
    stats = {"sent": 0, "blocked": 0, "timeout": 0}
    for i in range(n_messages):
        if i % 3 == 0:
            content = f"BENCHMARK_BYPASS hi {test_id} {i}"
        elif i % 3 == 1:
            words = ''.join(random.choices(string.ascii_lowercase, k=20))
            content = f"BENCHMARK_BYPASS long message {test_id} {i} {words}"
        else:
            content = f"BENCHMARK_BYPASS what do you think about {test_id}? {i}"
        await ws.send(json.dumps({"type": "message.send", "content": content}))
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=3.0)
            data = json.loads(response)
            if data.get("type") == "error":
                stats["blocked"] += 1
            else:
                stats["sent"] += 1
        except asyncio.TimeoutError:
            stats["timeout"] += 1
    return stats

async def benchmark_throughput(tokens: List[str], chatroom_id: str):
    print("\n" + "="*60)
    print("BENCHMARK 3: Full Pipeline Throughput (Anti-Spam Bypassed)")
    print("="*60)

    n_senders = THROUGHPUT_NUM_SENDERS
    msgs_per_sender = THROUGHPUT_MESSAGES_PER_SENDER
    total_messages = n_senders * msgs_per_sender
    test_id = str(uuid.uuid4())[:8]

    listener_count = THROUGHPUT_NUM_LISTENERS
    expected_total = total_messages * listener_count
    received_count = 0
    all_received = asyncio.Event()
    start_time = 0
    end_time = 0

    async def listener(ws):
        nonlocal received_count, end_time
        try:
            while not all_received.is_set():
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get("type") == "message.receive":
                    msg_content = data.get("message", {}).get("content", "")
                    if test_id in msg_content:
                        received_count += 1
                        if received_count >= expected_total:
                            end_time = time.monotonic()
                            all_received.set()
        except asyncio.CancelledError:
            pass

    # Create listeners
    listener_tasks = []
    listener_ws_list = []
    for _ in range(listener_count):
        token = random.choice(tokens)
        url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"
        try:
            ws = await websockets.connect(url)
            listener_ws_list.append(ws)
            listener_tasks.append(asyncio.create_task(listener(ws)))
        except Exception as e:
            print(f"  ⚠️  Listener connection failed: {e}")

    if not listener_ws_list:
        print("  ❌ No listeners connected. Aborting throughput test.")
        return 0.0

    await asyncio.sleep(1)

    # Create senders
    sender_ws_list = []
    sender_tasks = []
    for i in range(n_senders):
        token = random.choice(tokens)
        url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"
        try:
            ws = await websockets.connect(url)
            sender_ws_list.append(ws)
            sender_tasks.append(asyncio.create_task(throughput_sender(ws, i, test_id, msgs_per_sender)))
        except Exception as e:
            print(f"  ⚠️  Sender connection failed: {e}")

    if not sender_tasks:
        print("  ❌ No senders connected. Aborting.")
        return 0.0

    start_time = time.monotonic()
    sender_stats = await asyncio.gather(*sender_tasks)
    try:
        await asyncio.wait_for(all_received.wait(), timeout=20.0)
    except asyncio.TimeoutError:
        # Timeout: set end_time to now so elapsed is positive
        end_time = time.monotonic()

    # Cleanup
    for ws in sender_ws_list + listener_ws_list:
        await ws.close()
    for t in listener_tasks:
        t.cancel()
    await asyncio.gather(*listener_tasks, return_exceptions=True)

    elapsed = end_time - start_time
    if elapsed <= 0:
        print("  ⚠️  Timing error, using 1s as fallback.")
        elapsed = 1.0

    if received_count == 0:
        print("  ❌ No messages received. All blocked?")
        return 0.0

    total_sent = sum(s["sent"] for s in sender_stats)
    total_blocked = sum(s["blocked"] for s in sender_stats)
    total_timeout = sum(s["timeout"] for s in sender_stats)

    send_throughput = total_sent / elapsed
    broadcast_throughput = received_count / elapsed

    print(f"  Sent {total_messages} messages across {n_senders} senders")
    print(f"  Successful sends: {total_sent}, blocked: {total_blocked}, timeout: {total_timeout}")
    print(f"  Total broadcasts received: {received_count} (expected {expected_total})")
    print(f"  Elapsed: {elapsed:.3f}s")
    print(f"  ✅ SEND THROUGHPUT: {send_throughput:.1f} msg/s (successful sends)")
    print(f"  ✅ BROADCAST THROUGHPUT: {broadcast_throughput:.1f} broadcasts/s")
    return send_throughput

# -------------------------------------------------------------------
# Benchmark 4: Anti-Spam Validation (fresh users per test)
# -------------------------------------------------------------------
async def test_anti_spam(tokens: List[str], chatroom_id: str):
    print("\n" + "="*60)
    print("BENCHMARK 4: Anti‑Spam System Validation")
    print("="*60)

    if len(tokens) < 6:
        print("  ⚠️  Not enough test users for anti‑spam tests; skipping.")
        return

    async def send_and_check(ws, content: str) -> Tuple[bool, str]:
        await ws.send(json.dumps({"type": "message.send", "content": content}))
        try:
            response = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = json.loads(response)
            if data.get("type") == "error" or data.get("spam_detected"):
                return True, data.get("message", "Spam detected")
            elif data.get("type") == "message.receive":
                return False, "OK"
            else:
                return False, "Unknown response"
        except asyncio.TimeoutError:
            return False, "Timeout"

    test_cases = [
        (0, "duplicate"),
        (1, "similarity"),
        (2, "short_burst"),
        (3, "long_burst"),
        (4, "mute")
    ]

    for idx, test_name in test_cases:
        token = tokens[idx]
        url = f"{WS_BASE_URL}/ws/chat/{chatroom_id}/?token={token}"
        async with websockets.connect(url) as ws:
            if test_name == "duplicate":
                print("  Testing duplicate message detection (3 identical messages)")
                msg = f"duplicate test {uuid.uuid4().hex[:4]}"
                blocked = False
                for i in range(4):
                    blocked, err = await send_and_check(ws, msg)
                    if blocked:
                        print(f"    ✅ Duplicate blocked: {err}")
                        break
                if not blocked:
                    print("    ❌ Duplicate not blocked")

            elif test_name == "similarity":
                print("  Testing similarity detection (levenshtein)")
                base = f"similarity test {uuid.uuid4().hex[:4]}"
                blocked = False
                for mod in [".", "!", "?", "!!", "..."]:
                    blocked, err = await send_and_check(ws, base + mod)
                    if blocked:
                        print(f"    ✅ Similarity blocked: {err}")
                        break
                if not blocked:
                    print("    ❌ Similarity not blocked")

            elif test_name == "short_burst":
                print("  Testing burst spam (short messages, limit=10)")
                blocked = False
                for i in range(12):
                    msg = f"b {uuid.uuid4().hex[:1]}"
                    blocked, err = await send_and_check(ws, msg)
                    if blocked:
                        print(f"    ✅ Short burst blocked: {err}")
                        break
                if not blocked:
                    print("    ❌ Short burst not blocked")

            elif test_name == "long_burst":
                print("  Testing burst spam (long messages, limit=7)")
                blocked = False
                for i in range(9):
                    msg = f"long burst test {uuid.uuid4().hex[:4]} {i}"
                    blocked, err = await send_and_check(ws, msg)
                    if blocked:
                        print(f"    ✅ Long burst blocked: {err}")
                        break
                if not blocked:
                    print("    ❌ Long burst not blocked")

            elif test_name == "mute":
                print("  Testing that user gets muted after violations")
                msg = f"mute test {uuid.uuid4().hex[:4]}"
                blocked = False
                for i in range(9):
                    blocked, err = await send_and_check(ws, msg)
                    if blocked and "muted" in err.lower():
                        print(f"    ✅ User muted: {err}")
                        break
                if not blocked:
                    print("    ❌ User not muted as expected")

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chatroom", default=CHATROOM_ID, help="Chatroom UUID to test")
    parser.add_argument("--max-conns", type=int, default=CONNECTION_TEST_MAX, help="Max connections to test")
    parser.add_argument("--reset", action="store_true", help="Flush Redis state before tests (clears mutes/counters)")
    parser.add_argument("--no-cache", action="store_true", help="Ignore cached tokens and login fresh")
    args = parser.parse_args()

    if args.reset:
        print("Resetting Redis state...")
        await reset_redis_state()
        print("Redis reset complete.\n")

    async with aiohttp.ClientSession() as session:
        print(f"Logging in to {len(TEST_USERS)} test users...")
        tokens = []
        for email in TEST_USERS:
            token = await get_jwt_token(session, email, TEST_USER_PASSWORD, force=args.no_cache)
            tokens.append(token)
            print(f"  ✅ {email} logged in")

        chatroom_id = args.chatroom
        if not chatroom_id:
            chatroom_id = await get_chatroom_id(session, tokens[0])

        print(f"\n🚀 Starting benchmarks on chatroom: {chatroom_id}")

        # Run benchmarks
        await benchmark_connections(tokens, chatroom_id, args.max_conns)

        # Latency: use token[0] (but avoid using the same user for everything to prevent cross-contamination)
        await measure_latency(tokens[0], chatroom_id)

        # Throughput: use tokens[1:] to spread load (avoid muting the first user)
        throughput_tokens = tokens[1:] if len(tokens) > 1 else tokens
        await benchmark_throughput(throughput_tokens, chatroom_id)

        # Anti-spam: uses tokens[0..4] (fresh users per test)
        await test_anti_spam(tokens, chatroom_id)

        print("\n" + "="*60)
        print("✅ All benchmarks completed.")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())