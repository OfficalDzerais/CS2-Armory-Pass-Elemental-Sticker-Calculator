from flask import Flask, render_template, request, redirect
from peewee import SqliteDatabase, Model, IntegerField, DateTimeField
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# Datubāze
db = SqliteDatabase("water_intake.db")

class WaterIntake(Model):
    amount = IntegerField()  # Ūdens daudzums ml
    timestamp = DateTimeField(default=datetime.now)  # Kad tika pievienots

    class Meta:
        database = db

db.connect()
db.create_tables([WaterIntake], safe=True)  # Izveido tabulu, ja nav

# 📌 Sākumlapa (Forma ievadei)
@app.route("/")
def index():
    return render_template("index.html")

# 📌 Reģistrēt ūdens patēriņu
@app.route("/log", methods=["POST"])
def log_water():
    amount = request.form.get("amount")
    
    if amount:
        WaterIntake.create(amount=int(amount))  # Saglabā datubāzē
        return render_template("result.html", message=f"Pievienots: {amount} ml ūdens!")
    
    return redirect("/")

# 📊 Statistikas lapa (Vizualizācija)
@app.route("/stats")
def stats():
    # Nolasām datus no DB
    data = pd.DataFrame(list(WaterIntake.select().dicts()))

    if not data.empty:
        data["hour"] = data["timestamp"].apply(lambda x: x.hour)  # Grupējam pa stundām
        summary = data.groupby("hour")["amount"].sum()

        # 🔹 Zīmējam grafiku
        plt.figure(figsize=(8, 4))
        plt.bar(summary.index, summary.values, color="blue")
        plt.xlabel("Stunda")
        plt.ylabel("Ūdens daudzums (ml)")
        plt.title("Ūdens patēriņš dažādās stundās")
        plt.xticks(range(24))

        # Saglabājam kā attēlu
        img_path = os.path.join("static", "water_intake.png")
        plt.savefig(img_path)
        plt.close()

        return render_template("stats.html", image=img_path)

    return render_template("stats.html", image=None)

# 🚀 Palaid Flask serveri
if __name__ == "__main__":
    app.run(debug=True)
