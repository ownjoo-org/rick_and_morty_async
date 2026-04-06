import unittest
from asyncio import Queue
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import HTTPStatusError

from rick_and_morty_async.client import (
    get_response,
    list_results_paginated,
    list_results,
    list_characters,
    list_characters_paginated,
    list_locations,
    list_locations_paginated,
    list_episodes,
    list_episodes_paginated,
    get_data,
)


class TestGetResponse(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }

    async def test_get_response_success(self):
        """Test successful GET request."""
        with patch('rick_and_morty_async.client.AsyncClient') as mock_client:
            mock_session = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = self.mock_response
            mock_session.request.return_value = mock_response_obj
            mock_session.__aenter__.return_value = mock_session
            mock_client.return_value.__aenter__.return_value = mock_session

            result = await get_response(url='https://example.com/api')

            self.assertEqual(result, self.mock_response)
            mock_session.request.assert_called_once()

    async def test_get_response_404_returns_none(self):
        """Test GET request returns None for 404."""
        with patch('rick_and_morty_async.client.AsyncClient') as mock_client:
            mock_session = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 404
            mock_session.request.side_effect = HTTPStatusError(
                'Not Found',
                request=MagicMock(),
                response=mock_response_obj,
            )
            mock_session.__aenter__.return_value = mock_session
            mock_client.return_value.__aenter__.return_value = mock_session

            result = await get_response(url='https://example.com/api/404')

            self.assertIsNone(result)

    async def test_get_response_with_params(self):
        """Test GET request with query parameters."""
        with patch('rick_and_morty_async.client.AsyncClient') as mock_client:
            mock_session = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = {'results': []}
            mock_session.request.return_value = mock_response_obj
            mock_session.__aenter__.return_value = mock_session
            mock_client.return_value.__aenter__.return_value = mock_session

            await get_response(url='https://example.com/api', params={'page': 1})

            mock_session.request.assert_called_once()
            call_kwargs = mock_session.request.call_args[1]
            self.assertEqual(call_kwargs['params'], {'page': 1})

    async def test_get_response_with_proxies(self):
        """Test GET request with proxy configuration."""
        with patch('rick_and_morty_async.client.AsyncClient') as mock_client:
            mock_session = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = {}
            mock_session.request.return_value = mock_response_obj
            mock_session.__aenter__.return_value = mock_session
            mock_client.return_value.__aenter__.return_value = mock_session

            proxies = {'http': 'http://proxy.example.com:8080'}
            await get_response(url='https://example.com/api', proxies=proxies)

            self.assertEqual(mock_session.proxies, proxies)


class TestListResultsPaginated(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }

    async def test_list_results_paginated_single_page(self):
        """Test pagination with single page."""
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = self.mock_response

            results = []
            async for result in list_results_paginated(url='https://example.com/api'):
                results.append(result)

            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]['id'], 1)
            self.assertEqual(results[1]['id'], 2)

    async def test_list_results_paginated_multiple_pages(self):
        """Test pagination with multiple pages."""
        response_page_1 = {
            'results': [{'id': 1}, {'id': 2}],
            'info': {'count': 4, 'pages': 2, 'next': 'https://example.com/api?page=2', 'prev': None},
        }
        response_page_2 = {
            'results': [{'id': 3}, {'id': 4}],
            'info': {'count': 4, 'pages': 2, 'next': None, 'prev': 'https://example.com/api?page=1'},
        }

        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [response_page_1, response_page_2]

            results = []
            async for result in list_results_paginated(url='https://example.com/api'):
                results.append(result)

            self.assertEqual(len(results), 4)
            self.assertEqual(mock_get.call_count, 2)

    async def test_list_results_paginated_with_additional_params(self):
        """Test pagination with additional parameters."""
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                'results': [{'id': 1}],
                'info': {'count': 1, 'pages': 1, 'next': None, 'prev': None},
            }

            async for _ in list_results_paginated(
                url='https://example.com/api',
                additional_params={'status': 'alive'},
            ):
                pass

            call_kwargs = mock_get.call_args[1]
            self.assertIn('status', call_kwargs.get('params', {}))


class TestListResults(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }

    async def test_list_results(self):
        """Test list_results function."""
        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = self.mock_response

            await list_results(url='https://example.com/api', q=q)

            self.assertEqual(q.qsize(), 2)

    async def test_list_results_empty_results(self):
        """Test list_results with empty results."""
        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {
                'results': [],
                'info': {'count': 0, 'pages': 0, 'next': None, 'prev': None},
            }

            await list_results(url='https://example.com/api', q=q)

            self.assertEqual(q.qsize(), 0)


class TestListCharacters(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }
        self.root_response = {
            'characters': 'https://rickandmortyapi.com/api/character',
            'locations': 'https://rickandmortyapi.com/api/location',
            'episodes': 'https://rickandmortyapi.com/api/episode',
        }

    async def test_list_characters(self):
        """Test list_characters function."""
        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [
                self.root_response,
                {'info': {'pages': 1}, 'results': self.mock_response['results']},
            ]

            await list_characters(url='https://example.com/api', q=q)

            self.assertGreaterEqual(mock_get.call_count, 2)


class TestListCharactersPaginated(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }
        self.root_response = {
            'characters': 'https://rickandmortyapi.com/api/character',
            'locations': 'https://rickandmortyapi.com/api/location',
            'episodes': 'https://rickandmortyapi.com/api/episode',
        }

    async def test_list_characters_paginated(self):
        """Test list_characters_paginated function."""
        async def async_generator_mock():
            for result in self.mock_response['results']:
                yield result

        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get, \
             patch('rick_and_morty_async.client.list_results_paginated') as mock_paginated:

            mock_get.return_value = self.root_response
            mock_paginated.return_value = async_generator_mock()

            await list_characters_paginated(domain='https://example.com/api', q=q)

            self.assertEqual(q.qsize(), 2)


class TestListLocations(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }
        self.root_response = {
            'characters': 'https://rickandmortyapi.com/api/character',
            'locations': 'https://rickandmortyapi.com/api/location',
            'episodes': 'https://rickandmortyapi.com/api/episode',
        }

    async def test_list_locations(self):
        """Test list_locations function."""
        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [
                self.root_response,
                {'info': {'pages': 1}, 'results': self.mock_response['results']},
            ]

            await list_locations(url='https://example.com/api', q=q)

            self.assertGreaterEqual(mock_get.call_count, 2)


class TestListLocationsPaginated(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }
        self.root_response = {
            'characters': 'https://rickandmortyapi.com/api/character',
            'locations': 'https://rickandmortyapi.com/api/location',
            'episodes': 'https://rickandmortyapi.com/api/episode',
        }

    async def test_list_locations_paginated(self):
        """Test list_locations_paginated function."""
        async def async_generator_mock():
            for result in self.mock_response['results']:
                yield result

        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get, \
             patch('rick_and_morty_async.client.list_results_paginated') as mock_paginated:

            mock_get.return_value = self.root_response
            mock_paginated.return_value = async_generator_mock()

            await list_locations_paginated(domain='https://example.com/api', q=q)

            self.assertEqual(q.qsize(), 2)


class TestListEpisodes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }
        self.root_response = {
            'characters': 'https://rickandmortyapi.com/api/character',
            'locations': 'https://rickandmortyapi.com/api/location',
            'episodes': 'https://rickandmortyapi.com/api/episode',
        }

    async def test_list_episodes(self):
        """Test list_episodes function."""
        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = [
                self.root_response,
                {'info': {'pages': 1}, 'results': self.mock_response['results']},
            ]

            await list_episodes(url='https://example.com/api', q=q)

            self.assertGreaterEqual(mock_get.call_count, 2)


class TestListEpisodesPaginated(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }
        self.root_response = {
            'characters': 'https://rickandmortyapi.com/api/character',
            'locations': 'https://rickandmortyapi.com/api/location',
            'episodes': 'https://rickandmortyapi.com/api/episode',
        }

    async def test_list_episodes_paginated(self):
        """Test list_episodes_paginated function."""
        async def async_generator_mock():
            for result in self.mock_response['results']:
                yield result

        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get, \
             patch('rick_and_morty_async.client.list_results_paginated') as mock_paginated:

            mock_get.return_value = self.root_response
            mock_paginated.return_value = async_generator_mock()

            await list_episodes_paginated(domain='https://example.com/api', q=q)

            self.assertEqual(q.qsize(), 2)


class TestGetData(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_response = {
            'results': [
                {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
                {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
            ],
            'info': {'count': 2, 'pages': 1, 'next': None, 'prev': None},
        }
        self.root_response = {
            'characters': 'https://rickandmortyapi.com/api/character',
            'locations': 'https://rickandmortyapi.com/api/location',
            'episodes': 'https://rickandmortyapi.com/api/episode',
        }

    async def test_get_data(self):
        """Test get_data function."""
        async def async_generator_mock():
            for result in self.mock_response['results']:
                yield result

        q = Queue()
        with patch('rick_and_morty_async.client.get_response', new_callable=AsyncMock) as mock_get, \
             patch('rick_and_morty_async.client.list_results_paginated') as mock_paginated:

            mock_get.return_value = self.root_response
            mock_paginated.return_value = async_generator_mock()

            await get_data(domain='https://example.com/api', q=q)

            self.assertGreater(q.qsize(), 0)


if __name__ == '__main__':
    unittest.main()
