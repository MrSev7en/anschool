from flask import Flask, render_template, request, redirect

app = Flask(__name__)
users = []


def format_type(type):
    if type == "visitor":
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
    return render_template("index.html", users=users)


@app.route("/signup", methods=["POST"])
def signup():
    access_type = request.form.get("type")
    type = format_type(request.form.get("type")) or "Não fornecido"
    name = request.form.get("name")
    document = format_document(request.form.get("document"))
    phone = format_phone(request.form.get("phone")) or "Não fornecido"
    email = request.form.get("email") or "Não fornecido"
    password = request.form.get("password")

    if (
        any(user["document"] == document for user in users)
        or any(user["phone"] == phone for user in users)
        or any(user["email"] == email for user in users)
    ):
        return redirect("/?signup=error")

    users.append(
        {
            "access_type": access_type,
            "type": type,
            "name": name,
            "document": document,
            "phone": phone,
            "email": email,
            "password": password,
        }
    )

    return redirect("/?auth=success")


@app.route("/signin", methods=["POST"])
def signin():
    access_type = request.form.get("type")
    document = format_document(request.form.get("document"))
    password = request.form.get("password")

    for user in users:
        if (
            user["access_type"] == access_type
            and user["document"] == document
            and user["password"] == password
        ):
            return redirect("/?auth=success")

    return redirect("/?signin=error")


@app.route("/remove", methods=["POST"])
def remove_user(document):
    for user in users:
        if user["document"] == document:
            users.remove(user)
            break

    return render_template("index.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)
