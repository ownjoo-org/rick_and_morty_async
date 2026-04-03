import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_response():
    """Fixture for mock API responses."""
    return {
        'results': [
            {'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive'},
            {'id': 2, 'name': 'Morty Smith', 'status': 'Alive'},
        ],
        'info': {
            'count': 2,
            'pages': 1,
            'next': None,
            'prev': None,
        }
    }


@pytest.fixture
def mock_paginated_response():
    """Fixture for paginated API responses."""
    return {
        'results': [
            {'id': i, 'name': f'Character {i}', 'status': 'Alive'}
            for i in range(1, 21)
        ],
        'info': {
            'count': 826,
            'pages': 42,
            'next': 'https://rickandmortyapi.com/api/character?page=2',
            'prev': None,
        }
    }


@pytest.fixture
def root_response():
    """Fixture for root API response."""
    return {
        'characters': 'https://rickandmortyapi.com/api/character',
        'locations': 'https://rickandmortyapi.com/api/location',
        'episodes': 'https://rickandmortyapi.com/api/episode',
    }
