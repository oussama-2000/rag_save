from indexer import Indexer
from evaluation import Recall
from fire import Fire

class CLI:
    def __init__(self):
        self.indexer = Indexer("data/raw/vllm-0.10.1")
        self.recall = Recall()

    def index(self, max_chunk_size: int=2000):
        self.indexer.ingest(max_chunk_size)

    def search(self, query: str, k: int=1):
        self.indexer.load()
        print(self.indexer.search(query, k))

    def search_dataset(self, dataset_path: str, k: int=1, save_directory: str="data/search_results"):
        self.indexer.load()
        student_search_results = self.indexer.search_dataset(dataset_path, k)
        self.indexer.save_search_result(student_search_results, save_directory)

    def evaluate(self, studen_search_results_path: str, dataset_path: str):
        print(self.recall.calculate_recall(studen_search_results_path, dataset_path, 5))
        
if __name__ == "__main__":
    Fire(CLI)
