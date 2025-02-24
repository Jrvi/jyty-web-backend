from flask import Blueprint, request, Response
import json

from extensions import db
from models import PageContent
from utils.auth import authenticate_request

content_bp = Blueprint('content', __name__)

@content_bp.route('/api/content', methods=['GET', 'POST'])
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


@content_bp.route('/api/content/<int:id>', methods=['PUT', 'DELETE'])
def manage_content(id):
    if request.method == 'PUT':
        content = PageContent.query.get(id)
    if not content:
        return Response(json.dumps({'error': 'Content not found'}), status=404, mimetype='application/json')
    data = request.get_json()
    content.content = data['content']
    db.session.commit()
    return Response(json.dumps({'message': 'Content updated successfully!'}), status=200, mimetype='application/json')