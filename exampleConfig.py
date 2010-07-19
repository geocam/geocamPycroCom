PROTOCOL = 'tcp'

if PROTOCOL == 'ipc':
    SERVER_ENDPOINT = 'ipc:exampleServer'
    NOTIFY_ENDPOINT = 'ipc:localhost:1381'
    USE_SERVICE_DISCOVERY = True
elif PROTOCOL == 'tcp':
    SERVER_ENDPOINT = 'tcp:localhost:9085'
    NOTIFY_ENDPOINT = None
    USE_SERVICE_DISCOVERY = False
