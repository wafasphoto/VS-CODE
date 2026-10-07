from flask import Flask, render_template, session, redirect, url_for
from flask import request

app = Flask(__name__)
app.secret_key = "secretkey"

# Data produk sederhana
products = [
    {"id": 1, "name": "Sepatu Sneakers", "price": 250000},
    {"id": 2, "name": "Tas Ransel", "price": 175000},
    {"id": 3, "name": "Jam Tangan", "price": 300000},
]


@app.route("/")
def home():
    return render_template("index.html", products=products)


@app.route("/detail/<int:id>")
def detail(id):
    product = next((p for p in products if p["id"] == id), None)
    return render_template("detail.html", product=product)


@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    session.modified = True
    return redirect(url_for("home"))


@app.route("/cart")
def cart():
    cart_items = []
    total = 0

    if "cart" in session:
        for id in session["cart"]:
            product = next((p for p in products if p["id"] == id), None)
            if product:
                cart_items.append(product)
                total += product["price"]

    return render_template("cart.html", cart_items=cart_items, total=total)


if __name__ == "__main__":
    app.run(debug=True)
