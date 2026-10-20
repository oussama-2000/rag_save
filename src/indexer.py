from pathlib import Path
from chunkers.code import CodeChunker
from chunkers.text import TextChunker
import pickle
import re
from models import MinimalSource, RagDataset, MinimalSearchResults, StudentSearchResults
from bm25 import BM25
import json


class Indexer:
    def __init__(self, sources_directory_path):
        self.source_paths = []
        self.sources_directory_path = Path(sources_directory_path)
        self.text_chunker = TextChunker()
        self.code_chunker = CodeChunker()
        self.chunks = []
        self.tokenized_chunks = [] # [{id: chunk_id, tokens: [tokens]}]
        self.bm25 = None
        self.avgdl = 0
        self.tokens_frequ = None

    def set_source_paths(self):
        files_path = self.sources_directory_path.rglob("*")
        for path in files_path:
            if path.suffix.lower() in [".py", ".txt", ".md"]:
                self.source_paths.append(path)

    def chunk(self, max_chunk_size):
        self.set_source_paths()

        for path in self.source_paths:
            if path.suffix.lower() in [".txt", ".md"]:
                self.chunks.extend(self.text_chunker.build_chunks(path, max_chunk_size))

            if path.suffix.lower() == ".py":
                self.chunks.extend(self.code_chunker.build_chunks(path, max_chunk_size))


    def tokenize(self, text):
        tokens = re.split(r"[\W_]+", text.lower())
        clean_tokens = []

        for token in tokens:
            if len(token) < 3 or not token:
                continue
            clean_tokens.append(token.strip())

        return clean_tokens

    def build(self):
        for chunk in self.chunks:
            self.tokenized_chunks.append({"id": chunk['id'], "tokens": self.tokenize(chunk['text'])})

        self.bm25 = BM25(self.tokenized_chunks)
        self.avgdl = self.bm25.calculate_avgdl()
        self.tokens_frequ = self.bm25.calculate_freq()

    
    def save(self, save_path="data/processed/indexed_chunks"):
        with open(save_path, "wb") as storage:
            pickle.dump({
                    "chunks": [MinimalSource(**chunk) for chunk in self.chunks],
                    "tokenized_chunks": self.tokenized_chunks,
                    "avgdl": self.avgdl,
                    "tokens_frequ": self.tokens_frequ,
                }, storage)

    def load(self, dist_path="data/processed/indexed_chunks"):
        with open(dist_path, "rb") as storage:
            data = pickle.load(storage)

        self.chunks = data['chunks']
        self.tokenized_chunks = data['tokenized_chunks']
        self.avgdl = data["avgdl"]
        self.tokens_frequ = data["tokens_frequ"]

        self.bm25 = BM25(self.tokenized_chunks)
        self.bm25.avgdl = self.avgdl
        self.bm25.freq = self.tokens_frequ

    def ingest(self, max_chunk_size):
        self.chunk(max_chunk_size)
        self.build()
        self.save()

    def search(self, query, k):
        if k <= len(self.chunks):
            scores = self.bm25.get_scores(self.tokenize(query))[:k]
            return [self.chunks[score[0]] for score in scores]

    def search_dataset(self, dataset_path="data/datasets_public/public/UnansweredQuestions", k=1):
        dataset_dir = Path(dataset_path)
        dataset_files = dataset_dir.rglob("*.json")

        search_results = []
        for file in dataset_files:
            with open(file, "r") as dataset:
                rag_questions = RagDataset(**json.load(dataset)).rag_questions

                for question in rag_questions:
                    search_result: MinimalSearchResults = {}
                    search_result["question_id"] = question.question_id
                    search_result["question"] = question.question
                    search_result["retrieved_sources"] = self.search(question.question, 1)
                    search_result["storing_file"] = file.name
                    search_results.append(MinimalSearchResults(**search_result))

        return StudentSearchResults(search_results=search_results, k=k)

    def save_search_result(self, search_result: StudentSearchResults, save_directory="data/search_results", k=1):

        output = {} # {file: {search_results:result, k:k}}
        for result in search_result.search_results:

            output[result.storing_file] = output.get(result.storing_file, [])

            
            output[result.storing_file].append({
                    "question_id": result.question_id,
                    "question": result.question,
                    "retriveved_sources": [dict(source) for source in result.retrieved_sources]
                }
            )

        Path(save_directory).mkdir(exist_ok=True)
        for file in output.keys():
            with open(f"{save_directory}/{file}", "w") as output_file:
                inp = {"search_results": output[file], "k": k}
                json.dump(inp, output_file, indent=4)



            
        


indexer = Indexer("data/raw/vllm-0.10.1", 2000)
indexer.chunk()

indexer.tokenize_chunks()
# print(len(indexer.tokenized_chunks))

indexer.save()
indexer.load()
# print(
#     indexer.search("what Vulnerabilities cause", 2)
# )
student_search_results = indexer.search_dataset()
indexer.save_search_result(student_search_results)
