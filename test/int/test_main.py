"""Integration tests for rick_and_morty_async.main module."""
import unittest
from unittest.mock import AsyncMock, patch

from main import main


class TestMain(unittest.IsolatedAsyncioTestCase):
    async def test_main_fetches_all_endpoints(self) -> None:
        """Test that main fetches characters, locations, and episodes."""
        with patch("main.list_characters") as mock_chars, \
             patch("main.list_locations") as mock_locs, \
             patch("main.list_episodes") as mock_eps, \
             patch("main.json_out") as mock_output:

            mock_chars.return_value = AsyncMock()
            mock_locs.return_value = AsyncMock()
            mock_eps.return_value = AsyncMock()
            mock_output.return_value = AsyncMock()

            class Args:
                domain = "https://rickandmortyapi.com/api"
                proxies = None

            with patch("main.args", Args, create=True), \
                 patch("main.proxies", None, create=True):
                await main()

            mock_chars.assert_called_once()
            mock_locs.assert_called_once()
            mock_eps.assert_called_once()
            mock_output.assert_called_once()


if __name__ == '__main__':
    unittest.main()
