from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
import uuid

app = Flask(__name__)
app.debug = True
app.config['SECRET_TYPE'] = uuid.uuid4()
app.config['SESSION_TYPE'] = "filesystem" # filesystem store sessions localy in the folder


Session(app)

socketio = SocketIO(app, manage_session = False)

# Homepage render
@app.route('/', methods=['GET', "POST"])
def index():
    return render_template('index.html')


# Chat page render
@app.route('/chat', methods=['GET', "POST"])
def chat():
    if request.method == "POST":
        username = request.form['username']
        session['username'] = username
        session['id'] = username
        return render_template('chat.html', session = session)
    else:
        if session.get('username') is not None:
            return render_template('chat.html', session = session)
        else:
            return redirect(url_for('index'))

"""
Websoket events
    join  - when user created a connection to websocket
    text  - on message send
    left  - when user unconnected from websocket
"""

@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('id')
    join_room(room)
    emit('status', {'msg':  session.get('username') + ' has entered the room.'}, room=room)

@socketio.on('text', namespace='/chat')
def text(message, to):
    room = session.get('username')
    print(room)
    print(room, to)
    emit('message', {'user': session.get('username'), 'from': room, 'msg': f"{message['msg']}"}, room=to)
    emit('message', {'user': session.get('username'), 'from': to, 'msg': f"{message['msg']}"}, room=room)

@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('id')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('message', {'msg': f"{username} has left the room!"}, room=room)


if __name__ == "__main__":
    socketio.run(app)
