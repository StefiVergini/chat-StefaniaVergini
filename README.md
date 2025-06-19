Programa con sockets y threading que realiza lo siguiente:

Servidor

Permita multiples conexiones lleve la cuenta de las conexiones
Cuando un cliente se conecta envia un menu con 5 opciones

    Comandos        Opciones
 -----------------------------------------------------------------      
    /login          Login
    /send           Enviar mensaje a otro usuario en privado
    /salirchat      Comando para salir de un chat privado (estando en uno)
    /sendall        Enviar mensaje a todos los usuarios conectados
    /show           Mostrar usuarios conectados
    /exit           Salir 

Cliente 

El cliente tiene que poder conectarse al servidor y recibir el menu y poder ingresar una opcion.
Ambas deben ser con dos hilos uno para envio y otro para recepcion.
