from aiohttp import web
connected = set()

async def websocket_broadcast(request, chunk):
    global connected
    print("In Broadcast")

    ws1 = web.WebSocketResponse()
    await ws1.prepare(request)

    for ws2 in connected:
        ws1 = ws2
        print("sending chunk")
        await ws1.send_bytes(chunk)


async def sendMessage(request):
    print("In SendMessage")
    foo = await request.post()
    print("Got Bytes")
    print (len(foo))

    #await websocket_broadcast(request, foo)


async def websocket_handler(request):
    global connected

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    connected.add(ws)
    print("Added Client")
    print(len(connected))

    #await asyncio.wait([ws.send("Hello!") for ws in connected])

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == web.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())
        elif msg.type == web.WSMsgType.BINARY:
            print("Sending Binary")
            await ws.send_bytes(msg.data)
            for ws in connected:
                await ws.send_str("Hello")

    print('websocket connection closed')

    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
app.router.add_post('/ws', websocket_broadcast)
app.router.add_post('/', sendMessage)

web.run_app(app)