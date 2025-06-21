from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = 'tu_secreto_super_seguro'  # Clave secreta
socketio = SocketIO(app, async_mode='eventlet')

# Diccionario para trackear usuarios conectados {sid: username}
connected_users = {}

def get_connection():
    return mysql.connector.connect(
        host="mysql",
        user="root",
        password="rootpass",
        database="chatdb"
    )

# --- RUTAS WEB ---

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form.get("nombre").strip()
        password = request.form.get("password").strip()

        if not nombre or not password:
            return render_template("login.html", error="Faltan datos")

        # Verificar si el usuario existe o crear
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM usuarios WHERE nombre=%s", (nombre,))
            user = cursor.fetchone()

            if user:
                # Usuario existe: verifico password
                if check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    session['username'] = user['nombre']
                    return redirect(url_for('chat'))
                else:
                    error = "Contraseña incorrecta"
                    return render_template('login.html', error=error)
            else:
                 # Crear usuario nuevo
                pw_hash = generate_password_hash(password)
                cursor.execute("INSERT INTO usuarios (nombre, password) VALUES (%s, %s)", (nombre, pw_hash))
                conn.commit()
                session['user_id'] = cursor.lastrowid
                session['username'] = nombre
                cursor.close()
                conn.close()
                return redirect(url_for('chat'))


        except mysql.connector.Error as e:
            return f"Error DB: {e}"

        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    return render_template("login.html")


@app.route("/chat")
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Traer últimos 20 mensajes
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u1.nombre AS emisor, u2.nombre AS receptor, m.mensaje, m.creado_en
            FROM mensajes m
            JOIN usuarios u1 ON m.emisor_id = u1.id
            JOIN usuarios u2 ON m.receptor_id = u2.id
            WHERE u1.nombre = %s OR u2.nombre = %s OR m.receptor_id IS NULL
            ORDER BY m.creado_en DESC
            LIMIT 20
        """, (username, username))
        mensajes = cursor.fetchall()
    except mysql.connector.Error as e:
        mensajes = []
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    return render_template("chat.html", username=username, mensajes=mensajes)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- SOCKET.IO EVENTS ---

@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if not username:
        return False  # Rechaza la conexión si no está logueado

    connected_users[request.sid] = username
    emit('user_list', list(set(connected_users.values())), broadcast=True)
    print(f"{username} conectado.")


@socketio.on('disconnect')
def handle_disconnect():
    username = connected_users.get(request.sid)
    if username:
        print(f"{username} desconectado.")
        connected_users.pop(request.sid)
        emit('user_list', list(set(connected_users.values())), broadcast=True)


@socketio.on('private_message')
def handle_private_message(data):
    sender = connected_users.get(request.sid)
    receptor = data.get('receptor')
    mensaje = data.get('mensaje')

    if not sender or not receptor or not mensaje:
        return

    # Guardar mensaje en DB
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Obtener IDs
        cursor.execute("SELECT id FROM usuarios WHERE nombre=%s", (sender,))
        emisor_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM usuarios WHERE nombre=%s", (receptor,))
        receptor_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO mensajes (emisor_id, receptor_id, mensaje) VALUES (%s, %s, %s)",
                       (emisor_id, receptor_id, mensaje))
        conn.commit()

    except Exception as e:
        print(f"Error guardando mensaje privado: {e}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    # Enviar solo al receptor y al emisor
    for sid, user in connected_users.items():
        if user == receptor or user == sender:
            emit('new_private_message', {'emisor': sender, 'mensaje': mensaje}, room=sid)


@socketio.on('broadcast_message')
def handle_broadcast_message(data):
    sender = connected_users.get(request.sid)
    mensaje = data.get('mensaje')

    if not sender or not mensaje:
        return

    # Guardar mensaje en DB con receptor_id NULL para mensaje global
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE nombre=%s", (sender,))
        emisor_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO mensajes (emisor_id, receptor_id, mensaje) VALUES (%s, NULL, %s)", (emisor_id, mensaje))
        conn.commit()

    except Exception as e:
        print(f"Error guardando mensaje broadcast: {e}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    emit('new_broadcast_message', {'emisor': sender, 'mensaje': mensaje}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
