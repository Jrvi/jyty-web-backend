from extensions import db
import bcrypt


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
