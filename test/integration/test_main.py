"""Integration tests for rick_and_morty_async.main module."""
import pytest
from unittest.mock import AsyncMock, patch

from rick_and_morty_async.main import main


@pytest.mark.asyncio
async def test_main_fetches_all_endpoints() -> None:
    """Test that main fetches characters, locations, and episodes."""
    with patch("rick_and_morty_async.main.list_characters") as mock_chars, \
         patch("rick_and_morty_async.main.list_locations") as mock_locs, \
         patch("rick_and_morty_async.main.list_episodes") as mock_eps, \
         patch("rick_and_morty_async.main.json_out") as mock_output:

        mock_chars.return_value = AsyncMock()
        mock_locs.return_value = AsyncMock()
        mock_eps.return_value = AsyncMock()
        mock_output.return_value = AsyncMock()

        # Create a global args object for the test
        class Args:
            domain = "https://rickandmortyapi.com/api"
            proxies = None

        with patch("__main__.args", Args, create=True):
            await main()

        # Verify all three endpoints were queried
        mock_chars.assert_called_once()
        mock_locs.assert_called_once()
        mock_eps.assert_called_once()
        mock_output.assert_called_once()
