"""Tests for async_helpers module."""

import asyncio
import pytest

import octavius_monitors

@pytest.mark.asyncio
async def test_task_runner_sanity():
    """Sanity test for TaskRunner"""

    task_runner = octavius_monitors.TaskRunner()
    async with task_runner:
        await asyncio.sleep(5)
