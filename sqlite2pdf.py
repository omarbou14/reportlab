import numpy as np
import pandas as pd
from datetime import datetime
import locale
from sqlalchemy import (MetaData, Table, Column, Integer, Numeric, String,
DateTime, ForeignKey, create_engine, select)
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from math import floor
import qrcode
from pdf417gen import encode, render_image, render_svg

locale.setlocale(locale.LC_ALL, "fr_FR")

metadata = MetaData()

courant = Table('courant', metadata,
    Column('courant_id', Integer(), primary_key=True, autoincrement=True),
    Column('courant_val', String(), nullable=False),
    Column('created_on', DateTime(), default=datetime.now),
)

#importation de donnee
engine = create_engine('sqlite:///test3.db')
x = []
y = []
with engine.connect() as conn:
    s = courant.select().where(courant.c.created_on >= "2021-04-09 01:21:30").where(courant.c.created_on <= "2021-04-09 01:23:30")
    rp = conn.execute(s)
    results = rp.fetchall()
    for row in results:
        x.append(row[2])
        y.append(float(row[1]))

#conversion to np array
x = np.array(x)
y = np.array(y)

#courant figure
df = pd.DataFrame({"Courant (A)" : y}, index=x)
df.plot()
figure = plt.gcf()
figure.set_size_inches(8, 2)
plt.tight_layout(w_pad=10, h_pad=10)
plt.savefig('courant1.png' , dpi=250)

#{min, moy, max} figure
res = 120
min = []
moy = []
max = []
for i in range(len(y[::res])):
    min.append(y[i*res:(i+1)*res].min())
    moy.append(y[i*res:(i+1)*res].mean())
    max.append(y[i*res:(i+1)*res].max())
df = pd.DataFrame({"I min (A)" : min, "I moy (A)" : moy, "I max (A)" : max}, index=x[::res])
df.plot()
figure = plt.gcf()
figure.set_size_inches(8, 2)
plt.tight_layout(w_pad=10, h_pad=10)
plt.savefig('courant2.png' , dpi=250)

#cons figure
res = 60*18
cons = []
for i in range(len(y[::res])):
    cons.append(floor(y[i*res:(i+1)*res].sum()*220/36000)/100)

x_ = []
for _ in x[::res]:
    x_.append(_.strftime("%H:%M"))
df3 = pd.DataFrame({"Energie (KWh)" : cons}, index=x_)
df3.plot.bar()
figure = plt.gcf()
figure.set_size_inches(6, 3)
plt.tight_layout(w_pad=10, h_pad=10)
plt.savefig('cons.png' , dpi=250)

#qrcode
qr = qrcode.make("mellahavenir.com")
qr.save("qr.png")

#barcode
codes = encode("mellahavenir.com", columns=5, security_level=1)
image = render_image(codes)
image.save("barc.png")



#temps d'arrets
res = 20
ta = []
for i in range(len(y[::res])):
    if y[i*res:(i+1)*res].mean() < 10 :
        ta.append(0)
    else:
        ta.append(1)
i = 0
j = 0
for obj in ta:
    if obj == 0:
        i += 1
    j += 1
rta = float(i/j)*100
df4 = pd.DataFrame({"Temps d'arrets": ta}, index=x[::res])
df4.plot(title="TA: %.2f" %rta)
figure = plt.gcf()
figure.set_size_inches(8, 2)
plt.tight_layout(w_pad=10, h_pad=10)
plt.savefig('ta.png' , dpi=250)




#generation du pdf

def coord(x, y):
    x, y = x * A4[0], y * A4[1]
    return x, y

my_canvas = canvas.Canvas("test4.pdf", A4)


my_canvas.setFont("Courier", 20)
my_canvas.drawCentredString(*coord(0.5, 0.9), "Rapport de consommation")

my_canvas.setFont("Courier", 10)
date_d = x[0].strftime("%d-%b-%Y (%H:%M:%S)")
date_f = x[-1].strftime("%d-%b-%Y (%H:%M:%S)")

my_canvas.drawString(*coord(0.1, 0.85), "Date/Heure debut:")
my_canvas.drawString(*coord(0.1, 0.83), "Date/Heure  fin:")
my_canvas.drawString(*coord(0.3, 0.85), date_d)
my_canvas.drawString(*coord(0.3, 0.83), date_f)

my_canvas.drawImage("qr.png", *coord(0.06, 0.87), width=100, height=100)
my_canvas.drawImage("barc.png", *coord(0.6, 0.8), width=200)

my_canvas.setFont("Courier", 12)
my_canvas.drawString(*coord(0.1, 0.8), "Machine:")
my_canvas.drawString(*coord(0.2, 0.8), "OX-XXXX")

my_canvas.setFont("Courier-Bold", 15)
my_canvas.drawString(*coord(0.1, 0.75), "Graphe courant simple")
my_canvas.drawImage("courant1.png", *coord(0.15, 0.62), width=400, height=100)
my_canvas.drawString(*coord(0.1, 0.6), "Graphe courant complexe")
my_canvas.drawImage("courant2.png", *coord(0.15, 0.47), width=400, height=100)
my_canvas.drawString(*coord(0.1, 0.45), "Graphe consommation en KW")
my_canvas.drawImage("cons.png", *coord(0.15, 0.2), width=400, height=200)
my_canvas.drawString(*coord(0.12, 0.17), "Temps d'arrets")
my_canvas.drawImage("ta.png", *coord(0.17, 0.05), width=400, height=100)



my_canvas.save()


