import socket
import threading

# Configuración del cliente
HOST = 'chat-server'
PORT = 5000
def receive_messages(client_socket):
    #Recibir los mensajes del servidor en un hilo separado
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message, end="")
        except:
            break

# Inicialización del cliente socket.AF_INET (IP tipo ipv4) socket.SOCK_STREAM (de tipo TCP)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# conexion del cliente
client_socket.connect((HOST, PORT))

# Iniciar hilo para recibir mensajes
#daemon true si el cliente cierra la ventana que se se cierre para queel programa no se quede colgado esperando que ese hilo termine
threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()


# Permitir que el usuario ingrese opciones
while True:
    option = input("> ").strip()
    client_socket.sendall(option.encode('utf-8'))
    #ingresar el nombre de usuario
    if option == "/login":
        username = input("Ingrese su nombre de usuario: ")
        client_socket.sendall(username.encode('utf-8'))
    elif option == "/send":
        #client_socket.sendall("Escriba el mensaje para todos: ".encode('utf-8'))
        partner = input("¿A qué usuario deseas enviar mensajes?: ")
        client_socket.sendall(partner.encode('utf-8'))
    elif option == "/sendall":
        texto = input("Escriba el mensaje para enviar a todos los usuarios: ")
        client_socket.sendall(texto.encode('utf-8'))
    elif option == "/exit":
        break
#cerrar conexion
client_socket.close()
