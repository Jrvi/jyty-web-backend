from datetime import datetime, timedelta
from flask import Flask, request, Response, session
from flask_sqlalchemy import SQLAlchemy
import json
from dotenv import load_dotenv
import os
import bcrypt
from flask_cors import CORS
import jwt

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)


class User(db.Model):
    """
    Käyttäjän luokka

    Atribuutit:
        id (int) Käyttäjän tunnus
        username (str): Käyttäjän nimi
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """
        Kryptaa salasanan

        :param password: Käyttäjän antama salasana
        :return: Kryptattu salasana
        """
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """
        Tarkistaa salasanan

        :param password: Käyttäjän antama salasana
        :return: onko salasana oikein, True/False
        """
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    """
    Tapahtuman luokka

    attribuutit:
        id (int): Tapahtuman tunnus
        name (str): Tapahtuman nimi
        description (str): Tapahtuman kuvaus
        date (str): Päiväys
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.Date, unique=False, nullable=False)

    def __repr__(self):
        return f'<Event {self.name}>'


class Announcement(db.Model):
    """
    Tiedoteen luokka

    attribuutit:
        id (int): Tiedoteen tunnus
        title (str): Tiedotetunnuksen otsikko
        description (str): Tiedotetunnuksen kuvaus
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=False)

    def __repr__(self):
        return f'<Announcement {self.title}>'


class PageContent(db.Model):
    """
    Sivun sisällön luokka

    Attributes:
        id (int): Sisällön tunnus
        tag (str): Tunnus mikä sivu on kyseessä
        content (str): Sivun sisältö
    """
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(80), unique=False, nullable=False)
    content = db.Column(db.Text)

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.tag}>'


with app.app_context():
    db.create_all()

def authenticate_request():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, 'Missing token'  # Palauttaa tuplen

    try:
        # Tokenin tarkistaminen "Bearer <token>"-muodossa
        token = auth_header.split()[1]
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return decoded_token, None  # Palauttaa tokenin ja virheenä None
    except jwt.ExpiredSignatureError:
        return None, 'Token has expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'

@app.route('/')
def index():
    """
    Ompahan olemassa

    :return: merkkijonon
    """
    return json.dumps({'message': 'Miksi sä tätä kutsut?'})


@app.route('/api/user', methods=['POST'])
def user():
    """
    Rajapinta käyttäjän luomiseen

    :return: onnistumisen tilan
    """
    try:
        decoded_token, error = authenticate_request()
        if error:
            return Response(json.dumps({'error': 'Invalid token'}), status=401, mimetype='application/json')
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return Response(json.dumps({'message': 'User created successfully!'}), status=201, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=400, mimetype='application/json')


@app.route('/login', methods=['POST'])
def login():
    """
    Rajapinta kirjautumiseen

    :return: Token
    """
    data = request.get_json()
    if not data:
        return Response(json.dumps({'error': 'Invalid request'}), status=400, mimetype='application/json')
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(minutes=30) # Token vanhenee 30 minuutissa
        }
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return Response(json.dumps({'token': token, 'username':username, 'password': password}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Invalid username or password'}), status=401, mimetype='application/json')


@app.route('/api/event', methods=['GET', 'POST'])
def event():
    """
    Rajapinta tapahtuman luomiseen ja hakemiseen

    :return:
    """
    # Jos request method on GET haetaan kaikki tapahtumat
    if request.method == 'GET':
        # Hakee kannasta kaikki tapahtumat
        events = Event.query.all()
        # Muutetaan tapahtumat python listaksi
        events_list = []
        for event in events:
            events_list.append({
                'id': event.id,
                'name': event.name,
                'description': event.description,
                'date': event.date.isoformat()
            })
        # Palautetaan tapahtumat
        return Response(json.dumps(events_list), mimetype='application/json'), 200
    else:
        decoded_token, error = authenticate_request()
        if error:
            return Response(json.dumps({'error': 'Invalid token'}), status=401, mimetype='application/json')
        try:
            # otetaan data vastaan
            data = request.get_json()
            name = data['name']
            description = data['description']
            date = datetime.strptime(data['date'], '%Y-%m-%d')
            # Luodaan tapahtuma luokan avulla
            event = Event(name=name, description=description, date=date)
            # Tallennetaan tapahtuma tietokantaan
            db.session.add(event)
            db.session.commit()
            # Palautetaan onnistumis status
            return Response(json.dumps({'message': 'Event created successfully!'}), status=201,
                            mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=400, mimetype='application/json')


@app.route('/api/announcement', methods=['GET', 'POST'])
def announcement():
    """
    Rajapinta tiedoteen luomiseen ja hakemiseen

    :return: tiedotteet
    """
    if request.method == 'GET':
        announcements = Announcement.query.all()
        announcements_list = []
        for announcement in announcements:
            announcements_list.append({
                'id': announcement.id,
                'title': announcement.title,
                'description': announcement.description
            })
        return Response(json.dumps(announcements_list), mimetype='application/json'), 200
    else:
        try:
            decoded_token, error = authenticate_request()
            if error:
                return Response(json.dumps({'error': 'Invalid token'}), status=401, mimetype='application/json')
            # Otetaan vastaan pyynnön data
            data = request.get_json()
            title = data['title']
            description = data['description']
            # Luodaan luokan avulla tiedote
            announcement = Announcement(title=title, description=description)
            # Viedään tapahtuma kantaan
            db.session.add(announcement)
            db.session.commit()
            # Palautetaan onnistuminen
            return Response(json.dumps({'message': 'Announcement created successfully!'}), status=201,
                            mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=400, mimetype='application/json')


@app.route('/api/content', methods=['GET', 'POST'])
def content():
    if request.method == 'GET':
        tag = request.args.get('tag')
        if not tag:
            contents = PageContent.query.all()
            contents_list = []
            for content in contents:
                contents_list.append({
                    'id': content.id,
                    'tag': content.tag,
                    'content': content.content
                })
            return Response(json.dumps(contents_list), mimetype='application/json'), 200
        content = PageContent.query.filter_by(tag=tag).first()
        if not content:
            return Response(json.dumps({'error': 'Content not found'}), status=404, mimetype='application/json')
        return Response(json.dumps({'content': content.content}), mimetype='application/json'), 200
    else:
        try:
            decoded_token, error = authenticate_request()
            if error:
                return Response(json.dumps({'error': 'Invalid token'}), status=401, mimetype='application/json')
            data = request.get_json()
            tag = data['tag']
            content = data['content']
            page_content = PageContent(tag=tag, content=content)
            db.session.add(page_content)
            db.session.commit()
            return Response(json.dumps({'message': 'Content created successfully!'}), status=201,
                            mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), status=400, mimetype='application/json')

@app.route('/api/content/<int:id>', methods=['PUT', 'DELETE'])
def manage_content(id):
    if request.method == 'PUT':
        content = PageContent.query.get(id)
    if not content:
        return Response(json.dumps({'error': 'Content not found'}), status=404, mimetype='application/json')
    data = request.get_json()
    content.content = data['content']
    db.session.commit()
    return Response(json.dumps({'message': 'Content updated successfully!'}), status=200, mimetype='application/json')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
