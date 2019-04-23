import sys
  
f = open("main.c", 'r')
content = f.readlines()
f.close()
flipflop = 0
elements = [[]]

for i in content:
    line = i.rstrip()
    if (line.find("/* Section start */") > 0):
        flipflop = 1
        elements.append([])
        continue
    if (line.find("/* Section end */") > 0):
        flipflop = 0
        continue
    if flipflop:
      if len(line) > 1:
        elements[-1].append(line)
        

for i in range(0, len(elements)):
    #print "/* Byte start */"
    for ii in reversed(elements[i]):
      print ii
    #print "/* Byte end */"

