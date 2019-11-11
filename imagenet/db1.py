import sqlite3
import os

#os.system('clear')

#def searchItem(self, name):
conn = sqlite3.connect('demo1.sqlite')
c = conn.cursor()
name="apple"
cost = 0
c.execute("SELECT * fROM  material WHERE fname=?", (name,))

# c.execute("SELECT * fROM  material")
item = c.fetchall()
# item =c.fetchone()

for rows in item:
    print(item)
    print("id : ", rows[0])
    print("fname : ", rows[1])
    cost = rows[2]
    print("cost : ", rows[2])

print(cost)
conn.commit()
conn.close()
    #return cost

