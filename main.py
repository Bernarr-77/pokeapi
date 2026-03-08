from fastapi import FastAPI, HTTPException 
import httpx
import sqlite3
from validate.schemas import UserRegister
from validate.security import hash_password, verify_password,create_access_token
from database import insert_users, get_users_email

app = FastAPI()

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
def system_open(register: UserRegister):
    usuario_db = get_users_email(register.email)
    if usuario_db is None:
        raise HTTPException(status_code= 401, detail= "Usuario ou senha incorretas, tente novamente")
    
    verificador = verify_password(register.password, usuario_db["hashed_password"])

    if verificador == False:
        raise HTTPException(status_code= 401, detail= "Usuario ou senha incorretas, tente novamente")
    token = create_access_token({"sub": usuario_db["email"]})

    return {"access_token": token, "token_type": "bearer"}

    
    


