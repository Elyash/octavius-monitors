"""Tests for async_helpers module."""

import asyncio
import time
import pytest

import octavius_monitors


@pytest.mark.asyncio
async def test_task_runner_sanity(mocker):
    """Sanity test for TaskRunner"""

    task_runner = octavius_monitors.TaskRunner()

    mocked_in_start = mocker.patch('octavius_monitors.TaskRunner._in_start')
    mocked_in_loop = mocker.patch('octavius_monitors.TaskRunner._in_loop')
    mocked_in_suspend = mocker.patch('octavius_monitors.TaskRunner._in_suspend')
    mocked_in_restart = mocker.patch('octavius_monitors.TaskRunner._in_restart')
    mocked_in_end = mocker.patch('octavius_monitors.TaskRunner._in_end')

    async with task_runner:
        await asyncio.sleep(1)

    mocked_in_start.assert_called_once()
    mocked_in_loop.assert_called()
    mocked_in_suspend.assert_not_called()
    mocked_in_restart.assert_not_called()
    mocked_in_end.assert_called_once()


@pytest.mark.asyncio
async def test_task_runner_suspend_and_restart(mocker):
    """Suspend and restart task runner."""

    task_runner = octavius_monitors.TaskRunner()

    mocked_in_start = mocker.patch('octavius_monitors.TaskRunner._in_start')
    mocked_in_loop = mocker.patch('octavius_monitors.TaskRunner._in_loop')
    mocked_in_suspend = mocker.patch('octavius_monitors.TaskRunner._in_suspend')
    mocked_in_restart = mocker.patch('octavius_monitors.TaskRunner._in_restart')
    mocked_in_end = mocker.patch('octavius_monitors.TaskRunner._in_end')

    async with task_runner as my_task_runner:
        await asyncio.sleep(0)
        my_task_runner.suspend()
        await asyncio.sleep(0)
        my_task_runner.restart()
        await asyncio.sleep(0)

    mocked_in_start.assert_called_once()
    mocked_in_loop.assert_called()
    mocked_in_suspend.assert_called_once()
    mocked_in_restart.assert_called_once()
    mocked_in_end.assert_called_once()


@pytest.mark.xfail(raises=ZeroDivisionError)
@pytest.mark.asyncio
async def test_task_runner_failed_inside_monitor(mocker):
    """Monitor works in case of excpetion inside of the context manager."""

    task_runner = octavius_monitors.TaskRunner()

    mocked_in_start = mocker.patch('octavius_monitors.TaskRunner._in_start')
    mocked_in_loop = mocker.patch('octavius_monitors.TaskRunner._in_loop')
    mocked_in_suspend = mocker.patch('octavius_monitors.TaskRunner._in_suspend')
    mocked_in_restart = mocker.patch('octavius_monitors.TaskRunner._in_restart')
    mocked_in_end = mocker.patch('octavius_monitors.TaskRunner._in_end')

    async with task_runner:
        _ = 3 / 0

    mocked_in_start.assert_called_once()
    mocked_in_loop.assert_called()
    mocked_in_suspend.assert_not_called()
    mocked_in_restart.assert_not_called()
    mocked_in_end.assert_called_once()

@pytest.mark.parametrize('at_least', [0.0, 0.3, 0.7, 1.1])
@pytest.mark.asyncio
async def test_task_runner_with_at_least(at_least):
    """Task runner with usage in the at_least option."""

    task_runner = octavius_monitors.TaskRunner(at_least=at_least)

    monitor_start_time = time.time()
    async with task_runner:
        await asyncio.sleep(0)
    monitor_end_time = time.time()

    assert monitor_end_time - monitor_start_time > at_least


@pytest.mark.parametrize('timeout', [0.0, 0.3, 0.7, 1.1])
@pytest.mark.asyncio
async def test_task_runner_with_timeout_not_done(timeout):
    """Task runner with usage in the timeout option."""

    task_runner = octavius_monitors.TaskRunner(timeout=timeout)

    monitor_start_time = time.time()
    async with task_runner:
        await asyncio.sleep(0)
    monitor_end_time = time.time()

    assert monitor_end_time - monitor_start_time > timeout


@pytest.mark.parametrize('timeout', [0.0, 0.3, 0.7, 1.1])
@pytest.mark.asyncio
async def test_task_runner_with_timeout_and_done(timeout):
    """Task runner with usage in the timeout option."""

    task_runner = octavius_monitors.TaskRunner(timeout=timeout)

    monitor_start_time = time.time()
    async with task_runner:
        await asyncio.sleep(0)
        task_runner.done()
        await asyncio.sleep(0)

    monitor_end_time = time.time()

    assert monitor_end_time - monitor_start_time <= 0.01
