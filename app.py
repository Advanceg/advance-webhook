from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)

# Conexão com o banco de dados PostgreSQL (Render)
conn = psycopg2.connect(
    dbname="advance_db",
    user="advance_user",
    password="E96eMP2eZX3sV4n9RKPp6XohK5s0LEKo",
    host="dpg-cvpk3os9c44c73c4kif0-a",
    port="5432"
)
cursor = conn.cursor()

# Criação da tabela se não existir (executa uma vez)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        chave_api TEXT,
        status VARCHAR(20),
        data_ativacao DATE,
        data_pagamento DATE,
        proximo_vencimento DATE
    )
''')
conn.commit()

@app.route('/webhook-kiwify', methods=['POST'])
def webhook_kiwify():
    dados = request.json

    if dados.get("type") == "order.paid":
        try:
            nome = dados["Order"]["customer_name"]
            email = dados["Order"]["customer_email"]
            pagamento = datetime.fromisoformat(dados["Order"]["paid_at"][:-1])

            hoje = datetime.now()
            vencimento = hoje + timedelta(days=30)
            chave = "advnc_" + secrets.token_urlsafe(32)

            # Verifica se o usuário já existe
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            resultado = cursor.fetchone()

            if resultado:
                # Atualiza se já existir
                cursor.execute('''
                    UPDATE usuarios SET
                        status = %s,
                        data_pagamento = %s,
                        proximo_vencimento = %s,
                        data_ativacao = %s
                    WHERE email = %s
                ''', ("✅ Ativo", pagamento, vencimento, hoje, email))
            else:
                # Cria novo se não existir
                cursor.execute('''
                    INSERT INTO usuarios (nome, email, chave_api, status, data_ativacao, data_pagamento, proximo_vencimento)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (nome, email, chave, "✅ Ativo", hoje, pagamento, vencimento))

            conn.commit()
            return jsonify({"status": "pagamento processado com sucesso"}), 200

        except Exception as e:
            print("❌ Erro ao processar webhook:", e)
            return jsonify({"status": "erro no processamento"}), 500

    return jsonify({"status": "evento ignorado"}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
