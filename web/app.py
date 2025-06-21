from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)


def get_connection():
    return mysql.connector.connect(
        host="mysql",
        user="root",
        password="rootpass",
        database="chatdb"
    )

@app.route("/")
def index():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u1.nombre AS emisor, u2.nombre AS receptor, m.mensaje, m.creado_en
            FROM mensajes m
            JOIN usuarios u1 ON m.emisor_id = u1.id
            JOIN usuarios u2 ON m.receptor_id = u2.id
            ORDER BY m.creado_en DESC
            LIMIT 20
        """)
        mensajes = cursor.fetchall()
        return render_template("index.html", mensajes=mensajes)

    except mysql.connector.Error as e:
        return f"Error al conectarse a la base de datos: {e}"

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

@app.route("/buscar", methods=["GET"])
def buscar():
    usuario = request.args.get("usuario", "").strip()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u1.nombre AS emisor, u2.nombre AS receptor, m.mensaje, m.creado_en
            FROM mensajes m
            JOIN usuarios u1 ON m.emisor_id = u1.id
            JOIN usuarios u2 ON m.receptor_id = u2.id
            WHERE u1.nombre = %s OR u2.nombre = %s
            ORDER BY m.creado_en DESC
            LIMIT 20
        """, (usuario, usuario))
        mensajes = cursor.fetchall()
        return render_template("index.html", mensajes=mensajes, usuario=usuario)

    except mysql.connector.Error as e:
        return f"Error al conectarse a la base de datos: {e}"

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)