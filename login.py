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
        print("Ansluten till databasen! login.py")
        test_conn.close()
except Exception as e:
    print(f"Not connected {e}")
