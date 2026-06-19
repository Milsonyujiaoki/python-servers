import asyncio, csv, io, datetime, time, string
from uuid import UUID

import msgpack
from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    PlainTextResponse,
    Response,
    StreamingResponse,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import User
from app.schemas import (
    ItemCardSchema,
    UserPublic,
    UserSchema,
    UserList,
)

app = FastAPI(title="curso fastapi - app.py")


@app.get("/")
def root():
    return {"message": "Olá Mundo!"}


# =====================================================
# CRUD USERS
# =====================================================


@app.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserSchema, session: Session = Depends(get_session)) -> UserPublic:
    db_user: User | None = session.scalar(
        select(User).where(
            (User.email == user.email)
            | (User.username == user.name)
            | (User.cpf_cnpj == user.cpf_cnpj)
        )
    )
    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário com email já existe.",
            )
        elif db_user.username == user.name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário com nome já existe.",
            )
        elif db_user.cpf_cnpj == user.cpf_cnpj:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Usuário com CPF/CNPJ já existe.",
            )

    db_user = User(
        username=user.name,
        cpf_cnpj=user.cpf_cnpj,
        email=user.email,
        password=user.password,
        birth_date=user.birth_date,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserPublic(
        id=db_user.id,
        name=db_user.username,
        email=db_user.email,
    )

""" @app.post(
    "/users",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: UserSchema,
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
 """

@app.get("/users", response_model=UserList, status_code=status.HTTP_200_OK)
def get_all_users(session: Session = Depends(get_session), limit: int = 50, offset: int = 0) -> UserList:
    users = session.scalars(select(User).offset(offset).limit(limit)).all()
    return UserList(users=[UserPublic(id=user.id, name=user.username, email=user.email) for user in users])


@app.get(
    "/users/{user_id}",
    response_model=UserPublic,
)
def get_user(
    user_id: UUID, session: Session = Depends(get_session)
) -> UserPublic:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado.",
        )
    return UserPublic(
        id=user.id,
        name=user.username,
        email=user.email,
    )

@app.put(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
def update_user(
    user_id: UUID,
    user_update: UserSchema,
    session: Session = Depends(get_session),
) -> UserPublic:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )

    db_user.username = user_update.name
    db_user.cpf_cnpj = user_update.cpf_cnpj
    db_user.email = user_update.email
    db_user.password = user_update.password
    db_user.birth_date = user_update.birth_date

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return UserPublic(
        id=db_user.id,
        name=db_user.username,
        email=db_user.email,
    )

@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
)
def delete_user(
    user_id: UUID, session: Session = Depends(get_session)
) -> None:

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    session.delete(db_user)
    session.commit()
    return {'message': 'User deleted with success'}

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
