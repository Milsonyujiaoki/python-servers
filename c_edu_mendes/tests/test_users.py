from http import HTTPStatus


def test_create_user_success(client):

    payload = {
        "name": "Yuji",
        "birth_date": "2000-01-01",
        "cpf_cnpj": "52998224725",
        "email": "yuji@email.com",
        "password": "Senha123",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == HTTPStatus.CREATED

    data = response.json()

    assert data["name"] == "Yuji"

    assert data["email"] == "yuji@email.com"

    assert "id" in data


def test_list_users(client):

    response = client.get("/users")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


def test_get_user_not_found(client):

    response = client.get("/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404

    assert response.json() == {"detail": "Usuário não encontrado."}


def test_delete_user_success(client):

    payload = {
        "name": "Yuji",
        "birth_date": "2000-01-01",
        "cpf_cnpj": "52998224725",
        "email": "yuji@email.com",
        "password": "Senha123",
    }

    created = client.post("/users", json=payload)

    user_id = created.json()["id"]

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 204


def test_invalid_cpf(client):

    payload = {
        "name": "Yuji",
        "birth_date": "2000-01-01",
        "cpf_cnpj": "11111111111",
        "email": "yuji@email.com",
        "password": "Senha123",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_invalid_email(client):

    payload = {
        "name": "Yuji",
        "birth_date": "2000-01-01",
        "cpf_cnpj": "52998224725",
        "email": "abc",
        "password": "Senha123",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_invalid_password(client):

    payload = {
        "name": "Yuji",
        "birth_date": "2000-01-01",
        "cpf_cnpj": "52998224725",
        "email": "yuji@email.com",
        "password": "senha123",
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_json_response(client):

    response = client.get("/json")

    assert response.status_code == 200

    assert response.json() == {"message": "Olá Mundo"}


def test_orjson_response(client):

    response = client.get("/orjson")

    assert response.status_code == 201

    assert response.json() == {"message": "Criado"}


def test_xml_response(client):

    response = client.get("/xml")

    assert response.status_code == 200

    assert "application/xml" in response.headers["content-type"]


def test_csv_response(client):

    response = client.get("/csv")

    assert response.status_code == 200

    assert "text/csv" in response.headers["content-type"]


import msgpack


def test_msgpack_response(client):

    response = client.get("/msgpack")

    data = msgpack.unpackb(response.content, raw=False)

    assert data["name"] == "Yuji"


def test_websocket(client):

    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("teste")

        response = websocket.receive_text()

        assert response == "Recebido: teste"
