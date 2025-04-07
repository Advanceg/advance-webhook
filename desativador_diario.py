import psycopg2
from datetime import datetime

# Conexão com o PostgreSQL
conn = psycopg2.connect(
    dbname="advance_db",
    user="advance_user",
    password="E96eMP2eZX3sV4n9RKPp6XohK5s0LEKo",
    host="dpg-cvpk3os9c44c73c4kif0-a",
    port="5432"
)
cursor = conn.cursor()

hoje = datetime.now().date()

cursor.execute("""
    UPDATE usuarios
    SET status = '🚫 Inativo'
    WHERE proximo_vencimento < %s AND status != '🚫 Inativo'
""", (hoje,))

conn.commit()
print(f"[{hoje}] Verificação concluída.")
