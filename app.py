from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app)

# قائمة المستخدمين مع المدة الزمنية
users = {}
banned_ips = {}

# الصفحة الرئيسية مع HTML مدمج داخل السكربت
@app.route('/')
def home():
    return render_template('index.html')

# حدث إرسال رسالة
@socketio.on('send_message')
def handle_message(data):
    username = data['username']
    msg = data['msg']
    emit('receive_message', {'msg': f'{username}: {msg}'}, broadcast=True)

# حدث انضمام مستخدم
@socketio.on('join')
def handle_join(data):
    username = data['username']
    
    # التحقق من وجود المستخدم في قائمة الحظر
    if username in banned_ips:
        emit('ban_message', {'msg': 'You have been banned from the chat!', 'banDuration': banned_ips[username]})
        return
    
    # إذا كان اسم المستخدم هو الأونر
    if username == "yousefahmed-nullsec":
        emit('receive_message', {'msg': 'Owner Of NullSec Joined The Chat!'}, broadcast=True)
        return
    
    users[username] = {'join_time': time.time()}
    emit('receive_message', {'msg': f'{username} Joined The Chat !'}, broadcast=True)

# حدث طرد مستخدم
@socketio.on('kick_user')
def handle_kick(data):
    user_to_kick = data['userToKick']
    if user_to_kick in users:
        del users[user_to_kick]
        emit('kick_message', {'msg': f'{user_to_kick} has been kicked from the chat.'}, broadcast=True)

# حدث حظر مستخدم
@socketio.on('ban_user')
def handle_ban(data):
    user_to_ban = data['userToBan']
    if user_to_ban in users:
        del users[user_to_ban]
        banned_ips[user_to_ban] = time.time()  # حفظ وقت الحظر
        emit('ban_message', {'msg': f'{user_to_ban} has been banned from the chat.', 'banDuration': time.time()})
        
# حدث مسح الرسائل
@socketio.on('clear_messages')
def clear_messages():
    emit('receive_message', {'msg': '[System] All messages cleared.'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
