# tests/conftest.py
import pytest
from mockito import unstub

@pytest.fixture(autouse=True)
def _auto_unstub():
    """Limpa todos os stubs/mocks do mockito após cada teste."""
    yield
    unstub()