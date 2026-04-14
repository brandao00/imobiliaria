from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # evita erro de bloqueio entre front e backend

ARQUIVO = "imoveis.json"

# cria arquivo se não existir
if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w") as f:
        json.dump([], f)

# ler dados


def ler():
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)

# salvar dados


def salvar(data):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 🔥 API - listar imóveis


@app.route("/api/imoveis", methods=["GET"])
def get_imoveis():
    return jsonify(ler())

# 🔥 API - adicionar imóvel


@app.route("/api/imoveis", methods=["POST"])
def add_imovel():
    try:
        imoveis = ler()
        novo = request.json

        if not novo:
            return jsonify({"erro": "dados vazios"}), 400

        imoveis.append(novo)
        salvar(imoveis)

        return jsonify({"ok": True})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# 🔥 API - deletar imóvel (opcional mas já deixei pronto)


@app.route("/api/imoveis/<id>", methods=["DELETE"])
def delete_imovel(id):
    imoveis = ler()
    imoveis = [i for i in imoveis if i.get("id") != id]
    salvar(imoveis)
    return jsonify({"ok": True})

# 🖥️ admin


@app.route("/admin")
def admin():
    return render_template("admin.html")

# 🌐 site público


@app.route("/")
def site():
    return render_template("site.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)