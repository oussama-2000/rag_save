from models import MinimalSource

class Recall:
    def __init__(self):
        pass

    def calculate_UOI(self, source1: MinimalSource, souce2: MinimalSource):
        start1 = source1["start_index"]
        end1 = source1["end_index"]

        start2 = source1["start_index"]
        end2 = souce2["end_index"]

        union = max((end2 - start1), (end1 - start2))
        intersection = min((end1 - start2), (end2 - start1))

        return union / intersection if intersection else 0

    def calculate_recall(self, ground_truth: list[MinimalSource], retrieved: list[MinimalSource], at: int):

        for source in ground_truth:
            valid = 0
            for r_source in retrieved:
                if source["file_path"] == r_source["file_path"]:
                    if self.calculate_UOI(source, r_source) >= 0.5:
                        valid += 1
        