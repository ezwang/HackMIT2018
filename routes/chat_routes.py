from datetime import datetime
from flask import jsonify, request

from app import sio, db, app
from flask_login import current_user
from database import Message, Conversation, User
from sqlalchemy import or_, and_


@sio.on('message')
def send_message(message, recipient):
    usr = current_user.social_id
    if current_user.is_mentor:
        convo = Conversation.query.filter_by(mentor=usr, mentee=recipient).first()
    else:
        convo = Conversation.query.filter_by(mentee=usr, mentor=recipient).first()
    if convo is None:
        print('conversation not found')
        return
    timestamp = datetime.now()
    other_nick = User.query.filter_by(social_id=recipient).first()
    other_nick = other_nick.social_id
    print('message sent by {} to {} at {}: {}'.format(current_user.social_id, other_nick, timestamp, message))
    message = Message(sent=timestamp, owner=usr, recipient=recipient, contents=message)
    db.session.add(message)
    db.session.commit()

    # find if the other side is online
    other_sid = User.query.filter_by(social_id=recipient).first().id
    if sio.server.manager.is_connected(other_sid, '/chat'):
        # they are connected!
        sio.emit('message', {'sent': timestamp, 'owner': usr, 'recipient': recipient, 'contents': message})


@app.route('/chat/conversations')
def get_conversations():
    usr = current_user.social_id
    convos = Conversation.query.filter(or_(Conversation.mentor == usr, Conversation.mentee == usr)).all()
    return jsonify({"data": [conv.mentor if conv.mentee == usr else conv.mentee for conv in convos]})


@app.route('/chat/history')
def getMessages():
    other = request.args.get('other')
    usr = current_user.social_id
    if current_user.is_mentor:
        convo = Conversation.query.filter_by(mentor=usr, mentee=other).first()
    else:
        convo = Conversation.query.filter_by(mentee=other, mentor=usr).first()
    if convo is None:
        return jsonify({"error": "Conversation not found!"})

    messages = Message.query.filter(
        or_(
            and_(Message.owner == other, Message.recipient == usr),
            and_(Message.owner == usr, Message.recipient == other)
        )
    ).all()
    messages = list(map(lambda item: item.toDict(), messages))
    return jsonify(messages)


@app.route('/register_conversation', methods=['POST'])
def registerConversation():
    data = request.get_json(force=True)
    other = data['other']
    usr = current_user.social_id
    if current_user.is_mentor:
        convo = Conversation(mentor=usr, mentee=other)
    else:
        convo = Conversation(mentor=other, mentee=usr)

    db.session.add(convo)
    db.session.commit()

    return 'True'
