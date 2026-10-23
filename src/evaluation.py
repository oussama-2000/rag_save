from models import MinimalSource
import json


class Recall:
    def __init__(self):
        pass

    def calculate_IOU(self, source1: MinimalSource, source2: MinimalSource):
        start1 = source1["first_character_index"]
        end1 = source1["last_character_index"]

        start2 = source2["first_character_index"]
        end2 = source2["last_character_index"]

        union = max((end2 - start1), (end1 - start2))
        intersection = min((end1 - start2), (end2 - start1))

        return intersection / union if union else 0

    def calculate_question_recall(self, ground_truth: list[MinimalSource], retrieved: list[MinimalSource], at: int):

        valid = 0
        for g_source in ground_truth:
            for r_source in retrieved[:at]:
                if g_source["file_path"] == r_source["file_path"]:
                    if self.calculate_IOU(g_source, r_source) >= 0.05:
                        valid += 1
                        break

        return valid / len(ground_truth)

    
    def calculate_recall(self, student_search_result_path: str, dataset_ground_truth_path: str, at: int):
        with open(student_search_result_path, "r") as student_result_file:
            student_search_results = json.load(student_result_file)["search_results"]

        with open(dataset_ground_truth_path, "r") as dataset_file:
            dataset_ground_truth = json.load(dataset_file)["rag_questions"]

        recall = 0
        for question, result in zip(dataset_ground_truth, student_search_results):
            if question["question_id"] == result["question_id"]:
                recall += self.calculate_question_recall(question["sources"], result["retrieved_sources"], at)

        return recall / len(dataset_ground_truth)


        