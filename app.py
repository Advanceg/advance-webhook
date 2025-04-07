
from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)

def processar_pagamento(cliente):
    arquivo = "tabela_final_chaves_usuarios.xlsx"
    try:
        df = pd.read_excel(arquivo)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Nome Usuário", "Chave API", "Status", "Data Ativação", "Email", "Data Pagamento", "Próximo Vencimento"])

    email = cliente["customer_email"]
    hoje = datetime.now()
    vencimento = hoje + timedelta(days=30)

    if email in df["Email"].values:
        idx = df[df["Email"] == email].index[0]
        df.at[idx, "Status"] = "✅ Ativo"
        df.at[idx, "Data Pagamento"] = cliente["payment_date"]
        df.at[idx, "Próximo Vencimento"] = vencimento.strftime("%Y-%m-%d")
        df.at[idx, "Data Ativação"] = hoje.strftime("%Y-%m-%d")
    else:
        nova_chave = "advnc_" + secrets.token_urlsafe(32)
        novo_usuario = {
            "Nome Usuário": cliente["customer_name"],
            "Chave API": nova_chave,
            "Status": "✅ Ativo",
            "Data Ativação": hoje.strftime("%Y-%m-%d"),
            "Email": email,
            "Data Pagamento": cliente["payment_date"],
            "Próximo Vencimento": vencimento.strftime("%Y-%m-%d")
        }
        df = pd.concat([df, pd.DataFrame([novo_usuario])], ignore_index=True)

    df.to_excel(arquivo, index=False)

@app.route('/webhook-kiwify', methods=['POST'])
def webhook_kiwify():
    dados = request.json

    if dados["type"] == "order.paid":
        customer_name = dados["Order"]["customer_name"]
        customer_email = dados["Order"]["customer_email"]
        payment_date = dados["Order"]["paid_at"]

        cliente = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "payment_date": payment_date
        }

        processar_pagamento(cliente)
        return jsonify({"status": "pagamento processado com sucesso"}), 200

    return jsonify({"status": "evento ignorado"}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
