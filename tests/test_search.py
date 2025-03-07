"""Test RAGLite's search functionality."""

import pytest

from raglite import (
    RAGLiteConfig,
    hybrid_search,
    keyword_search,
    retrieve_chunks,
    retrieve_segments,
    vector_search,
)
from raglite._database import Chunk
from raglite._typing import SearchMethod


@pytest.fixture(
    params=[
        pytest.param(keyword_search, id="keyword_search"),
        pytest.param(vector_search, id="vector_search"),
        pytest.param(hybrid_search, id="hybrid_search"),
    ],
)
def search_method(
    request: pytest.FixtureRequest,
) -> SearchMethod:
    """Get a search method to test RAGLite with."""
    search_method: SearchMethod = request.param
    return search_method


def test_search(raglite_test_config: RAGLiteConfig, search_method: SearchMethod) -> None:
    """Test searching for a query."""
    # Search for a query.
    query = "What does it mean for two events to be simultaneous?"
    num_results = 5
    chunk_ids, scores = search_method(query, num_results=num_results, config=raglite_test_config)
    assert len(chunk_ids) == len(scores) == num_results
    assert all(isinstance(chunk_id, str) for chunk_id in chunk_ids)
    assert all(isinstance(score, float) for score in scores)
    # Retrieve the chunks.
    chunks = retrieve_chunks(chunk_ids, config=raglite_test_config)
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert all(chunk_id == chunk.id for chunk_id, chunk in zip(chunk_ids, chunks, strict=True))
    assert any("Definition of Simultaneity" in str(chunk) for chunk in chunks)
    # Extend the chunks with their neighbours and group them into contiguous segments.
    segments = retrieve_segments(chunk_ids, neighbors=(-1, 1), config=raglite_test_config)
    assert all(isinstance(segment, str) for segment in segments)


def test_search_no_results(raglite_test_config: RAGLiteConfig, search_method: SearchMethod) -> None:
    """Test searching for a query with no keyword search results."""
    query = "supercalifragilisticexpialidocious"
    num_results = 5
    chunk_ids, scores = search_method(query, num_results=num_results, config=raglite_test_config)
    num_results_expected = 0 if search_method == keyword_search else num_results
    assert len(chunk_ids) == len(scores) == num_results_expected
    assert all(isinstance(chunk_id, str) for chunk_id in chunk_ids)
    assert all(isinstance(score, float) for score in scores)
