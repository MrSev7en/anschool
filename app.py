import sqlite3
import time
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
users = []


def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            type_formatted TEXT,
            name TEXT,
            document TEXT,
            document_formatted TEXT,
            phone TEXT,
            phone_formatted TEXT,
            email TEXT,
            login TEXT,
            password TEXT,
            status BOOLEAN
        )
    """
    )
    conn.commit()
    conn.close()


def load_operator():
    return {
        "type": "operator",
        "type_formatted": "Operador",
        "name": "",
        "document": "",
        "document_formatted": "",
        "phone": "",
        "phone_formatted": "",
        "email": "",
        "login": "admin",
        "password": "P@ssw0rd",
        "status": True,
    }


def load_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users_data = cursor.fetchall()
    conn.close()

    return [
        {
            "type": row[1],
            "type_formatted": row[2],
            "name": row[3],
            "document": row[4],
            "document_formatted": row[5],
            "phone": row[6],
            "phone_formatted": row[7],
            "email": row[8],
            "login": row[9],
            "password": row[10],
            "status": row[11],
        }
        for row in users_data
    ]


def remove_duplicates(users):
    seen_keys = set()
    unique_users = []

    for user in users:
        key = (user["document"], user["phone"], user["email"], user["login"])

        if key not in seen_keys:
            unique_users.append(user)
            seen_keys.add(key)

    return unique_users


def save_user(user):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (type, type_formatted, name, document, document_formatted,
                           phone, phone_formatted, email, login, password, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            user["type"],
            user["type_formatted"],
            user["name"],
            user["document"],
            user["document_formatted"],
            user["phone"],
            user["phone_formatted"],
            user["email"],
            user["login"],
            user["password"],
            user["status"],
        ),
    )
    conn.commit()
    conn.close()


def remove_user_by_document(document):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE document = ?", (document,))
    conn.commit()
    conn.close()


def format_type(type):
    if type == "operator":
        return "Operador"
    elif type == "visitor":
        return "Visitante"
    elif type == "employee":
        return "Funcionário"

    return ""


def format_document(document):
    document = "".join(filter(str.isdigit, str(document)))

    if len(document) != 11:
        return ""

    formatted = f"{document[:3]}.{document[3:6]}.{document[6:9]}-{document[9:]}"
    return formatted


def format_phone(phone):
    phone = "".join(filter(str.isdigit, str(phone)))

    if len(phone) < 11:
        return ""

    formatted = f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    return formatted


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", users=users[1:])


@app.route("/signup", methods=["POST"])
def signup():
    type = request.form.get("type")
    type_formatted = format_type(request.form.get("type")) or "Não fornecido"
    name = request.form.get("name")
    document = request.form.get("document")
    document_formatted = format_document(request.form.get("document"))
    phone = request.form.get("phone") or "Não fornecido"
    phone_formatted = format_phone(request.form.get("phone")) or "Não fornecido"
    email = request.form.get("email") or "Não fornecido"

    if any(user["document"] == document for user in users) or (
        type == "employee"
        and (
            any(user["phone"] == phone for user in users)
            or any(user["email"] == email for user in users)
        )
    ):
        return redirect("/?signup=error")

    user = {
        "type": type,
        "type_formatted": type_formatted,
        "name": name,
        "document": document,
        "document_formatted": document_formatted,
        "phone": phone,
        "phone_formatted": phone_formatted,
        "email": email,
        "login": "",
        "password": "",
        "status": False,
    }

    users.append(user)
    save_user(user)

    return redirect("/?signup=success")


@app.route("/signin", methods=["POST"])
def signin():
    type = request.form.get("type")
    login = request.form.get("login")
    password = request.form.get("password")

    if type != "operator":
        return redirect("/?signin=error")

    for user in users:
        if (
            user["type"] == type
            and user["login"] == login
            and user["password"] == password
        ):
            return redirect("/?auth=success")

    return redirect("/?signin=error")


@app.route("/remove", methods=["POST"])
def remove_user():
    document = request.form.get("document")
    ts = int(time.time())

    for user in users:
        if user["document"] == document:
            users.remove(user)
            remove_user_by_document(document)
            break

    return redirect(f"/?auth=success&timestamp={ts}")


@app.route("/status", methods=["POST"])
def status_user():
    document = request.form.get("document")
    ts = int(time.time())

    for index, user in enumerate(users):
        if user["document"] == document:
            users[index]["status"] = not users[index]["status"]
            save_user(users[index])
            break

    return redirect(f"/?auth=success&timestamp={ts}")


init_db()
users.clear()
users.append(load_operator())

for user in load_users():
    users.append(user)

users = remove_duplicates(users)
app.run(debug=True)
