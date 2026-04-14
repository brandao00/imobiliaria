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
        imoveis = ler
