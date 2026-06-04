import asyncio
import csv
import io
import time
from http import HTTPStatus
from ctypes import CDLL

import msgpack
from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    status,
    WebSocketDisconnect,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    ORJSONResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)

from schemas.schemas import (
    ItemCardSchema,
    UserCreate,
    UserDB,
    UserPublic,
)

libmlx = CDLL("./libs/libmlx.so")
libft = CDLL("./libs/libft.so")
libformas = CDLL("./libs/libformas.so")

app = FastAPI(title="Dev_Yuji_v00")

users: list[UserDB] = []




@app.get("/")
def root():
    return {
        "message": "Olá Mundo!"
    }


# =====================================================
# CRUD USERS
# =====================================================


@app.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserCreate,
):

    user_db = UserDB(
        name=user.name,
        birth_date=user.birth_date,
        cpf_cnpj=user.cpf_cnpj,
        email=user.email,
        password_hash=f"HASH:{user.password}",
    )

    users.append(user_db)

    return UserPublic(
        id=user_db.id,
        name=user_db.name,
        email=user_db.email,
    )


@app.get(
    "/users",
    response_model=list[UserPublic],
)
def list_users():

    return [
        UserPublic(
            id=user.id,
            name=user.name,
            email=user.email,
        )
        for user in users
    ]


@app.get(
    "/users/{user_id}",
    response_model=UserPublic,
)
def get_user(user_id):

    for user in users:
        if str(user.id) == str(user_id):
            return UserPublic(
                id=user.id,
                name=user.name,
                email=user.email,
            )

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado.",
    )


@app.delete(
    "/users/{user_id}",
    status_code=204,
)
def delete_user(user_id):

    for index, user in enumerate(users):
        if str(user.id) == str(user_id):
            users.pop(index)

            return

    raise HTTPException(
        status_code=404,
        detail="Usuário não encontrado.",
    )


# =====================================================
# WEBSOCKET
# =====================================================

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    try:

        while True:

            message = await ws.receive_text()

            await ws.send_text(
                f"Recebido: {message}"
            )

    except WebSocketDisconnect:
        pass

# =====================================================
# FILES
# =====================================================


@app.get("/pdf")
def get_pdf():

    return FileResponse(
        "relatorio.pdf",
        media_type="application/pdf",
    )


@app.get("/zip")
def get_zip():

    return FileResponse("backup.zip")


@app.get("/image")
def get_image():

    return FileResponse("foto.png")


# =====================================================
# TEXT
# =====================================================


@app.get(
    "/text",
    response_class=PlainTextResponse,
)
def get_text():

    return "Servidor funcionando"


# =====================================================
# JSON
# =====================================================


@app.get("/json")
def get_json():

    return {"message": "Olá Mundo"}


# =====================================================
# ORJSON
# =====================================================


@app.get(
    "/orjson",
    response_class=ORJSONResponse,
)
def get_orjson():

    return ORJSONResponse(
        status_code=HTTPStatus.CREATED,
        content={"message": "Criado"},
    )


# =====================================================
# XML
# =====================================================


@app.get("/xml")
def get_xml():

    xml = """
<user>
    <id>1</id>
    <name>Yuji</name>
</user>
"""

    return Response(
        content=xml,
        media_type="application/xml",
    )


# =====================================================
# CSV
# =====================================================


@app.get("/csv")
def get_csv():

    buffer = io.StringIO()

    writer = csv.writer(buffer)

    writer.writerow(["id", "nome"])

    writer.writerow([1, "Yuji"])

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=usuarios.csv"},
    )


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
