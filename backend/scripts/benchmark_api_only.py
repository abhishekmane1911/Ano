"""
Quick benchmark — REST API only (no throughput test to avoid polluting DB).
Run this for clean message endpoint latency numbers.

Usage:
    python scripts/benchmark_api_only.py \
      --email cse240001051@iiti.ac.in \
      --password rajpatil
"""
import asyncio
import time
import statistics
import argparse
import aiohttp

BASE_URL = "http://localhost:8000"

async def get_jwt_token(email, password):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/api/auth/login/",
            json={"email": email, "password": password},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            data = await resp.json()
            return data["access"]

async def get_chatroom_id(token):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BASE_URL}/api/chat/chatrooms/",
            headers={"Authorization": f"Bearer {token}"},
        ) as resp:
            data = await resp.json()
            rooms = data.get("results", data) if isinstance(data, dict) else data
            return rooms[0]["id"]

async def benchmark_rest_api(token, chatroom_id, n=100):
    endpoints = [
        ("GET", f"/api/chat/chatrooms/"),
        ("GET", f"/api/auth/me/"),
        ("GET", f"/api/chat/chatrooms/{chatroom_id}/messages/"),
        ("GET", f"/api/chat/chatrooms/{chatroom_id}/messages/?ordering=wilson_score"),
    ]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n{'='*65}")
    print(f"REST API Benchmark ({n} requests each)")
    print(f"{'='*65}")
    print(f"{'Endpoint':<50} {'p50':>8} {'p95':>8} {'p99':>8}")
    print(f"{'-'*65}")

    all_results = {}
    async with aiohttp.ClientSession() as session:
        for method, path in endpoints:
            times = []
            url = f"{BASE_URL}{path}"
            # Warmup
            for _ in range(5):
                async with session.get(url, headers=headers) as r:
                    await r.json()

            for _ in range(n):
                t0 = time.perf_counter()
                async with session.get(url, headers=headers) as r:
                    await r.json()
                times.append((time.perf_counter() - t0) * 1000)

            p50 = round(statistics.median(times), 1)
            p95 = round(sorted(times)[int(len(times) * 0.95)], 1)
            p99 = round(sorted(times)[int(len(times) * 0.99)], 1)
            short = path[:48]
            print(f"{short:<50} {p50:>7.1f}ms {p95:>7.1f}ms {p99:>7.1f}ms")
            all_results[path] = {"p50": p50, "p95": p95, "p99": p99}

    print(f"\n{'='*65}")
    print("RESUME SNIPPET:")
    msg_p50 = all_results.get(f"/api/chat/chatrooms/{chatroom_id}/messages/", {}).get("p50", "?")
    me_p50  = all_results.get("/api/auth/me/", {}).get("p50", "?")
    print(f"""
  REST API: /me/ at {me_p50}ms p50, paginated message history
  at {msg_p50}ms p50 (50 messages/page, with reactions + ranking).
""")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email",    required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--chatroom", default="")
    parser.add_argument("--n",        type=int, default=100)
    args = parser.parse_args()

    print("Logging in...")
    token = await get_jwt_token(args.email, args.password)
    print(f"✅ Authenticated")
    chatroom_id = args.chatroom or await get_chatroom_id(token)
    print(f"✅ Chatroom: {chatroom_id}")
    await benchmark_rest_api(token, chatroom_id, args.n)

if __name__ == "__main__":
    asyncio.run(main())
