# corpus = [
#     {"id": 1, "tokens": ['what', 'is', 'is', 'rag', '?']},
#     {"id": 2, "tokens": ['how', 'is', 'rag', 'it', 'works', '?']},
#     {"id": 3, "tokens": ['python', 'contains', 'a', 'lot', 'of', 'build-in', 'functions']}
# ]

import math

class BM25:
    def __init__(self, chunks):

        self.chunks = chunks
        self.freq = {} # {token: {chunk_id: number of repetitions}}
        self.avgdl = 0
        self.k1 = 1.2
        self.b = 0.75

    def calculate_freq(self):
        for chunk in self.chunks:
            for token in chunk['tokens']:
                self.freq[token] = self.freq.get(token, {})
                self.freq[token][chunk['id']] = self.freq[token].get(chunk['id'], 0) + 1
                
        return self.freq

    def calculate_avgdl(self):
        s = sum([len(chunk['tokens']) for chunk in self.chunks])
        self.avgdl = s / len(self.chunks)

        return self.avgdl

    def calculate_TF(self, token, chunk):
        try:
            freq = self.freq[token][chunk['id']]
        except KeyError:
            freq = 0

        part2 = (freq + self.k1 * (1 - self.b + self.b * (len(chunk['tokens']) / self.avgdl)))

        return (freq * (self.k1 + 1)) / part2

    def calculate_IDF(self, token):
        N = len(self.chunks)
        nt = len(self.freq.get(token, []))
    
        return math.log(((N - nt + 0.5) / (nt + 0.5)) + 1)

    def score(self, query, chunk):
        score = 0
    
        for token in query:
            score += self.calculate_IDF(token) * self.calculate_TF(token, chunk)  
        return score

    def get_scores(self, query):
        scores = []
        for index,chunk  in enumerate(self.chunks):
            scores.append((index, self.score(query, chunk)))
        return sorted(scores, key=lambda chunk:chunk[1], reverse=True)

            
# bm = BM25(corpus)
# bm.calculate_freq()

# bm.calculate_avgdl()

# query = "what is rag"
# print(bm.get_scores(query.split()))

# from rank_bm25 import BM25Okapi

# b = BM25Okapi([list(chunk.values())[1] for chunk in corpus])
# scores = b.get_scores(query.split())
# print(scores)
