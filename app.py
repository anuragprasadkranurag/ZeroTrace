import flask
import firebase_admin
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from firebase_admin import credentials, firestore
app=Flask(__name__)
app.secret_key='your_secret_key'

cred=credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db=firestore.client()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/home")
def home():
    email=session.get('user')
    user_display=email
    if email:
        user_ref=db.collection('user').document(email)
        user_doc=user_ref.get()
        if user_doc.exists:
            user_data=user_doc.to_dict()
            user_display=user_data.get('name', email)
    return render_template("home.html", user=user_display)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user',None)
    return redirect(url_for('index'))

@app.route("/set-session", methods=['POST'])
def set_session():
    data=request.json
    email=data.get('email')
    session['user']=email
    if email:
        user_ref = db.collection('user').document(email)
        user_doc = user_ref.get()
        if not user_doc.exists:
            default_name = email.split('@')[0]
            user_ref.set({
                "name": default_name,
                "email": email
            }, merge=True)
    return jsonify({"status": "success"}), 200

@app.route("/analyze")
def analyze():
    if 'user' not in session:
        return redirect(url_for('login', next='analyze'))
    return render_template("analyze.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/profile")
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    email=session.get('user')
    user_ref=db.collection('user').document(email)
    user_doc=user_ref.get()
    user_data=user_doc.to_dict() if user_doc.exists else {"name": "New User", "email": email}
    return render_template("profile.html", user=user_data)

@app.route("/update-profile", methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    new_name=request.form.get('name')
    email=session.get('user')
    db.collection('user').document(email).set({
        "name": new_name,
        "email": email
    }, merge=True)
    return redirect(url_for('profile'))

if __name__ =='__main__':
    app.run(debug=True)