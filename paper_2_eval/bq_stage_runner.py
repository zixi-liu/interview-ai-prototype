"""Minimal async stage runner.

asyncio 要点（与本文件相关）：
- `async def` 定义的是「协程函数」，调用它得到「协程对象」，不会立刻执行函数体。
- 在已经运行的事件循环里，用 `await` 驱动协程：把控制权交回循环，等该协程可继续时再恢复。
- `asyncio.Semaphore(n)`：最多同时 n 个协程进入 `async with sem` 保护的代码块（计数型限流）。
- `asyncio.Lock()`：异步互斥锁，`async with lock` 保证同一时刻只有一个协程执行临界区（这里用来串行更新「上次开始时间」）。
- `asyncio.wait_for(coro, timeout)`：给协程加超时，超时会取消该协程并抛出 `asyncio.TimeoutError`。
- `asyncio.gather(*coros)`：并发调度多个协程，等它们全部结束（默认有一个异常会传播；本处每个任务内部已 try/except，故多为正常返回 dict）。
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections.abc import Callable, Coroutine, Sequence
from typing import Any

_LOGGER = logging.getLogger(__name__)

# (task_id, provider_bucket, coro_factory) — factory must return a new coroutine per call (retries).
TaskRow = tuple[str, str, Callable[[], Coroutine[Any, Any, Any]]]


async def run_stage_tasks(
    tasks: Sequence[TaskRow],
    *,
    max_concurrent_global: int = 10,
    max_concurrent_per_provider: dict[str, int] | None = None,
    min_interval_sec_per_provider: dict[str, float] | None = None,
    max_retries: int = 3,
    retry_base_delay_sec: float = 1.0,
    retry_max_delay_sec: float = 60.0,
    retry_jitter_ratio: float = 0.1,
    request_timeout_sec: float | None = 120.0,
    log_level: int | str = logging.INFO,
    replicate_id: int | None = None,
    stage: int | None = None,
) -> list[dict[str, Any]]:
    caps = max_concurrent_per_provider or {}
    intervals = min_interval_sec_per_provider or {}

    if isinstance(log_level, str):
        _LOGGER.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    else:
        _LOGGER.setLevel(log_level)

    def provider_cap(provider: str) -> int:
        return max(1, int(caps.get(provider, max_concurrent_global)))

    # Semaphore：内部计数器，acquire 减一（到 0 则阻塞等待），release 加一。
    # 这里限制「全局限流」：任意时刻最多 max_concurrent_global 个协程同时占用「一次 API 尝试」的槽位。
    global_sem = asyncio.Semaphore(max(1, int(max_concurrent_global)))
    provider_sems: dict[str, asyncio.Semaphore] = {}
    # 每个 provider 一把异步锁：更新「上次任务开始时间」时必须互斥，避免两个协程同时改 dict 算错间隔。
    provider_locks: dict[str, asyncio.Lock] = {}
    provider_last_start: dict[str, float] = {}

    async def wait_min_interval(provider: str) -> None:
        """在真正发起请求前，按 provider 做最小时间间隔（与 Semaphore 配合：先抢到并发名额，再排队等间隔）。"""
        min_interval = max(0.0, float(intervals.get(provider, 0.0)))
        if min_interval <= 0:
            return
        lock = provider_locks.get(provider)
        if lock is None:
            lock = asyncio.Lock()
            provider_locks[provider] = lock
        # async with lock：进入时 await acquire()，退出时 release()；与线程锁不同，不会在阻塞时占满 OS 线程。
        async with lock:
            now = time.monotonic()
            last = provider_last_start.get(provider)
            if last is not None:
                wait = min_interval - (now - last)
                if wait > 0:
                    # asyncio.sleep：非阻塞「让出」事件循环指定秒数；期间其他协程可运行。
                    await asyncio.sleep(wait)
            provider_last_start[provider] = time.monotonic()

    async def run_one_attempt(provider: str, factory: Callable[[], Coroutine[Any, Any, Any]]) -> Any:
        """单次 API 尝试：先占全局槽位，再占该 provider 槽位，最后执行 factory() 返回的协程。"""
        # async with global_sem：等价于 finally 里 release，保证不会漏释放。
        async with global_sem:
            p_sem = provider_sems.get(provider)
            if p_sem is None:
                p_sem = asyncio.Semaphore(provider_cap(provider))
                provider_sems[provider] = p_sem
            # 这里用手动 acquire/release 包住 try/finally：与 async with 等价，便于在 finally 里一定 release。
            await p_sem.acquire()
            try:
                await wait_min_interval(provider)
                if request_timeout_sec is None or request_timeout_sec <= 0:
                    # await：暂停当前协程，直到 factory() 这次调用返回的协程跑完。
                    return await factory()
                # wait_for：在 timeout 内等待协程完成；超时则取消内部任务并抛 asyncio.TimeoutError。
                return await asyncio.wait_for(factory(), timeout=request_timeout_sec)
            finally:
                p_sem.release()

    async def run_task(task: TaskRow) -> dict[str, Any]:
        """一个业务任务：可能重试多次；每次重试都会再次 await run_one_attempt（即重新占信号量、重新执行 factory）。"""
        task_id, provider, factory = task
        started = time.perf_counter()
        attempts = 0
        result: Any | None = None
        error = ""
        status = "error"
        max_tries = max(1, int(max_retries) + 1)

        for attempt in range(1, max_tries + 1):
            attempts = attempt
            try:
                # 子协程里再 await：形成「协程调用链」，事件循环统一调度。
                result = await run_one_attempt(provider, factory)
                status = "ok"
                error = ""
                break
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                code = getattr(exc, "status_code", None)
                nested = getattr(exc, "response", None)
                nested_code = getattr(nested, "status_code", None) if nested is not None else None
                name = type(exc).__name__
                retryable = (
                    # 超时来自 wait_for 时，异常类型多为 asyncio.TimeoutError（与 asyncio 模块绑定）。
                    isinstance(exc, asyncio.TimeoutError)
                    or any(
                        s in name
                        for s in (
                            "RateLimit",
                            "Timeout",
                            "APIConnection",
                            "ConnectError",
                            "ReadTimeout",
                            "ServiceUnavailable",
                            "InternalServerError",
                        )
                    )
                    or (code is not None and int(code) in (408, 429, 500, 502, 503, 504))
                    or (nested_code is not None and int(nested_code) in (408, 429, 500, 502, 503, 504))
                )
                if attempt >= max_tries or not retryable:
                    status = "error"
                    break
                base = retry_base_delay_sec * (2 ** (attempt - 1))
                cap = min(base, retry_max_delay_sec)
                delay = min(cap + cap * retry_jitter_ratio * random.random(), retry_max_delay_sec)
                _LOGGER.warning(
                    "task %s attempt %s/%s failed (%s); retry in %.2fs",
                    task_id,
                    attempt,
                    max_tries,
                    error,
                    delay,
                )
                # 退避等待：同样用 asyncio.sleep，避免阻塞整个线程。
                await asyncio.sleep(delay)

        latency_ms = int((time.perf_counter() - started) * 1000)
        ok = status == "ok"
        if ok:
            _LOGGER.info(
                "task %s ok latency_ms=%s attempts=%s replicate_id=%s stage=%s",
                task_id,
                latency_ms,
                attempts,
                replicate_id,
                stage,
            )
        else:
            _LOGGER.error(
                "task %s failed latency_ms=%s attempts=%s err=%s replicate_id=%s stage=%s",
                task_id,
                latency_ms,
                attempts,
                error,
                replicate_id,
                stage,
            )

        return {
            "task_id": task_id,
            "ok": ok,
            "result": result,
            "error": error,
            "latency_ms": latency_ms,
            "attempts": attempts,
            "status": status,
            "replicate_id": replicate_id,
            "stage": stage,
        }

    _LOGGER.info(
        "run_stage_tasks start n=%s replicate_id=%s stage=%s global_cap=%s",
        len(tasks),
        replicate_id,
        stage,
        max_concurrent_global,
    )
    # gather：为每个 task 创建一个 run_task(t) 协程，并发执行；await gather 会等「全部」完成。
    # 返回值为各协程返回值按顺序组成的列表（此处为 list[dict]）。
    # 注意：生成器表达式里每个 run_task(t) 会立刻创建协程对象，真正调度由事件循环在 gather 内完成。
    outcomes = list(await asyncio.gather(*(run_task(t) for t in tasks)))
    ok_count = sum(1 for o in outcomes if o["ok"])
    _LOGGER.info(
        "run_stage_tasks done ok=%s fail=%s replicate_id=%s stage=%s",
        ok_count,
        len(outcomes) - ok_count,
        replicate_id,
        stage,
    )
    return outcomes
