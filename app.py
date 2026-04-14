from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__, template_folder='backend/templates')
CORS(app)

ARQUIVO = "imoveis.json"

if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w") as f:
        json.dump([], f)


def ler():
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar(data):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.route("/api/imoveis", methods=["GET"])
def get_imoveis():
    return jsonify(ler())


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


@app.route("/api/imoveis/<id>", methods=["PUT"])
def update_imovel(id):
    try:
        imoveis = ler()
        dados = request.json
        if not dados:
            return jsonify({"erro": "dados vazios"}), 400
        imoveis = [dados if i.get("id") == id else i for i in imoveis]
        salvar(imoveis)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/api/imoveis/<id>", methods=["DELETE"])
def delete_imovel(id):
    imoveis = ler()
    imoveis = [i for i in imoveis if i.get("id") != id]
    salvar(imoveis)
    return jsonify({"ok": True})


@app.route("/admin")
def admin():
    return render_template("index.html")


@app.route("/")
def site():
    return render_template("SiteDecorumAtt.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
