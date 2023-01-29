import socketio
from aiohttp import web
from collections import defaultdict

# create a Socket.IO server
sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

clients_list = []
rooms_dict = defaultdict(list)


async def client(request):
    print('client')
    return web.json_response({'clients': clients_list})


async def room(request):
    return web.json_response({'rooms': rooms_dict})


@sio.event
async def test(sid, data):
    print(f"Received message from {sid}: {data}")


@sio.event
async def connect(sid, environ):
    global clients_list
    print('connect ', sid)
    clients_list.append(sid)
    print(clients_list)


@sio.event
async def disconnect(sid):
    global clients_list
    print('disconnect ', sid)
    clients_list.remove(sid)
    print(clients_list)


# sio.emit('my event', {'data': 'foobar'}, room=user_sid)
@sio.event
async def send_message_to_room(sid, message):
    print(f"in send_message_to_room, params are: message: ${message}, socket_id: ${sid}")
    await sio.emit("room_message",
                   {'data': message['data']},
                   room=message['room']
                   )


@sio.event
async def join_room(sid, data):
    sio.enter_room(sid, data.room_id)
    print(f"Client {sid} joined room {data.room_id}")
    rooms_dict.push(data.room_id, [sid])
    print(rooms_dict)


@sio.event
async def exit_chat(sid, data):
    sio.leave_room(sid, data.room_id)
    print(f"Client {sid} left room {data.room_id}")
    rooms_dict[data.room_id].remove(sid)
    print(rooms_dict)


if __name__ == '__main__':
    app.router.add_get('/clients', client)
    app.router.add_get('/rooms', room)
    app.router.add_get('/', lambda request: web.Response(text="Hello world!"))
    web.run_app(app)
