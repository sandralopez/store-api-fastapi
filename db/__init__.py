import json

file = open("db/data.json")
data = json.load(file)

file.close()