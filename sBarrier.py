import socket
import threading
#JMJA
class GatoServer:
    def __init__(self, num_jugadores):
        self.barrier = None
        self.turn_lock = threading.Lock()
        self.turno_actual = 0
        self.letras = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'I':8}
        self.modo_juego = {'1': 3, '2':5}
        self.jugadores = []
        self.casillas_jugadores = []
        self.fichas = []
        self.num_jugadores = num_jugadores
        self.tableroSize = self.modo_juego[input("1.Principiante\n2.Avanzado\nSelecciona una opción:")]
        self.tablero = [['*' for x in range(self.tableroSize)] for i in range(self.tableroSize)]

    def empezar(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 1234))
        server_socket.listen()
        print('Servidor en ejecución. Esperando jugadores...')
    
        while True:
            client_socket, client_address = server_socket.accept()
            print(f'Jugador conectado: {client_address}')
            if len(self.jugadores) >= self.num_jugadores:
                client_socket.send('El número máximo de jugadores ha sido alcanzado. No se aceptan más jugadores.'.encode())
                client_socket.close()
                continue
            self.jugadores.append(client_socket)
            if len(self.jugadores) >= self.num_jugadores:
                self.barrier = threading.Barrier(self.num_jugadores)
            t = threading.Thread(target=self.aceptar_jugador, args=(client_socket,))
            t.start()

    def aceptar_jugador(self, client_socket):
        player_id = self.jugadores.index(client_socket) + 1
        client_socket.send(f'¡Bienvenido, jugador {player_id}!\n'.encode())
        ficha = client_socket.recv(1024).decode()
        self.casillas_jugadores.append([])
        self.fichas.append(ficha)

        if self.barrier is not None:
            self.barrier.wait()  #Esperar a que todos los jugadores estén conectados

        
        while True:
            with self.turn_lock:
                #Para que pueda ir por turnos seguidos
                if player_id != self.turno_actual+1:
                    self.broadcast('Espera tu turno...\n')
                    continue   
                self.broadcast(f'Tablero:\n{self.dibujar()}\n')
                client_socket.send('Turno'.encode())
                casillas = client_socket.recv(1024).decode().split(',')
                fila= int(casillas[0]) - 1
                #Obtener el valor de la letra
                col = self.letras[casillas[1]]
                self.jugar(player_id, fila, col)
                self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
            #Esperando que todos realicen su tirada para continuar
            self.barrier.wait()

    def jugar(self, player_id, fila, col):
        ficha = self.fichas[player_id - 1]
        #Haciendo el tiro
        if(self.tablero[fila][col] != '*'):
             print("Casilla utilizada")
             self.jugadores[player_id-1].send("Casilla utilizada".encode())
        else:
            self.tablero[fila][col] = ficha
            print(self.dibujar())
            self.casillas_jugadores[self.fichas.index(ficha)].append([fila, col])
            check_juego = self.verificar_juego(player_id-1)
            if check_juego[0]:
                mensaje = check_juego[1]
                self.broadcast(mensaje)
                

    def verificar_juego(self, player_id):
        
        columnas_ganadoras = [[[x,i] for x in range(self.tableroSize)] for i in range(self.tableroSize)]
        filas_ganadoras = [[[i, x] for x in range(self.tableroSize)] for i in range(self.tableroSize)]
        tab = [i for x  in self.tablero for i in x]
        # Ordenar el arreglo en base al primer elemento de cada subarreglo
        tiradas_ordenadas_columna =  sorted(self.casillas_jugadores[player_id], key=lambda x: x[0])
        tiradas_ordenadas_fila =  sorted(self.casillas_jugadores[player_id], key=lambda x: x[1])
        if tab.count('*') == 0:        
            return [True, "Al parecer es un empate!!! \n"]
        if tiradas_ordenadas_columna in columnas_ganadoras or tiradas_ordenadas_fila in filas_ganadoras:
            return [True ,f'El jugador {player_id+1} gano!!! \n']
        return [False]
    #Mandar mensaje de que alguien gano o perdio
    def broadcast(self, mensaje):
            for jugador in self.jugadores:
                 jugador.send(mensaje.encode())
    def dibujar(self):
        tableroStr = ''
        #Obteniendo solo hasta la posición de self.tableroSize
        columnas = '  ' + '|'.join(list(self.letras.keys())[:self.tableroSize]) + '\n'
        filas = [x+1 for x in list(self.letras.values())]
        tableroStr += columnas

        #division para separar filas
        tableroStr += '-+'*self.tableroSize + '-' + '\n'
        
        for x in range(self.tableroSize):
            tableroStr += str(filas[x]) + '|' + '|'.join(self.tablero[x]) + '\n'
            if x != self.tableroSize-1: 
                tableroStr +='-+'*self.tableroSize + '-' + '\n'
         
        return tableroStr


num_jugadores = int(input("Introduce el numero de jugadores: "))

# Crear objeto del servidor del juego del gato
gato_server = GatoServer(num_jugadores)
gato_server.empezar()
