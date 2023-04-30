from flask import Flask, request, redirect, url_for
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
bcrypt = Bcrypt(app)
client = MongoClient("mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.test

@app.route('/')
def index():
    ip_address = request.remote_addr
    record = db.ip_addresses.find_one({'ip_address': ip_address})
    if record:
        last_request_time = record['last_request_time']
    else:
        last_request_time = None
    db.ip_addresses.update_one({'ip_address': ip_address}, {'$set': {'last_request_time': datetime.utcnow()}}, upsert=True)
    return f'Your IP address is {ip_address}. Last request time: {last_request_time}'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({'username': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    else:
        return '''
        <form method="post">
            <input type="text" name="username" placeholder="Username">
            <input type="password" name="password" placeholder="Password">
            <input type="submit" value="Login">
        </form>
        '''

if __name__ == '__main__':
    app.run()
