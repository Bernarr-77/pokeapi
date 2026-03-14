from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import httpx
import sqlite3
from validate.schemas import UserRegister, Pokemon
from validate.security import hash_password, verify_password,create_access_token,verify_token
from database import insert_users, get_users_email
import asyncio

app = FastAPI()
oauth = OAuth2PasswordBearer(tokenUrl="login")

def get_token(token: str = Depends(oauth)):
    try:
        email = verify_token(token)
        return email
    except ValueError:
         raise HTTPException(status_code= 401, detail= "Token inválido.")
    
async def buscar_pokemon(nome: str, cliente: httpx.AsyncClient):
    url = f"https://pokeapi.co/api/v2/pokemon/{nome}"
    resposta = await cliente.get(url)
    dados_brutos = resposta.json()
    pokemon_limpo = {
        "name": dados_brutos["name"],
        "image_url": dados_brutos["sprites"]["front_default"],
        "types": [item["type"]["name"] for item in dados_brutos["types"]],
        "ability": [item["ability"]["name"] for item in dados_brutos["abilities"]],
        "stats": {item["stat"]["name"]: item["base_stat"] for item in dados_brutos["stats"]}
    }
    return pokemon_limpo

@app.post("/register")
def register_user(payload: UserRegister):
    senha_protegida = hash_password(payload.password)
    try:
        insert_users(payload.email, senha_protegida)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code= 409, detail= "esse email ja esta cadastrado no sistema, tente outro!")
    except Exception as error_500:
        raise HTTPException(status_code=500, detail= f"Erro desconhecido: {str(error_500)}")
    return {"Message": "Usuario cadastrado com sucesso"}

@app.post("/login")
def system_open(register: OAuth2PasswordRequestForm = Depends()):
    usuario_db = get_users_email(register.username)
    if usuario_db is None:
        raise HTTPException(status_code= 401, detail= "Usuario ou senha incorretas, tente novamente")
    
    verificador = verify_password(register.password, usuario_db["hashed_password"])

    if not verificador:
        raise HTTPException(status_code= 401, detail= "Usuario ou senha incorretas, tente novamente")
    token = create_access_token({"sub": usuario_db["email"]})

    return {"access_token": token, "token_type": "bearer"}


@app.post("/porta")
async def acessar_pokeapi(input: Pokemon, usuario_logado: str = Depends(get_token)):
    async with httpx.AsyncClient() as client:
        lista_pokemon = input.pokemons
        organiza_pokemon = [buscar_pokemon(nome.lower(), client) for nome in lista_pokemon]
        resultado = await asyncio.gather(*organiza_pokemon)
        return {"time": resultado}

