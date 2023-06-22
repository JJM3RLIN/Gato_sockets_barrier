import socket
#JMJA
class GatoCliente:
    def __init__(self):
        self.server_address = ('localhost', 1234)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)

    def iniciar(self):
        m_inicio =self.client_socket.recv(1024).decode()
        print(m_inicio)
        if "No se aceptan más jugadores" in m_inicio:
            print("Lo sentimos")
            return
        else:
            ficha = input('Ingrese su ficha para jugar: ')
            self.client_socket.send(ficha.encode())
            
        while True:
            mensaje = self.client_socket.recv(1024).decode()
            if mensaje.startswith("Tablero:"):
                tab_str = mensaje[8:]
                print("Tablero actual:")
                print(tab_str)
            if "Casilla" in mensaje:
                print("Casilla utilizada\n Pierdes tu turno")
            if 'Turno' in mensaje:
                print("Es tu turno")
                casillas = input("Introduce la casilla en donde vas a tirar (1,A):")
                self.client_socket.send(casillas.encode())
            if "gano" in mensaje or "empate" in mensaje:
                print(mensaje)
                break

                

# Crear objeto del cliente del juego del gato
gato_client = GatoCliente()
gato_client.iniciar()

