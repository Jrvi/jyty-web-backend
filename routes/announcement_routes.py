from flask import Blueprint, request, Response
import json

from extensions import db
from models import Announcement
from utils.auth import authenticate_request

announcement_bp = Blueprint('announcement', __name__)

@announcement_bp.route('/api/announcement', methods=['GET', 'POST'])
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