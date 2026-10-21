import json

with open("src/stop_words.txt", "r") as file:
    data = file.read()
    with open("src/stop_words.json", "w") as j:
        json.dump({"data": [i for i in data.split() if len(i) > 2]}, j)

    