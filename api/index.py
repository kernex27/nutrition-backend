from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "Hello from Flask on Vercel!"}

# Vercel akan mencari variabel "app" di file ini
if __name__ == "__main__":
    app.run()
