import socket
import threading
import os
# Configuración del servidor para conexion ip y puerto
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))



# diccionario para almacenar las conexiones de los clientes / usuarios 

# clientes almacena clave = el obj socket valor = IP:Puerto 
# se usa clientes si el usuario no se logueo para encontrarlo
clientes = {}

# usuarios almacena clave = nombre de usuario logueado (no puede haber 2 iguales) valor = obj socket
# se usa usuarios cuando el cliente se logueo
usuarios = {}

#diccionario de conversaciones privadas
conversaciones = {}

# Menú inicial para los clientes
MENU = """Seleccione una opción:
    /login   - Login
    /send    - Enviar mensaje a otro usuario
    /sendall - Enviar mensaje a todos los usuarios conectados
    /show    - Mostrar usuarios conectados
    /exit    - Salir
"""

#manejar cliente
# funcion para manejar al cliente
# recibe las peticiones del cliente en base a su seleccion del menu
# se encarga de redirigir a otras funciones para ejecutar 
# las solicitudes del cliente
def handle_client(client_socket, address):

    # 1) Nombre del cliente por default apenas se conecta (IP:PUERTO)
    nombre_temporal = f"{address[0]}:{address[1]}"
    clientes[client_socket] = nombre_temporal
    usuarios[nombre_temporal] = client_socket

    print(f"Cliente conectado desde {address}")
    print(f"Total de usuarios conectados: {len(clientes)}")

    # 2) Mostar al cliente el Menú
    client_socket.sendall(MENU.encode('utf-8'))

    # 3) Ejecutar los comandos del Menú
    while True:
        try:
            message = client_socket.recv(4096).decode('utf-8').strip()
            if not message:
                # El cliente cerró la conexión de repente
                break

            # conversacion privada: si 2 usuarios estan en una conversacion privada
            if client_socket in conversaciones:

                # comando para salir de un chat/conversación privada -- '/salirchat'
                if message == "/salirchat":
                    partner = conversaciones[client_socket]
                    client_socket.sendall("Saliste del chat privado.\n".encode('utf-8'))
                    partner.sendall(f"{clientes.get(client_socket, 'Desconocido')} ha salido del chat privado.\n".encode('utf-8'))
                    # eliminar la conversación en ambos usuarios
                    del conversaciones[partner]
                    del conversaciones[client_socket]
                    # enviar el menu a ambos usuarios
                    client_socket.sendall(MENU.encode('utf-8'))
                    partner.sendall(MENU.encode('utf-8'))

                else:
                    partner = conversaciones[client_socket]
                    partner.sendall(
                        f"[Privado] {clientes.get(client_socket, 'Desconocido')}: {message}\n".encode('utf-8')
                    )
                # No se procesa nada mas que el chat privado hasta no salir, es decir no aparecera el menu    
                continue 
                 
            # Salir
            if message == "/exit":
                # se llama a la funcion de salir
                finalizar = exit_server(client_socket)
                if finalizar:
                    print(f"{nombre_temporal} se ha desconectado.")
                    print(f"Total de usuarios conectados: {len(clientes)}")
                    break

            #login
            elif message == "/login":
                # se llama a la función de login
                exitoso = login_server(client_socket)
                if exitoso:
                    # Mostrar al servidor el nuevo nombre
                    nuevo_nombre = clientes[client_socket]
                    print(f"Cliente {address} ahora es '{nuevo_nombre}'")
                    print(f"Total de usuarios conectados: {len(clientes)}")
                # Después de /login, enviar menú de nuevo
                client_socket.sendall(MENU.encode('utf-8'))

            #mensaje privado
            elif message == "/send":
                # se llama a la función de chat privado
                send_server(client_socket, conversaciones)

            #enviar a todos
            elif message == "/sendall":
                # se llama a la función para enviar un mensaje a todos
                sendall_server(client_socket)
                # Después de /sendall, enviar menú de nuevo
                client_socket.sendall(MENU.encode('utf-8'))

            #mostrar usuarios conectados
            elif message == "/show":
                show_server(client_socket)
                # Después de /show, enviar menú de nuevo
                client_socket.sendall(MENU.encode('utf-8'))

            #usuario eligio una opcion que no existe:
            else:
                client_socket.sendall("Ingreso una opción inexistente. Por favor intente nuevamente\n".encode('utf-8'))
                client_socket.sendall(MENU.encode('utf-8'))

        except Exception as e:
            # ante un error inesperado, se elimina con pop al usuario y cerramos dicha conexion
            print("Error en handle_client:", e)
            nombre = clientes.pop(client_socket, None)
            if nombre in usuarios:
                usuarios.pop(nombre, None)
            client_socket.close()
            print(f"Total de usuarios conectados: {len(clientes)}")
            break


def login_server(client_socket):
    # /login
    # funcion encargada de permitir al usuario
    # ingresar un nombre de usuario
    # verifica que no sea igual a otro usuario
    # guarda el nombre elegido para que se visualice
    # entre los otros usuarios conectados
    # borra el nombre de usuario por default
    try:
        # 1) Recibe el nombre de usuario
        username = client_socket.recv(1024).decode('utf-8').strip()

        # 2) Comprobar si ya existe un nombre igual -> si existe no le permite continuar
        if username in clientes.values():
            client_socket.sendall(
                "Ese nombre ya está en uso. Intente otro.\n".encode('utf-8')
            )
            return False

        # 3) se borra el 'login por default' (IP:puerto) en usuarios{}
        anterior = clientes[client_socket]
        usuarios.pop(anterior, None)

        # 4) Guardar el nuevo nombre de usuario
        clientes[client_socket] = username
        usuarios[username] = client_socket
        client_socket.sendall(f"Login exitoso. Bienvenido, {username}!\n".encode('utf-8'))
        return True

    except Exception:
        # Si hay error retorna False
        return False

def send_server(client_socket, conversaciones):
    #/send
    # funcion encargada de enviar un mensaje a otro usuario
    # de forma privada
    # Solicita el nombre del destinatario.
    # Si se encuentra conectado (y no es el mismo que el emisor), se crea un chat privado bidireccional.
    # Si no está disponible, informa el error y vuelve al menú.
    try:
        # input se pasa al lado del cliente, traia conflictos
        #client_socket.sendall("¿A qué usuario deseas enviar mensajes?: ".encode('utf-8'))
        # se selecciona con quien iniciar un chat
        destinatario = client_socket.recv(1024).decode('utf-8').strip()

        # si se elige a si mismo, no permite continuar
        if destinatario == clientes.get(client_socket, ""):
            client_socket.sendall("No puedes iniciar chat contigo mismo.\n".encode('utf-8'))
            # se envia el menu nuevamente
            client_socket.sendall(MENU.encode('utf-8'))
            return

        # si no se reconoce al usuario ingresado
        if destinatario not in usuarios:
            client_socket.sendall("Ese usuario no está conectado.\n".encode('utf-8'))
            # se envia el menu nuevamente
            client_socket.sendall(MENU.encode('utf-8'))
            return

        # si encuentra al destinatario que cree la variable para iniciar la conversacion
        partner_socket = usuarios[destinatario]

        # checkeo si el destinatario no esta ya en un chat privado con otra persona, no permite enviar
        if client_socket in conversaciones or partner_socket in conversaciones:
            client_socket.sendall("El destinatario ya está en una conversación privada. Intente mas tarde\n".encode('utf-8'))
            client_socket.sendall(MENU.encode('utf-8'))
            return

        # Si no sucede nada que impida, se inicia el chat privado para ambos usuarios
        conversaciones[client_socket] = partner_socket
        conversaciones[partner_socket] = client_socket

        client_socket.sendall(
            f"Iniciaste chat privado con {destinatario}. Escribe tus mensajes (usa /salirchat para salir).\n".encode('utf-8')
        )
        partner_socket.sendall(
            f"{clientes.get(client_socket, 'Desconocido')} ha iniciado un chat privado contigo.\n Escribe para responder o usa /salirchat para salir.\n".encode('utf-8')
        )
    except Exception:
        client_socket.sendall("Error al iniciar chat privado.\n".encode('utf-8'))


def show_server(client_socket):
    #/show
    # funcion encargada de mostrar los nombres de todos los usuario conectados
    try:
        # recorre y almacena en una lista los valores del dic clientes
        lista = [nombre for nombre in clientes.values()]
        cantidad = len(lista)
        # se muestra la totalidad de conectados y los nombres
        texto = f"Usuarios conectados ({cantidad}):\n" + "\n".join(lista) + "\n"
        client_socket.sendall(texto.encode('utf-8'))
    except Exception:
        client_socket.sendall("Error al obtener usuarios conectados.\n".encode('utf-8'))

def sendall_server(client_socket):

    #/sendall
    # Funcion encargada de enviar un mensaje a todos los usuarios conectados
    # Pide al cliente el mensaje que quiere enviar a todos.
    # Reenvía ese texto a todos los sockets en 'clientes', excepto al emisor.

    try:
        # Pedir mensaje del lado del cliente
        #client_socket.sendall("Escriba el mensaje para todos: ".encode('utf-8'))
        texto = client_socket.recv(4096).decode('utf-8').strip()

        # Obtener nombre del emisor (IP:puerto o username)
        emisor = clientes.get(client_socket, "Desconocido")

        # Construir el formato del mensaje
        mensaje_formateado = f"[Todos] {emisor}: {texto}\n"

        # Reenviar a todos excepto al emisor
        for sock in clientes:
            if sock != client_socket:
                try:
                    if sock in conversaciones:
                        # Están en chat privado → mostrar encabezado y mensaje global
                        sock.sendall("[Mensaje global recibido]\n".encode('utf-8'))
                        sock.sendall(mensaje_formateado.encode('utf-8'))
                    else:
                        # Están en el menú u otra interacción → mostrar mensaje + menú
                        sock.sendall(mensaje_formateado.encode('utf-8'))
                        sock.sendall(MENU.encode('utf-8'))
                except:
                    pass

        # Confirmar al emisor
        client_socket.sendall(f"[Tú → todos]: {texto}\n".encode('utf-8'))
        

    except Exception:
        client_socket.sendall("Error al enviar mensaje a todos.\n".encode('utf-8'))

def exit_server(client_socket):
    #/exit
    # funcion encargada de salir de la conexion
    # borra al usuario que elige la opcion de salir
    # cierra la conexion a ese cliente
    # obtener al cliente que selecciona /exit
    nombre = clientes.get(client_socket, None)
    if nombre:
        # se elimina de clientes y usuarios
        del clientes[client_socket]
        usuarios.pop(nombre, None)

    client_socket.sendall("Desconectando...\n".encode('utf-8'))
    client_socket.close()

    #retornar true para finalizar el bucle de handle    
    return True



#inicializacion del servidor  socket.AF_INET (IP tipo ipv4) socket.SOCK_STREAM (de tipo TCP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#bind() donde el socket va a recibir las conexiones asociando la ip y el puerto
server_socket.bind((HOST, PORT))
#servidor se queda en escucha para recibir las conexiones - 5 conexiones en cola maximo
server_socket.listen(5)

print("Servidor escuchando en", HOST, ":", PORT)

while True:
    #aceptar la conexion
    client_socket, client_address = server_socket.accept()
    #inicializacion del hilo parael cliente, se asocia el socket y la direccion
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
