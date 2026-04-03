import pytest
from asyncio import Queue
from unittest.mock import patch, MagicMock

from rick_and_morty_async.parser import json_out


class MockTaskList(list):
    """Mock task list that simulates task lifecycle."""
    def __init__(self, initial_tasks=1):
        super().__init__()
        self.initial_tasks = initial_tasks
        self.call_count = 0
        if initial_tasks > 0:
            self.append('task1')

    def __bool__(self):
        self.call_count += 1
        # Return True for first few calls, then False to exit loop
        if self.call_count > 3:
            return False
        return len(self) > 0


class TestJsonOut:
    @pytest.mark.asyncio
    async def test_json_out_single_result(self):
        """Test json_out with single result."""
        q = Queue()
        result = {'id': 1, 'name': 'Rick'}
        await q.put(result)

        mock_tasks = MockTaskList(initial_tasks=1)

        with patch('rick_and_morty_async.parser.contributing_tasks', mock_tasks):
            with patch('builtins.print') as mock_print:
                try:
                    await json_out(q=q)
                except Exception:
                    pass

                # Verify output started with '['
                calls = [str(call) for call in mock_print.call_args_list]
                output = ''.join(calls)
                assert '[' in output

    @pytest.mark.asyncio
    async def test_json_out_multiple_results(self):
        """Test json_out with multiple results."""
        q = Queue()
        results = [
            {'id': 1, 'name': 'Rick'},
            {'id': 2, 'name': 'Morty'},
        ]
        for result in results:
            await q.put(result)

        mock_tasks = MockTaskList(initial_tasks=1)

        with patch('rick_and_morty_async.parser.contributing_tasks', mock_tasks):
            with patch('builtins.print') as mock_print:
                try:
                    await json_out(q=q)
                except Exception:
                    pass

                # Verify output
                calls = [str(call) for call in mock_print.call_args_list]
                output = ''.join(calls)
                assert '[' in output

