from flask import Flask, render_template, request, redirect, session, url_for
from peewee import SqliteDatabase, Model, IntegerField, CharField

app = Flask(__name__)
app.secret_key = 'some_random_secret_key'  # Nepieciešams sesijas saglabāšanai
db = SqliteDatabase('database.db')

class WaterIntake(Model):
    weight = IntegerField()  # Svars kg
    gender = CharField()
    amount = IntegerField()  # Ūdens daudzums ml

    class Meta:
        database = db

# Izveido datubāzi
with db:
    db.create_tables([WaterIntake])

def calculate_water_intake(weight, gender):
    if weight <= 0:
        return None  # Ja svars nav derīgs, atgriež None
    
    oz = weight * 0.85  # Aprēķinām ūdens daudzumu (oz)
    ml = round(oz * 29.5735)  # Pārvēršam oz uz ml un noapaļojam
    
    # Ņemam vērā dzimumu
    if gender.lower() == "female":
        ml *= 0.8  # Sievietēm koeficients ir 0.8
    
    return round(ml)  # Noapaļojam uz veselu skaitli

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log_water():
    weight = request.form.get("weight", type=int)
    gender = request.form.get("gender", type=str)

    if None in (weight, gender):
        return "Kļūda: Lūdzu, aizpildiet visus laukus!", 400  # Pārbauda, vai ir aizpildīti visi lauki
    
    if weight <= 0:
        return render_template('error.html', message="Kļūda: Lūdzu, ievadiet derīgu svaru!", back_url=url_for('index')), 400  # Error lapa ar atpakaļ pogu
    
    recommended_intake = calculate_water_intake(weight, gender)
    if recommended_intake is None:
        return render_template('error.html', message="Kļūda: Svars nav derīgs!", back_url=url_for('index')), 400  # Error lapa ar atpakaļ pogu
    
    WaterIntake.create(weight=weight, gender=gender, amount=recommended_intake)
    
    # Saglabājam rezultātu sesijā
    session['recommended_intake'] = recommended_intake
    
    return redirect("/total")

@app.route('/total')
def total_water():
    recommended_intake = session.get('recommended_intake', 0)  # Ņemam rezultātu no sesijas
    
    if recommended_intake == 0:
        return render_template('error.html', message="Kļūda: Nevar atrast rezultātu.", back_url=url_for('index')), 400
    
    return render_template('result.html', message="Ieteicamais ūdens daudzums aprēķināts!", recommended_intake=recommended_intake)

if __name__ == '__main__':
    app.run(debug=True)
