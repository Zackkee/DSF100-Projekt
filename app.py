from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from datetime import datetime

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
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', today=today)

@app.route('/booking.html')
def booking():
    return render_template('booking.html')

@app.route('/Mina_bokningar.html')
def mina_bokningar_page():
    return render_template('Mina_bokningar.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/rooms.html')
def rooms():

    #spara datum och antal personer i sessionen
    if request.args.get('check_in_date'):
        session['check_in_date'] = request.args.get('check_in_date')
        session['check_out_date'] = request.args.get('check_out_date')
        session['antal_personer'] = request.args.get('antal_personer')
        session.modified = True


    in_date = session['check_in_date']
    out_date = session['check_out_date']
    guests = session['antal_personer']


    conn = database_connection()
    cursor = conn.cursor()

    sql = """
        SELECT * FROM rum 
        WHERE capacity >= %s 
        AND id NOT IN (
            SELECT room_id FROM bokningar 
            WHERE check_in < %s AND check_out > %s
        )
    """
    
    cursor.execute(sql, (guests, out_date, in_date))
    lediga_rum = cursor.fetchall()

    cursor.close()
    conn.close()

    
    return render_template('rooms.html', rooms=lediga_rum)


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

@app.route('/api/hasSelectedRooms') #checkar varukorg
def selected_rooms():
    if 'basket' in session and len(session['basket']) > 0:
        return jsonify({'hasRooms': True})
    
    return jsonify({'hasRooms': False})

@app.route('/api/register', methods=['POST']) 
def register():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    conn = database_connection()
    cursor = conn.cursor()

    #Kolla om e-posten redan finns
    cursor.execute("SELECT kund_id FROM kunder WHERE email = %s", (email,))
    existing_customer = cursor.fetchone()
    
    if existing_customer:
        cursor.close()
        conn.close()
        return jsonify({'status': 'error', 'message': 'E-posten är redan registrerad.'})
        
    else:
        #Spara i databas
        sql = 'INSERT INTO kunder (firstname, lastname, email, phone, password) VALUES (%s, %s, %s, %s, %s)'
        values = (firstname, lastname, email, phone, password)

        cursor.execute(sql, values)
        conn.commit()

        customer_id = cursor.lastrowid
        
        session['customer_id'] = customer_id
        session['customer_email'] = email
        session.modified = True

    cursor.close()
    conn.close()

    return jsonify({'status': 'success', 'customer_id': customer_id})


@app.route('/api/Mina_bokningar.html', methods=['GET']) #hämtar bokningar för en kund
def get_bookings():
    email = request.args.get('email')
    
    conn = database_connection()
    cursor = conn.cursor()

    sql = """
        SELECT 
            bokningar.id AS booking_id, 
            bokningar.room_id AS id, 
            rum.room_name, 
            bokningar.check_in, 
            bokningar.check_out,
            rum.price
        FROM bokningar
        JOIN rum ON bokningar.room_id = rum.id
        JOIN kunder ON bokningar.customer_id = kunder.kund_id
        WHERE kunder.email = %s
    """
    cursor.execute(sql, (email,))
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    bookings_list = []
    for b in bookings:
        bookings_list.append({
            'booking_id': b[0],
            'room_id': b[1],
            'room_name': b[2],
            'check_in': b[3].strftime('%Y-%m-%d'),
            'check_out': b[4].strftime('%Y-%m-%d'),
            'price': float(b[5])
        })

    return jsonify({'status': 'success','bookings': bookings_list})


#BEKRÄFTAR BOKNINGEN OCH LÄGGER IN DEN I DATABASEN
@app.route('/api/bookRoom', methods=['POST'])
def book_room():
    data = request.get_json()
    customer_id = data.get('customer_id')

    # sparar datum
    check_in = session.get('check_in_date')
    check_out = session.get('check_out_date')

    try:
        conn = database_connection()
        cursor = conn.cursor()

        for room_id in session['basket']:

            #kollar databas på valda rum så att de inte är bokade
            sql = """SELECT room_id FROM bokningar 
                WHERE room_id = %s AND check_in < %s AND check_out > %s"""
            
            cursor.execute(sql, (room_id, check_out, check_in))
            already_booked_room = cursor.fetchone()

            if already_booked_room:
                return jsonify({'status': 'error', 'message': 'Ett av rummen är tyävrr redan bokade'})

            sql = """
                INSERT INTO bokningar (room_id, customer_id, check_in, check_out) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (room_id, customer_id, check_in, check_out,))
        
        conn.commit()
        cursor.close()
        conn.close()

        session.pop('basket', None)
        session.modified = True

        return jsonify({'status': 'success'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Boknningen misslyckades. Försök igen senare.'})
    

@app.route('/api/getBookingSummary', methods=['GET'])
def get_booking_summary():
    #Kolla om det finns rum i varukorgen
    if 'basket' not in session or len(session['basket']) == 0:
        return jsonify({'status': 'error', 'message': 'Varukorgen är tom.'})

    
    check_in_str = session.get('check_in_date')
    check_out_str = session.get('check_out_date')
    
    if check_in_str and check_out_str:
        try:
            check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d')
            nights_count = (check_out_date - check_in_date).days
            if nights_count <= 0: nights_count = 1
        except ValueError:
            pass

    try:
        conn = database_connection()
        cursor = conn.cursor()

        rooms_in_basket = ', '.join(['%s'] * len(session['basket']))
        
        sql = f"SELECT id, room_name, price, image FROM rum WHERE id IN ({rooms_in_basket})"
        cursor.execute(sql, tuple(session['basket']))
        rum_data = cursor.fetchall() #sparar datan i rum_data
        
        cursor.close()
        conn.close()

        rooms_list = []
        total_price = 0

        for r in rum_data:
            room_price = float(r[2]) 
            rooms_list.append({
                'name': r[1],      
                'price': room_price,
                'image': r[3]      
            })
            total_price += (room_price * nights_count)

        return jsonify({'status': 'success','rooms': rooms_list,'total_price': total_price,})

    except Exception as e:
        print(f"Något gick fel: {e}")
        return jsonify({'status': 'error'})
    


#AVBOKNING
@app.route('/api/cancelBooking', methods=['POST'])
def cancel_booking():
    data = request.get_json()
    booking_id = data.get('booking_id')
    try:
        conn = database_connection()
        cursor = conn.cursor()

        sql = "DELETE FROM bokningar WHERE id = %s"
        cursor.execute(sql, (booking_id,))
        
        conn.commit()
        
        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Bokningen har nu avbokats!'})

    except Exception as e:
        print(f"Går ej att avboka: {e}")
        return jsonify({'status': 'error'})
    

if __name__ == "__main__":
    app.run(debug=True)