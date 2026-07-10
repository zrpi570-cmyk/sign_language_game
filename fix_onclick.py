import os
os.chdir("D:\\sign_language_game")
c = open("templates/learn-stage.html", "r", encoding="utf-8").read()

old = chr(39)+"+w.video_path+chr(39)+chr(44)+chr(39)+"+w.word+chr(39)+chr(44)+chr(39)+"+w.word_type+chr(39)+chr(44)+chr(39)+"+w.category+chr(39)
new = chr(39)+"+i+chr(39)
c = c.replace("onclick="+chr(34)+"ovm("+old+")"+chr(34), "onclick="+chr(34)+"ovm("+new+")"+chr(34))

open("templates/learn-stage.html", "w", encoding="utf-8").write(c)
print("Fixed onclick:", "ovm("+chr(39)+"+i+" in c)
