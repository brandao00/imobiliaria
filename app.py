from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
import json
import os

app = Flask(__name__, template_folder='backend/templates')
app.secret_key = os.environ.get("SECRET_KEY", "imobiliaria-secret-key")
CORS(app)

DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(DATA_DIR, exist_ok=True)

ARQUIVO = os.path.join(DATA_DIR, "imoveis.json")
ADMIN_ARQUIVO = os.path.join(DATA_DIR, "admin_user.json")
DEFAULT_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@imobiliaria.com").strip().lower()
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123456")

if not os.path.exists(ARQUIVO):
    with open(ARQUIVO, "w") as f:
        json.dump([], f)


def ler():
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar(data):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def email_valido(email):
    return "@" in email and "." in email.split("@")[-1]


def salvar_admin(data):
    with open(ADMIN_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def carregar_admin():
    if not os.path.exists(ADMIN_ARQUIVO):
        admin_data = {
            "email": DEFAULT_ADMIN_EMAIL,
            "password_hash": generate_password_hash(DEFAULT_ADMIN_PASSWORD),
        }
        salvar_admin(admin_data)
        return admin_data

    with open(ADMIN_ARQUIVO, "r", encoding="utf-8") as f:
        admin_data = json.load(f)

    email = str(admin_data.get("email", "")).strip().lower()
    password_hash = str(admin_data.get("password_hash", "")).strip()

    if not email or not password_hash:
        admin_data = {
            "email": DEFAULT_ADMIN_EMAIL,
            "password_hash": generate_password_hash(DEFAULT_ADMIN_PASSWORD),
        }
        salvar_admin(admin_data)

    return admin_data


def admin_atual():
    admin_data = carregar_admin()
    return {
        "email": str(admin_data.get("email", DEFAULT_ADMIN_EMAIL)).strip().lower(),
        "password_hash": str(admin_data.get("password_hash", "")).strip(),
    }


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logado"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/api/imoveis", methods=["GET"])
@login_required
def get_imoveis():
    return jsonify(ler())


@app.route("/api/imoveis", methods=["POST"])
@login_required
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
@login_required
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
@login_required
def delete_imovel(id):
    imoveis = ler()
    imoveis = [i for i in imoveis if i.get("id") != id]
    salvar(imoveis)
    return jsonify({"ok": True})


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logado"):
        return redirect(url_for("admin"))

    erro = None
    proxima = request.args.get("next") or request.form.get("next") or url_for("admin")

    if request.method == "POST":
        admin_data = admin_atual()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email_valido(email):
            erro = "Informe um e-mail válido."
        elif email == admin_data["email"] and check_password_hash(admin_data["password_hash"], senha):
            session["admin_logado"] = True
            session["admin_user"] = email
            return redirect(proxima)
        else:
            erro = "E-mail ou senha inválidos."

    return render_template("login.html", erro=erro, next_url=proxima)


@app.route("/admin/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/admin/account", methods=["GET"])
@login_required
def get_admin_account():
    admin_data = admin_atual()
    return jsonify({"email": admin_data["email"]})


@app.route("/api/admin/account", methods=["POST"])
@login_required
def update_admin_account():
    try:
        dados = request.json or {}
        email = str(dados.get("email", "")).strip().lower()
        senha_atual = str(dados.get("current_password", ""))
        nova_senha = str(dados.get("new_password", ""))

        admin_data = admin_atual()

        if not check_password_hash(admin_data["password_hash"], senha_atual):
            return jsonify({"erro": "Senha atual incorreta."}), 400

        if not email_valido(email):
            return jsonify({"erro": "Informe um e-mail válido."}), 400

        if nova_senha and len(nova_senha) < 8:
            return jsonify({"erro": "A nova senha precisa ter pelo menos 8 caracteres."}), 400

        novo_hash = admin_data["password_hash"]
        if nova_senha:
            novo_hash = generate_password_hash(nova_senha)

        salvar_admin({
            "email": email,
            "password_hash": novo_hash,
        })

        session["admin_user"] = email
        return jsonify({"ok": True, "email": email})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/admin")
@login_required
def admin():
    admin_data = admin_atual()
    return render_template("index.html", admin_user=session.get("admin_user", admin_data["email"]))


@app.route("/")
def site():
    return render_template("SiteDecorumAtt.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
