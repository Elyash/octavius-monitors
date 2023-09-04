"""Async helpers for monitors."""

from typing import Self, Callable, Any

import asyncio
import collections
import contextlib
import enum
import functools
import time


class InvalidTaskStateException(Exception):
    """Invalid task state."""


class TaskState(enum.Enum):
    """A Task state."""

    UNINITIALIZED = 0
    RUNNING = 1
    SUSPENDED = 2
    STOPED = 3
    RESTARTED = 4
    DONE = 5


class TaskRunner:
    """A task runner to run a specific task."""

    def __init__(self, **kwargs: dict[str, Any]):
        self._task: asyncio.Task | None = None
        self._task_state: TaskState = TaskState.UNINITIALIZED
        self._task_initialization_time: float | None = None

        default_kwargs = collections.defaultdict(lambda: 0.0, kwargs)

        self._at_least: float = default_kwargs['at_least']
        self._timeout: float = default_kwargs['timeout']


    async def __aenter__(self) -> Self:
        """Enter to the monitor."""

        self._task = asyncio.create_task(self._task_function())
        self._task_initialization_time = time.time()
        self._task_state = TaskState.RUNNING

        await asyncio.sleep(0)

        return self

    async def __aexit__(self, *exception) -> bool:
        """Exit from the monitor."""

        while await asyncio.sleep(0, result=True):
            task_runtime = time.time() - self._task_initialization_time
            if (self._at_least < task_runtime and
                    (self._timeout < task_runtime or self._task_state == TaskState.DONE)):
                break

        self._task.cancel()
        await asyncio.sleep(0)
        try:
            self._task.result()
        except asyncio.CancelledError:
            pass

    def done(self) -> None:

        self._task_state = TaskState.DONE

    def suspend(self) -> None:

        self._task_state = TaskState.SUSPENDED

    def restart(self) -> None:

        self._task_state = TaskState.RESTARTED

    async def _task_function(self) -> None:

        await self._in_start()

        try:
            while await asyncio.sleep(0, result=True):
                match self._task_state:
                    case TaskState.DONE:
                        if self._task_initialization_time + self._at_least > time.time():
                            await self._in_loop()
                        else:
                            break

                    case TaskState.STOPED:
                        continue

                    case TaskState.RUNNING:
                        await self._in_loop()

                    case TaskState.RESTARTED:
                        await self._in_restart()
                        self._task_state = TaskState.RUNNING

                    case TaskState.SUSPENDED:
                        await self._in_suspend()
                        self._task_state = TaskState.STOPED

                    case _:
                        raise InvalidTaskStateException()
        finally:
            await self._in_end()

    async def _in_start(self) -> None:

        pass

    async def _in_loop(self) -> None:

        pass

    async def _in_suspend(self) -> None:

        pass

    async def _in_restart(self) -> None:

        pass

    async def _in_end(self) -> None:

        pass


@contextlib.contextmanager
def suspend(*task_runners: tuple[TaskRunner]) -> None:

    for task_runner in task_runners:
        task_runner.suspend()

    try:
        yield

    finally:
        for task_runner in task_runners:
            task_runner.restart()


def run_in_executor(func: Callable) -> Callable:

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

    return wrapper