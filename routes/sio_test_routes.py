from app import sio


@sio.on('echo-back')
def handle_message(client, message):
    string = 'got message "{}" from {}'.format(message, client)
    print(string)
    return string


@sio.on('async-echo-back')
def handle_async_message(client, message):
    string = 'got message "{}" from {}'.format(message, client)
    print(string)
    sleep(5)
    emit('async back', string)