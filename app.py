from flask import Flask, render_template, request, redirect, session
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import io
from db_config import get_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/create', methods=['GET', 'POST'])
def create_certificate():
    if request.method == 'POST':
        session['form_data'] = request.form
        return redirect('/review')
    return render_template('create_certificate.html')

@app.route('/review', methods=['GET', 'POST'])
def review_certificate():
    form_data = session.get('form_data')
    if not form_data:
        return redirect('/create')

    if request.method == 'POST':
        save_to_mysql(form_data)
        generate_pdf(form_data)
        return redirect('/home')

    return render_template('review_certificate.html', data=form_data)

def save_to_mysql(data):
    conn = get_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO certificates (name, rank, course, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        data['name'],
        data['rank'],
        data['course'],
        data['start_date'],
        data['end_date']
    ))
    conn.commit()
    conn.close()

def generate_pdf(data):
    filename = f"static/output/{data['name'].replace(' ', '_')}_certificate.pdf"
    c = canvas.Canvas(filename, pagesize=(2480, 3508))
    c.drawImage("static/certificate_bg.png", 0, 0, width=2480, height=3508)
    c.setFont("Helvetica-Bold", 72)
    c.drawString(600, 2000, data['name'])
    c.setFont("Helvetica", 48)
    c.drawString(600, 1900, data['rank'])
    c.drawString(600, 1800, data['course'])
    c.drawString(600, 1700, f"{data['start_date']} to {data['end_date']}")
    c.save()

if __name__ == '__main__':
    if not os.path.exists('static/output'):
        os.makedirs('static/output')
    app.run(debug=True)
