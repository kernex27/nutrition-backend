from flask import Flask, jsonify, request

app = Flask(__name__)

# Root endpoint
@app.route("/")
def root():
    return jsonify({"message": "NIRMAS API is running 🚀"})

# Contoh endpoint user
@app.route("/users/me", methods=["GET"])
def get_user_me():
    # Dummy response, nanti bisa diganti dengan DB query
    return jsonify({
        "id": 1,
        "name": "Demo User",
        "email": "demo@example.com"
    })

# Contoh endpoint foods
@app.route("/foods", methods=["GET"])
def get_foods():
    search = request.args.get("search", "")
    return jsonify([
        {"id": 1, "name": "Nasi Putih", "kcal": 130},
        {"id": 2, "name": "Ayam Bakar", "kcal": 165}
    ])

# Tambahkan endpoint lain sesuai kebutuhan (dummy)
