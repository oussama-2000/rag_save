from transformers import pipeline

class Generation:
    def __init__(self):
        self.pipeline = pipeline("text-generation", "Qwen/Qwen3-0.6B")

    def answer(self, context, query):
        prompts = [
            {
                "role": "system",
                "content": "Answer question using only context.\nIf there is no relation between question and context say just I don't know."
            },
            {
                "role": "user",
                "content": f"\ncontext:{context}\nquestion: {query}\n/no_think"
            }
        ]

        return self.pipeline(prompts, return_full_text=False)[0]['generated_text'].split("</think>", 1)[1]

