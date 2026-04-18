from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
translations = {
    'sv': {
        # Navigation
        'home': 'Hem',
        'create_account': 'Skapa konto',
        'my_bookings': 'Mina bokningar',
        'back_to_home': '← Tillbaka till start',

        # Index page
        'welcome_title': 'Välkommen till Nordic Haven Hotel',
        'welcome_text_1': 'Upptäck en plats där avkoppling möter elegans. På',
        'welcome_text_2': 'skapar vi minnesvärda vistelser, oavsett om du reser för arbete eller nöje.',
        'find_room_title': 'Hitta ditt perfekta rum',
        'check_in': 'Ankomstdatum',
        'check_out': 'Avresedatum',
        'guests': 'Antal gäster',
        'show_available_rooms': 'Visa lediga rum',

        # About
        'about_hotel_title': 'Om Nordic Haven Hotel',
        'about_hotel_text_1': 'Sedan mitten av 1900-talet har Nordic Haven Hotel välkomnat gäster till hjärtat av Göteborg. Med fokus på personlig service och hög komfort erbjuder vi en harmonisk miljö där tradition möter nutid.',
        'about_hotel_text_2': 'Våra rum är noggrant utformade för att passa olika behov – från bekväma enkelrum till rymliga sviter för längre vistelser.',

        # Rooms page
        'available_rooms': 'Tillgängliga rum',
        'book_now': 'Boka nu',
        'add_room': 'Lägg till rum',
        'sorry': 'Tyvärr!',
        'no_rooms': 'Vi har inga lediga rum för dessa datum och det antalet gäster.',

        # Customer / registration
        'customer_registration': 'Kundregistrering',
        'first_name': 'Förnamn',
        'last_name': 'Efternamn',
        'email': 'E-post',
        'phone': 'Telefonnummer',
        'register': 'Registrera',
        'first_name_placeholder': 'Skriv ditt förnamn',
        'last_name_placeholder': 'Skriv ditt efternamn',
        'email_placeholder': 'exempel@mail.com',
        'phone_placeholder': '070-1234567',
        'registration_success': 'Registreringen lyckades!',
        'redirecting_message': 'Du skickas vidare...',
        'generic_error': 'Något gick fel, försök igen.',

        # Booking page
        'customer_id': 'Kund-ID',
        'confirm_booking': 'Bekräfta bokning',
        'booking_summary': 'Bokningsöversikt',
        'selected_rooms': 'Valda rum',
        'per_night': '/ natt',
        'total_price': 'Totalt pris',
        'no_active_booking': 'Ingen aktiv bokning hittades.',
        'booking_info_error': 'Kunde inte hämta bokningsinformation.',
        'booking_confirmed_message': 'Bokningen är bekräftad! Tack för din bokning.',
        'booking_failed_message': 'Bokningen misslyckades',
        'technical_error': 'Ett tekniskt fel uppstod.',

        # My bookings page
        'show_bookings': 'Visa bokningar',
        'booking_id': 'Bokning',
        'room_id': 'Rum',
        'room_type': 'Typ',
        'price': 'Pris',
        'actions': 'Åtgärder',
        'status': 'Status',
        'upcoming_bookings': 'Kommande bokningar',
        'past_bookings': 'Tidigare bokningar',
        'completed_status': 'Genomförd',
        'no_bookings_found': 'Inga bokningar hittades',
        'booking_fetch_error': 'Fel vid hämtning av bokningar',
        'confirm_cancel': 'Vill du avboka?',
        'cancel_error': 'Fel vid avbokning',

        # Actions / general
        'cancel': 'Avboka',

        # Footer
        'footer_rights': 'Alla rättigheter förbehållna.',

        # Toast / messages
        'choose_room': 'Välj minst ett rum innan du fortsätter',
        'room_added': 'Rummet har lagts till i din bokning',
        'error_occurred': 'Fel inträffade',
        'cannot_add_room': 'Kunde inte lägga till rummet',
        'booking_info_missing': 'Bokningsinformation saknas.',
        'booking_success': 'Bokningen lyckades!',
        'booking_failed': 'Bokningen misslyckades.',
        'cancel_success': 'Bokningen har avbokats!',
        'empty_cart': 'Varukorgen är tom.'
    },

    'en': {
        # Navigation
        'home': 'Home',
        'create_account': 'Create account',
        'my_bookings': 'My bookings',
        'back_to_home': '← Back to home',

        # Index page
        'welcome_title': 'Welcome to Nordic Haven Hotel',
        'welcome_text_1': 'Discover a place where relaxation meets elegance. At',
        'welcome_text_2': 'we create memorable stays, whether you travel for business or leisure.',
        'find_room_title': 'Find your perfect room',
        'check_in': 'Check-in date',
        'check_out': 'Check-out date',
        'guests': 'Number of guests',
        'show_available_rooms': 'Show available rooms',

        # About
        'about_hotel_title': 'About Nordic Haven Hotel',
        'about_hotel_text_1': 'Since the mid-1900s, Nordic Haven Hotel has welcomed guests to the heart of Gothenburg. With a focus on personal service and high comfort, we offer a harmonious environment where tradition meets modern life.',
        'about_hotel_text_2': 'Our rooms are carefully designed to suit different needs – from comfortable single rooms to spacious suites for longer stays.',

        # Rooms page
        'available_rooms': 'Available Rooms',
        'book_now': 'Book now',
        'add_room': 'Add room',
        'sorry': 'Sorry!',
        'no_rooms': 'We do not have any available rooms for these dates and number of guests.',

        # Customer / registration
        'customer_registration': 'Customer Registration',
        'first_name': 'First name',
        'last_name': 'Last name',
        'email': 'Email',
        'phone': 'Phone number',
        'register': 'Register',
        'first_name_placeholder': 'Enter your first name',
        'last_name_placeholder': 'Enter your last name',
        'email_placeholder': 'example@mail.com',
        'phone_placeholder': '070-1234567',
        'registration_success': 'Registration successful!',
        'redirecting_message': 'You are being redirected...',
        'generic_error': 'Something went wrong, please try again.',

        # Booking page
        'customer_id': 'Customer ID',
        'confirm_booking': 'Confirm booking',
        'booking_summary': 'Booking summary',
        'selected_rooms': 'Selected rooms',
        'per_night': '/ night',
        'total_price': 'Total price',
        'no_active_booking': 'No active booking was found.',
        'booking_info_error': 'Could not retrieve booking information.',
        'booking_confirmed_message': 'Your booking is confirmed! Thank you for your reservation.',
        'booking_failed_message': 'Booking failed',
        'technical_error': 'A technical error occurred.',

        # My bookings page
        'show_bookings': 'Show bookings',
        'booking_id': 'Booking',
        'room_id': 'Room',
        'room_type': 'Type',
        'price': 'Price',
        'actions': 'Actions',
        'status': 'Status',
        'upcoming_bookings': 'Upcoming bookings',
        'past_bookings': 'Past bookings',
        'completed_status': 'Completed',
        'no_bookings_found': 'No bookings found',
        'booking_fetch_error': 'Error fetching bookings',
        'confirm_cancel': 'Do you want to cancel?',
        'cancel_error': 'Error while canceling',

        # Actions / general
        'cancel': 'Cancel',

        # Footer
        'footer_rights': 'All rights reserved.',

        # Toast / messages
        'choose_room': 'Please select at least one room before continuing',
        'room_added': 'The room has been added to your booking',
        'error_occurred': 'An error occurred',
        'cannot_add_room': 'Could not add the room',
        'booking_info_missing': 'Booking information is missing.',
        'booking_success': 'Booking successful!',
        'booking_failed': 'Booking failed.',
        'cancel_success': 'Booking has been canceled!',
        'empty_cart': 'The cart is empty.'
    }
}

def get_language():
    lang = session.get('language', 'sv')
    return translations.get(lang, translations['sv'])
@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in translations:
        session['language'] = lang
        session.modified = True
    return jsonify({'status': 'success'})

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
    t = get_language()
    return render_template('index.html', t=t)

@app.route('/booking.html')
def booking():
    t = get_language()
    return render_template('booking.html', t=t)

@app.route('/mina_bokningar.html')
def mina_bokningar_page():
    t = get_language()
    return render_template('mina_bokningar.html', t=t)

@app.route('/rooms.html')
def rooms():
    
    if request.args.get('check_in_date'):
        session['check_in_date'] = request.args.get('check_in_date')
        session['check_out_date'] = request.args.get('check_out_date')
        session['antal_personer'] = request.args.get('antal_personer')
        session.modified = True

    in_date = session.get('check_in_date')
    out_date = session.get('check_out_date')
    guests = session.get('antal_personer')

    t = get_language()

    if not in_date or not out_date or not guests:
        return t['booking_info_missing'], 400

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

    return render_template('rooms.html', rooms=lediga_rum, t=t)




@app.route('/kunder.html')
def kunder():
    t = get_language()
    return render_template('kunder.html', t=t)

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

@app.route('/api/register', methods=['POST']) #kund registrering
def register():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    phone = data.get('phone')

    conn = database_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT kund_id FROM kunder WHERE email = %s", (email,))
    existing_customer = cursor.fetchone()
    if existing_customer:
        customer_id = existing_customer[0]
        
        
    else:
        sql = 'INSERT INTO kunder (firstname, lastname, email, phone) VALUES (%s, %s, %s, %s)'
        values = (firstname, lastname, email, phone)

        cursor.execute(sql, values)
        
        conn.commit()


        customer_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({'status': 'success', 'customer_id': customer_id})


@app.route('/api/mina_bokningar.html', methods=['GET']) #hämtar bokningar för en kund
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
    if 'basket' not in session or len(session['basket']) == 0:
        return jsonify({'status': 'error', 'message': 'Varukorgen är tom.'})

    check_in_str = session.get('check_in_date')
    check_out_str = session.get('check_out_date')
    nights_count = 1

    if check_in_str and check_out_str:
        try:
            check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d')
            check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d')
            nights_count = (check_out_date - check_in_date).days
            if nights_count <= 0:
                nights_count = 1
        except ValueError:
            nights_count = 1

    try:
        conn = database_connection()
        cursor = conn.cursor()

        rooms_in_basket = ', '.join(['%s'] * len(session['basket']))
        sql = f"SELECT id, room_name, price, image FROM rum WHERE id IN ({rooms_in_basket})"
        cursor.execute(sql, tuple(session['basket']))
        rum_data = cursor.fetchall()

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

        return jsonify({
            'status': 'success',
            'rooms': rooms_list,
            'total_price': total_price,
        })

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