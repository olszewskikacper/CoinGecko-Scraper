from io import BytesIO
import sys
from flask import Flask, render_template, session, url_for, jsonify, redirect, request, flash
import csv
import secrets
sys.path.append('./')
from backend.Scraping.main import get_random_crypto, scrape_data, download_csv_to_folder, read_users, write_user
import os
import pandas as pd
import mysql.connector
from flask import send_file

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 


app.secret_key = secrets.token_hex(16)

db_config = {
    'user': 'root',
    'password': 'admin',
    'host': 'localhost',
    'database': 'usersdb'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('start.html')

@app.route('/home')
def home():
    if not session.get('username'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generate():
    if not session.get('username'):
        return redirect(url_for('login'))
    row = get_random_crypto()
    return render_template('index.html', row=row)

@app.route('/save-data', methods=['POST'])
def save_data():
    directory = request.form.get('directory')
    download_csv_to_folder(directory)
    return redirect('/home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = {"username": username, "password": password}
        write_user(user)
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = read_users()
        if (username, password) in [(u['username'], u['password']) for u in users]:
            session['username'] = username
            return redirect('/home')
        else:
            flash('Invalid username or password. Please try again.', category='error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logout successful!', category='success')
    return redirect(url_for('login'))

@app.route('/all-crypto')
def all_crypto():
    if not session.get('username'):
        return redirect(url_for('login'))

    try:
        connection = get_db_connection()
        query = "SELECT * FROM crypto_data"
        df = pd.read_sql(query, connection)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash("Failed to retrieve data from the database.", category='error')
        return redirect(url_for('home'))
    finally:
        if connection.is_connected():
            connection.close()

    if df.empty:
        flash("No data available.", category='error')
        return redirect(url_for('home'))

    all_cryptos = df.to_dict(orient='records')
    return render_template('all_crypto.html', all_cryptos=all_cryptos)

@app.route('/add-to-favorites', methods=['POST'])
def add_to_favorites():
    if not session.get('username'):
        return jsonify({'success': False, 'message': 'Not logged in'})

    crypto_name = request.json.get('name')
    username = session.get('username')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            cursor.execute("INSERT INTO favorites (user_id, crypto_name) VALUES (%s, %s) ON DUPLICATE KEY UPDATE crypto_name=crypto_name", (user_id, crypto_name))
            connection.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'User not found'})

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'success': False, 'message': 'Database error'})
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/profile')
def profile():
    if not session.get('username'):
        return redirect(url_for('login'))

    username = session.get('username')

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            user_id = user['id']
            cursor.execute("SELECT crypto_name FROM favorites WHERE user_id = %s", (user_id,))
            favorites = cursor.fetchall()
            favorite_names = [favorite['crypto_name'] for favorite in favorites]

            all_cryptos_df = pd.read_sql("SELECT * FROM crypto_data", connection)
            favorites_list = all_cryptos_df[all_cryptos_df['name'].isin(favorite_names)].to_dict(orient='records')

            return render_template('profile.html', favorites=favorites_list)
        else:
            return redirect(url_for('login'))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return render_template('profile.html', favorites=[])
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/remove-from-favorites', methods=['POST'])
def remove_from_favorites():
    if not session.get('username'):
        return jsonify({'success': False, 'message': 'Not logged in'})

    crypto_name = request.json.get('name')
    username = session.get('username')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            cursor.execute("DELETE FROM favorites WHERE user_id = %s AND crypto_name = %s", (user_id, crypto_name))
            connection.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'User not found'})

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'success': False, 'message': 'Database error'})
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/download-csv')
def download_csv():
    try:
        connection = get_db_connection()
        query = "SELECT * FROM crypto_data"
        df = pd.read_sql(query, connection)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flash("Failed to retrieve data from the database.", category='error')
        return redirect(url_for('home'))
    finally:
        if connection.is_connected():
            connection.close()

    if df.empty:
        flash("No data available.", category='error')
        return redirect(url_for('home'))

    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='Crypto_Data.csv'
    )


if __name__ == '__main__':
    scrape_data()
    app.run()
