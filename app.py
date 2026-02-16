from flask import Flask, render_template, request, jsonify, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def database_connection():
    return mysql.connector.connect(
        host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
        user="DU4VxkNw4kvgKbT.root",
        password="rEgdtkQLFPm58iYW",
        database="HAVEN_DB",
        port=4000,
        ssl_ca="isrgroot1x.pem",
        ssl_verify_identity=False
        )


try:
    test_conn = database_connection()
    if test_conn.is_connected():
        print("Ansluten till databasen!")
        test_conn.close()
except Exception as e:
    print(f"Not connected {e}")



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mina_bokningar.html')
def mina_bokningar():
    return render_template('mina_bokningar.html')

@app.route('/booking.html')
def booking():
    return render_template('booking.html')

@app.route('/rooms.html')
def rooms():
    return render_template('rooms.html')

@app.route('/kunder.html')
def kunder():
    return render_template('kunder.html')

@app.route('/api/selectRoom', methods=['POST']) #skapar varukorg med rum
def select_room():
    data = request.get_json()
    room_id = data.get('room_id')
    if 'basket' not in session:
        session['basket'] = []

    session['basket'].append(room_id)
    session.modified = True

    return jsonify({'status': "success"})

@app.route('/api/hasSelectedRooms') #kollar om det finns rum i varukorgen 
def selected_rooms():
    if 'basket' in session and len(session['basket']) > 0:
        return jsonify({'hasRooms': True})
    
    return jsonify({'hasRooms': False})

@app.route('/api/register', methods=['POST']) #kund registrering
def register():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    phone = data.get('phone')

    conn = database_connection()
    cursor = conn.cursor()

    sql = 'INSERT INTO kunder (firstname, lastname, email, phone) VALUES (%s, %s, %s, %s)'
    values = (firstname, lastname, email, phone)

    cursor.execute(sql, values)
    
    conn.commit()


    customer_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({'status': 'success', 'customer_id': customer_id})

if __name__ == "__main__":
    app.run(debug=True)