import msgpack
from fastapi import status


def test_get_user_not_found(client):

    response = client.get("/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == status.HTTP_404_NOT_FOUND

    assert response.json() == {"detail": "Usuário não encontrado."}


def test_invalid_cpf(client):

    payload = {
        "name": "Yuji",
        "birth_date": "2000-01-01",
        "cpf_cnpj": "11111111111",
        "email": "yuji@email.com",
        "password": "Senha123",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_invalid_email(client):

    payload = {
        "name": "Yuji",
        "birth_date": "2000-01-01",
        "cpf_cnpj": "52998224725",
        "email": "abc",
        "password": "Senha123",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_invalid_password(client):

    payload = {
        "name": "Yuji",
        "birth_date": "2000-01-01",
        "cpf_cnpj": "52998224725",
        "email": "yuji@email.com",
        "password": "senha123",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_msgpack_response(client):

    response = client.get("/msgpack")

    assert response.status_code == status.HTTP_200_OK

    data = msgpack.unpackb(response.content, raw=False)

    assert data["name"] == "Yuji"


def test_websocket(client):

    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("teste")

        response = websocket.receive_text()

        assert response == "Recebido: teste"
