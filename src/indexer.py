from pathlib import Path
from chunkers.code import CodeChunker
from chunkers.text import TextChunker
import pickle
import re
from models import MinimalSource
from bm25 import BM25


class Indexer:
    def __init__(self, sources_directory_path, max_chunk_size):
        self.source_paths = []
        self.sources_directory_path = Path(sources_directory_path)
        self.text_chunker = TextChunker(max_chunk_size)
        self.code_chunker = CodeChunker(max_chunk_size)
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

    def chunk(self):
        self.set_source_paths()

        for path in self.source_paths:
            if path.suffix.lower() in [".txt", ".md"]:
                self.chunks.extend(self.text_chunker.build_chunks(path))

            if path.suffix.lower() == ".py":
                self.chunks.extend(self.code_chunker.build_chunks(path))


    def tokenize(self, text):
        tokens = re.split(r"[\W_]+", text.lower())
        clean_tokens = []

        for token in tokens:
            if len(token) < 3 or not token:
                continue
            clean_tokens.append(token.strip())

        return clean_tokens

    def tokenize_chunks(self):
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

    def search(self, query):
        scores = self.bm25.get_scores(self.tokenize(query), 1)
        print(self.chuks[])



indexer = Indexer("data/raw/vllm-0.10.1", 2000)
indexer.chunk()

indexer.tokenize_chunks()
# print(len(indexer.tokenized_chunks))

indexer.save()
indexer.load()
indexer.search("what Vulnerabilities cause")
