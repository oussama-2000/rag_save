from indexer import Indexer
from fire import Fire

class CLI:
    def __init__(self):
        self.indexer = Indexer("data/raw/vllm-0.10.1")

    def index(self, max_chunk_size: int=2000):
        self.indexer.ingest(max_chunk_size)

    def search(self, query: str, k: int=1):
        self.indexer.load()
        print(self.indexer.search(query, k))

    def search_dataset(self, dataset_path: str, k: int=1, save_directory: str="data/search_results"):
        self.indexer.load()
        student_search_results = self.indexer.search_dataset(dataset_path, k)
        self.indexer.save_search_result(student_search_results, save_directory)
    
if __name__ == "__main__":
    Fire(CLI)
