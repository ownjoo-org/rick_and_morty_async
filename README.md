# rick_and_morty_async

An async Python client for the [Rick and Morty API](https://rickandmortyapi.com/) demonstrating concurrent HTTP patterns with `httpx`, `asyncio`, and `ownjoo-org/utils`.

## Features

- **Async HTTP Client** — Uses `httpx` with HTTP/2 support for concurrent API requests
- **Automatic Retries** — Built-in retry logic with exponential backoff via `retry-async`
- **Queue-Based Coordination** — Coordinates concurrent fetchers (characters, locations, episodes) with output parser using `asyncio.Queue`
- **Structured Logging** — Integration with `ownjoo-org/utils` logging utilities
- **Type-Safe** — Full type hints with mypy validation
- **Comprehensive Testing** — Unit and integration tests with pytest

## Setup

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/ownjoo-org/rick_and_morty_async.git
cd rick_and_morty_async

# Install development dependencies
pip install -e ".[dev]"
```

## Usage

### Basic Command

```bash
python main.py --domain https://rickandmortyapi.com/api
```

### Options

```
$ python main.py --help
usage: main.py [-h] [--domain DOMAIN] [--proxies PROXIES] [--log-level LOG_LEVEL]

options:
  -h, --help                     show this help message and exit
  --domain DOMAIN                The FQDN for your API (default: example.com)
  --proxies PROXIES              JSON structure specifying 'http' and 'https' proxy URLs
  --log-level LOG_LEVEL          Logging level 0 (NOTSET) - 50 (CRITICAL) (default: 20)
```

### Examples

```bash
# Query all characters, locations, and episodes
python main.py --domain https://rickandmortyapi.com/api

# With proxy configuration
python main.py \
  --domain https://rickandmortyapi.com/api \
  --proxies '{"http": "http://proxy:8080", "https": "https://proxy:8080"}'

# With debug logging
python main.py \
  --domain https://rickandmortyapi.com/api \
  --log-level 10
```

## Development

### Make Commands

```bash
make install          # Install production dependencies
make install-dev      # Install development dependencies
make lint             # Run linting checks
make format           # Format code with black
make type-check       # Run type checking with mypy
make test             # Run tests
make test-cov         # Run tests with coverage report
make clean            # Remove build artifacts and caches
make run              # Show CLI help
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rick_and_morty_async

# Run specific test file
pytest test/unit/test_client.py -v
```

### Code Quality

The project uses:

- **black** for code formatting
- **ruff** for linting
- **mypy** for type checking
- **pytest** for testing
- **pytest-asyncio** for async test support

All checks run automatically in the CI/CD pipeline (GitHub Actions).

## Architecture

### Module Structure

```
rick_and_morty_async/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── client.py            # Async HTTP client with httpx
├── parser.py            # JSON output formatter
├── tracker.py           # Task coordination
└── consts.py            # Constants
```

### Key Patterns

#### Async Fetcher Coordination

Concurrent fetchers for characters, locations, and episodes:

```python
client_coroutines: List[Coroutine] = [
    list_characters(url=domain, proxies=proxies, q=q),
    list_locations(url=domain, proxies=proxies, q=q),
    list_episodes(url=domain, proxies=proxies, q=q),
]
```

#### Queue-Based Output

Parser consumes results as they arrive:

```python
parser_coroutines: List[Coroutine] = [
    json_out(q=q),
]
await gather(*client_coroutines, *parser_coroutines, q.join())
```

#### Automatic Retry

Request retry with exponential backoff:

```python
@retry(exceptions=Exception, tries=3, delay=1, backoff=2, max_delay=5, logger=logger, is_async=True)
async def get_response(...) -> Optional[dict]:
    # Automatically retried on exception
```

## API Reference

- **Characters** — All 826+ characters from the show
- **Locations** — Locations featured in the series
- **Episodes** — All episodes with character and location references

See [Rick and Morty API Docs](https://rickandmortyapi.com/documentation) for details.

## Contributing

See [CLAUDE.md](CLAUDE.md) for organization standards and best practices.

## Standards

This project adheres to [ownjoo-org](https://github.com/ownjoo-org) standards:

- **Simplicity First** — Write the simplest code that solves the problem
- **Integration Testing** — Prefer real dependencies over mocks
- **Security by Default** — No OWASP Top 10 vulnerabilities
- **Explicit Commits** — Use conventional commits with clear history

See the [claude configuration hub](https://github.com/ownjoo-org/claude) for full guidelines.

## License

MIT
