import sqlite3
import string
import re

conn = sqlite3.connect('beerfacts.sqlite')
cur = conn.cursor()

cur.execute('''SELECT alcohol, beer_name FROM facts_beer 
ORDER BY alcohol
DESC
LIMIT 100
''')

beers = dict()
for message_row in cur :
    beer_name = message_row[1]
    text = re.sub('[^A-Za-z]+', '', beer_name)
    text = text[:15]
    beers[text] = message_row[0]

print(beers)

x = sorted(beers, key=beers.get, reverse=True)

print(x)

highest = None
lowest = None
for k in x:
    if highest is None or highest < beers[k] :
        highest = beers[k]
    if lowest is None or lowest > beers[k] :
        lowest = beers[k]
print('Range of counts:',highest,lowest)

# Spread the font sizes across 20-100 based on the count
bigsize = 80
smallsize = 20

fhand = open('gword.js','w')
fhand.write("gword = [")
first = True
for k in x[:100]:
    if not first : fhand.write( ",\n")
    first = False
    size = beers[k]
    size = (size - lowest) / float(highest - lowest)
    size = int((size * bigsize) + smallsize)
    fhand.write("{text: '"+k+"', size: "+str(size)+"}")
fhand.write( "\n];\n")
fhand.close()

print("Output written to gword.js")
print("Open gword.htm in a browser to see the vizualization")
