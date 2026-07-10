import os
os.chdir("D:\\sign_language_game")
with open("templates/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("Total lines:", len(lines))
# Check for key elements
for i, l in enumerate(lines):
    if "three-container" in l:
        print(f"Line {i}: has three-container")
    if "hero-bd" in l or "hero-badge" in l:
        print(f"Line {i}: has hero badge")
    if "authSubmitBtn" in l:
        print(f"Line {i}: has authSubmitBtn")
    if "authToggleBtn" in l:
        print(f"Line {i}: has authToggleBtn")
    if "loadStats" in l:
        print(f"Line {i}: has loadStats")
