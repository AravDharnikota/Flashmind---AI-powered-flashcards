from flask import Flask, render_template, session, redirect, url_for, request, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.parse import quote_plus
from dotenv import load_dotenv
from openai import OpenAI
import json
from bson import ObjectId
from passlib.hash import sha256_crypt
from datetime import datetime
import pdfplumber
import os
import certifi

load_dotenv()

client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

password = quote_plus(os.getenv("MONGO_PASSWORD"))
user = os.getenv("MONGO_USER")
uri = f"mongodb+srv://{user}:{password}@cluster0.29rc5zg.mongodb.net/?appName=Cluster0"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
db = client['flashmind']

def get_text(file):
    if file.filename.endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
        return text


@app.route('/',methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        if 'signup-btn' in request.form:
            existing_user = db.users.find_one({'Email':request.form['email-signup']})
            if existing_user:
                flash("Email already exists! Please log in.", "danger")
                return redirect('/')
            else:
                document = {}
                document['First Name'] = request.form['fname']
                document['Last Name'] = request.form['lname']
                document['Email'] = request.form['email-signup']
                document['Password'] =  sha256_crypt.hash(request.form['password-signup'])
                document['Timestamp'] = datetime.now()
                db.users.insert_one(document)
                flash("Signup Successful!", "success")
                return redirect('/home')
        if 'login-button' in request.form:
            email = request.form['email-login']
            password = request.form['password-login']

            user = db.users.find_one({'Email':email})
            if(user):
                if(sha256_crypt.verify(password, user['Password'])):
                    session['email'] = email
                    session['name'] = user['First Name']
                    return redirect('/home')
                else:
                    flash("Incorrect password. Please try again.", "danger")
                    return redirect('/')
            else:
                flash("No account exists. Please sign up.", "danger")
                return redirect('/')
            
@app.route('/home',methods=["GET", "POST"])
def home():
    if 'email' not in session:
        flash('You must login')
        return redirect('/')
    sets = list(db.sets.find({'user_email': session['email']}))
    return render_template('home.html', sets=sets)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/new-set', methods=["POST"])
def new_set():
    title = request.form.get('title', 'Untitled Set')
    result = db.sets.insert_one({
        'user_email': session['email'],
        'title': title,
        'flashcards': [],
        'created_at': datetime.now()
    })
    print(title)
    return redirect(f'/set/{result.inserted_id}')

@app.route('/set/<id>')
def view_set(id):
    set_doc = db.sets.find_one({'_id': ObjectId(id)})
    return render_template('/flashcards-view.html', set=set_doc)

@app.route('/set/<id>/upload', methods=['POST'])
def upload(id):
    if request.method == 'POST':
        files = request.files.getlist('files')
        for file in files:
            text = get_text(file)
            db.sets.update_one(
            {'_id': ObjectId(id)},
            {'$push': {'files': {'name': file.filename, 'text': text}}}
            )
        print("loaded")
        set_doc = db.sets.find_one({'_id': ObjectId(id)})
        all_text = ' \n'.join([f['text'] for f in set_doc.get('files', [])])

        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a flashcard generator. You take in notes and course content and turn it into flashcards for a high school or college student to study with. Return only a JSON array like: [{'question': '...', 'answer': '...'}]. No extra text. Decide based on the information density and amount provided in the upload the appropriate amount of flashcards needed. Make sure to cover all concepts that are in the notes the user provides."},
                {"role": "user", "content": f"Make flashcards from these notes:{all_text}"}
            ]
        )

        raw = response.choices[0].message.content
        raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
        flashcards = json.loads(raw)

        db.sets.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'flashcards': flashcards}}
        )


        return redirect(f"/set/{id}")
    
@app.route('/set/<id>/delete-file', methods=['POST'])
def delete_file(id):
    filename = request.form['filename']
    db.sets.update_one(
    {'_id': ObjectId(id)},
    {'$pull': {'files': {'name': filename}}},
    )
    return redirect(f"/set/{id}")

@app.route('/set/<id>/flag/<int:index>', methods=['POST'])
def flag_card(id, index):
    set_doc = db.sets.find_one({'_id': ObjectId(id)})
    current = set_doc['flashcards'][index].get('flagged', False)
    db.sets.update_one(
        {'_id': ObjectId(id)},
        {'$set': {f"flashcards.{index}.flagged":True}} 
    )
    return '', 204


    
if __name__ == '__main__':
    app.run(debug=True)