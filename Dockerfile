# Käytetään kevyttä Python-kuvaa Raspberry Pi:tä varten
FROM python:3.11-slim

# Asetetaan työpolku
WORKDIR /app

# Kopioidaan projektin kaikki tiedostot
COPY . .

# Asennetaan riippuvuudet
RUN pip install --no-cache-dir -r requirements.txt

# Exposoidaan Flaskin oletusportti
EXPOSE 5000

# Asetetaan Flask-sovellus ympäristömuuttujilla
ENV FLASK_APP=main.py
ENV FLASK_ENV=production

# Käynnistetään sovellus
CMD ["python", "main.py"]