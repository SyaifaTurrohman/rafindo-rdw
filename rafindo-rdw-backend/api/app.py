import os
import json  # Tambahkan import json di bagian atas
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

if not firebase_admin._apps:
    
    if os.environ.get("FIREBASE_JSON"):
        firebase_info = json.loads(os.environ.get("FIREBASE_JSON"))
        cred = credentials.Certificate(firebase_info)
    else:
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cred_path = os.path.join(base_dir, "firebase-credentials.json")
        cred = credentials.Certificate(cred_path)
        
    firebase_admin.initialize_app(cred)

db = firestore.client()
# -------------------------------------------------

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password') 

    if not email or not password:
        return jsonify({"status": "error", "message": "Email dan password wajib diisi!"}), 400

    try:
        user_ref = db.collection('users').document(email)
        user_doc = user_ref.get()

        if user_doc.exists:
            user_data = user_doc.to_dict()
            password_database = user_data.get('password') 

            if password == password_database:
                return jsonify({
                    "status": "success",
                    "message": "Login berhasil",
                    "user": {
                        "email": user_data.get('email'),
                        "role": user_data.get('role'),
                        "angka_dasar": user_data.get('angka_dasar')
                    }
                }), 200
            else:
                return jsonify({"status": "error", "message": "Kata sandi salah!"}), 401
        else:
            return jsonify({"status": "error", "message": "User tidak ditemukan!"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    email = data.get('email')
    input_angka_str = data.get('angka')
    operasi = data.get('operasi')

    if not email or input_angka_str is None or not operasi:
        return jsonify({"status": "error", "message": "Data tidak lengkap!"}), 400

    if not input_angka_str.isdigit() or not (0 <= int(input_angka_str) <= 9):
        return jsonify({"status": "error", "message": "Input hanya menerima angka 0 hingga 9!"}), 400

    try:
        user_ref = db.collection('users').document(email)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"status": "error", "message": "User tidak valid!"}), 404

        angka_dasar = int(user_doc.to_dict().get('angka_dasar', 0))
        input_angka = int(input_angka_str)

        if operasi == 'tambah':
            hasil = angka_dasar + input_angka
        elif operasi == 'kurang':
            hasil = angka_dasar - input_angka
        else:
            return jsonify({"status": "error", "message": "Operasi tidak dikenal!"}), 400

        return jsonify({
            "status": "success",
            "angka_dasar": angka_dasar,
            "input_angka": input_angka,
            "operasi": operasi,
            "hasil": hasil
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)