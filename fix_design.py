import sys
sys.stdout.reconfigure(encoding="utf-8")
c=open("templates/index.html","r",encoding="utf-8").read()
print("Read OK",len(c))
c=open("templates/index.html","r",encoding="utf-8").read()
