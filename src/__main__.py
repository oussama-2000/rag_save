from indexer import Indexer
from fire import Fire

class CLI:
    def __init__(self):
        self.indexer = Indexer("data/raw/vllm-0.10.1", 200)

    def index(self, max_chunk_size):
        self.indexer.ingest(max_chunk_size)


