import asyncio
import time

import msgpack
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import (
    HTMLResponse,
    Response,
    StreamingResponse,
)

from app.schemas import (
    ItemCardSchema,
)

from app.routes import (
    auth,
    users,
)

app = FastAPI(title="curso fastapi - app.py")
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Olá Mundo!"}


# =====================================================
# WEBSOCKET
# =====================================================


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    try:
        while True:
            message = await ws.receive_text()

            await ws.send_text(f"Recebido: {message}")

    except WebSocketDisconnect:
        pass


# =====================================================
# HTML
# =====================================================


@app.get(
    "/html",
    response_class=HTMLResponse,
)
def get_html():

    cards = [
        ItemCardSchema(titulo="Servidor", descricao="Servidor iniciado"),
        ItemCardSchema(titulo="Backup", descricao="Backup executado"),
    ]

    cards_html = "".join(
        f"""
        <div>
            <h3>{card.titulo}</h3>
            <p>{card.descricao}</p>
        </div>
        """
        for card in cards
    )

    return HTMLResponse(
        f"""
        <html>
            <body>
                {cards_html}
            </body>
        </html>
        """
    )


# =====================================================
# STREAMING
# =====================================================


@app.get("/stream")
def stream():

    def generator():

        for i in range(10):
            yield f"Evento {i}\n"

            time.sleep(1)

    return StreamingResponse(
        generator(),
        media_type="text/plain",
    )


# =====================================================
# SSE
# =====================================================


@app.get("/events")
async def events():

    async def generator():

        while True:
            yield ("data: novo evento\n\n")

            await asyncio.sleep(1)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
    )


# =====================================================
# MSGPACK
# =====================================================


@app.get("/msgpack")
def get_msgpack():

    data = {
        "id": 1,
        "name": "Yuji",
    }

    return Response(
        content=msgpack.packb(data),
        media_type="application/msgpack",
    )
