
import os
import oracledb

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_USER = os.getenv("ORACLE_USER", "SYSTEM")
DB_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
DB_DSN = os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1")


def get_connection():
    if not DB_PASSWORD:
        raise RuntimeError(
            "Oracle password is missing. Check your .env file."
        )

    return oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )


def fetch_all(sql, params=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or {})
            columns = [col[0].lower() for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]


def fetch_one(sql, params=None):
    rows = fetch_all(sql, params)
    return rows[0] if rows else {}


def json_safe(data):
    """Convert Oracle date and decimal-like values for JSON."""
    from datetime import date, datetime
    from decimal import Decimal

    if isinstance(data, dict):
        return {key: json_safe(value) for key, value in data.items()}
    if isinstance(data, list):
        return [json_safe(value) for value in data]
    if isinstance(data, (datetime, date)):
        return data.strftime("%d %b %Y, %I:%M %p")
    if isinstance(data, Decimal):
        return float(data)

    return data


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/dashboard")
def dashboard():
    try:
        stats = fetch_one("""
            SELECT
                (SELECT COUNT(*) FROM products) AS product_count,
                (SELECT NVL(SUM(stock_quantity), 0)
                 FROM products) AS units_in_stock,
                (SELECT COUNT(*) FROM products
                 WHERE stock_quantity <= 20) AS low_stock_count,
                (SELECT NVL(SUM(final_amount), 0)
                 FROM sales) AS total_sales,
                (SELECT COUNT(*) FROM sales) AS total_orders
            FROM dual
        """)

        recent_sales = fetch_all("""
            SELECT s.sale_id, p.product_name, s.quantity,
                   s.gross_amount, s.discount, s.final_amount,
                   s.sale_date
            FROM sales s
            JOIN products p ON p.product_id = s.product_id
            ORDER BY s.sale_id DESC
            FETCH FIRST 5 ROWS ONLY
        """)

        return jsonify(json_safe({
            "stats": stats,
            "recent_sales": recent_sales
        }))
    except Exception as error:
        app.logger.exception("Dashboard loading failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/products")
def products():
    try:
        data = fetch_all("""
            SELECT product_id, product_name,
                   stock_quantity, price
            FROM products
            ORDER BY product_id
        """)
        return jsonify(json_safe(data))
    except Exception as error:
        app.logger.exception("Products loading failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/sales")
def sales():
    try:
        data = fetch_all("""
            SELECT s.sale_id, s.product_id, p.product_name,
                   s.quantity, s.gross_amount, s.discount,
                   s.final_amount, s.sale_date
            FROM sales s
            JOIN products p ON p.product_id = s.product_id
            ORDER BY s.sale_id DESC
        """)
        return jsonify(json_safe(data))
    except Exception as error:
        app.logger.exception("Sales loading failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/stock-audit")
def stock_audit():
    try:
        data = fetch_all("""
            SELECT a.audit_id, a.product_id, p.product_name,
                   a.old_quantity, a.new_quantity, a.change_date
            FROM stock_audit a
            JOIN products p ON p.product_id = a.product_id
            ORDER BY a.audit_id DESC
        """)
        return jsonify(json_safe(data))
    except Exception as error:
        app.logger.exception("Stock history loading failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/low-stock")
def low_stock():
    try:
        data = fetch_all("""
            SELECT product_id, product_name,
                   stock_quantity, price
            FROM products
            WHERE stock_quantity <= 20
            ORDER BY stock_quantity
        """)
        return jsonify(json_safe(data))
    except Exception as error:
        app.logger.exception("Low-stock report failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/sale", methods=["POST"])
def create_sale():
    data = request.get_json(silent=True) or {}

    try:
        product_id = int(data.get("product_id", 0))
        quantity = int(data.get("quantity", 0))

        if product_id <= 0 or quantity <= 0:
            return jsonify({
                "error": "Choose a product and enter a quantity above zero."
            }), 400

        # Use the PL/SQL procedure already created in Oracle.
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.callproc(
                    "record_sale",
                    [product_id, quantity]
                )

        # The procedure commits the sale itself.
        # Fetch the latest sale for the response.
        sale = fetch_one("""
            SELECT s.sale_id, p.product_name, s.quantity,
                   s.gross_amount, s.discount, s.final_amount,
                   s.sale_date
            FROM sales s
            JOIN products p ON p.product_id = s.product_id
            ORDER BY s.sale_id DESC
            FETCH FIRST 1 ROW ONLY
        """)

        return jsonify({
            "message": "Sale recorded successfully.",
            "sale": json_safe(sale)
        }), 201

    except ValueError:
        return jsonify({
            "error": "Product ID and quantity must be valid whole numbers."
        }), 400

    except oracledb.DatabaseError as error:
        app.logger.exception("Oracle rejected the sale")
        message = str(error.args[0]) if error.args else str(error)
        return jsonify({"error": message}), 400

    except Exception as error:
        app.logger.exception("Sale failed")
        return jsonify({"error": str(error)}), 500


@app.route("/api/health")
def health():
    try:
        result = fetch_one("SELECT 'connected' AS status FROM dual")
        return jsonify({"status": result.get("status", "unknown")})
    except Exception as error:
        app.logger.exception("Database connection check failed")
        return jsonify({
            "status": "error",
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
