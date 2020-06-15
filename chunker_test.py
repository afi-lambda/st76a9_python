import pytest
import json

from chunker import Chunker


@pytest.fixture
def reference_chunks():
    with open('evaluation.json') as json_file:
        json_data = json.load(json_file)
    return [each['source'] for each in json_data]


def test_chunker(reference_chunks):
    with open('bootstrap.utf.txt', encoding='utf-8') as bootstrap_file:
        chunker = Chunker(bootstrap_file)
        for index, each_chunk in enumerate(chunker):
            reference_chunk = reference_chunks[index]
            assert each_chunk == reference_chunk
