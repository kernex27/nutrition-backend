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
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def root():
    return jsonify({"message": "NIRMAS API is running 🚀"})

@app.route("/users/me")
def get_user():
    return jsonify({
        "id": 1,
        "name": "Demo User",
        "email": "demo@example.com"
    })

if __name__ == "__main__":
    # Railway menggunakan PORT dari environment variable
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
