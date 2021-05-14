import json


def predict(target_word, dataset):
    if target_word not in dataset:
        print("사용되지 않은 단어입니다.")
        return 0

    s = sum(dataset[target_word].values())
    for i in ["society", "politics", "economic", "foreign", "culture", "digital"]:
        print(f"{i} : {round(dataset[target_word][i] / s * 100)}%")


with open("words_by_category.json", "r", encoding="utf8") as f:
    data = json.loads(f.read())

dic = {}

categories = list(data.keys())

for category in categories:
    words = list(data[category].keys())

    for word in words:
        if word not in dic:
            dic[word] = {
                "society": 0,
                "politics": 0,
                "economic": 0,
                "foreign": 0,
                "culture": 0,
                "digital": 0,
            }
        if word in dic:
            dic[word][category] += data[category][word]

predict(input("예측할 단어를 입력해주세요:"), dic)
