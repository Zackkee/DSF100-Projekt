from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

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
        print("Connected")
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

if __name__ == "__main__":
    app.run(debug=True)