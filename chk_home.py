import os
os.chdir("D:\\sign_language_game")
with open("templates/index.html", "r", encoding="utf-8") as f:
    content = f.read()
print("Read:", len(content), "bytes")
