import sqlite3

def start_bank_users():
    con = sqlite3.connect("users.db")
    cur = con.cursor()

    sql = """
        CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL
        )
        """
    
    cur.execute(sql)
    con.commit()
    con.close()

def insert_users(email, hashed_password):
    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        sql = """
        INSERT INTO users(email, hashed_password)
        VALUES(?, ?)
        """
        cur.execute(sql, (email, hashed_password,))

def get_users_email(email):
    with sqlite3.connect("users.db") as con :
        con.row_factory = sqlite3.Row

        cur = con.cursor()

        sql = """
            SELECT * FROM users WHERE email = ?
            """
        cur.execute(sql, (email,))
        linha = cur.fetchone()
        if linha:
            return dict(linha)
        else:
            return None

if __name__ == "__main__":
    start_bank_users()
    print("Banco de dados users funcionando")