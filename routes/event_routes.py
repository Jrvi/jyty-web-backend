from flask import Blueprint, request, Response

from extensions import db
from models import Event
import json
from datetime import datetime

from utils.auth import authenticate_request

event_bp = Blueprint('event', __name__)


@event_bp.route('/api/event', methods=['GET', 'POST'])
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
