import keyboard
import time
import threading
import queue
import pygame
import sys
import pygame.time



class Game:
    def __init__(self, protocol, Player_id):
        self.protocol = protocol
        self.Player_id = Player_id
        self.comandos = {'arriba': False, 'abajo': False}
        self.received_message_queue = queue.Queue()
        self.received_message = "No hay Comando"
        self.message_to_send = ""
        self.datos = []
        self.setup_pygame()
        
    def setup_pygame(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.window = pygame.display.set_mode((self.width, self.height))
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        self.paddle_width, self.paddle_height = 10, 100
        self.paddle_speed = 50
        self.ball_radius = 10
        self.ball_speed_x = 7
        self.ball_speed_y = 7

        self.paddle1_x, self.paddle1_y = 10, (self.height - self.paddle_height) // 2
        self.paddle2_x, self.paddle2_y = self.width - 20, (self.height - self.paddle_height) // 2
        self.ball_x, self.ball_y = (self.width - self.ball_radius) // 2, (self.height - self.ball_radius) // 2

        self.puntaje_jugador1 = 0
        self.puntaje_jugador2 = 0

        self.font = pygame.font.Font(None, 74)
        self.game = True
        self.game_over = False
        

    def receive_data(self):
        while True:
            self.protocol_message = self.protocol.receive()
            if self.protocol_message:
                self.datos = self.protocol_message.split()
                self.received_message_queue.put(self.datos[0])

    def draw_elements(self):
                self.window.fill(self.BLACK)
                pygame.draw.rect(self.window, self.WHITE, (self.paddle1_x, self.paddle1_y, self.paddle_width, self.paddle_height))
                pygame.draw.rect(self.window, self.WHITE, (self.paddle2_x, self.paddle2_y, self.paddle_width, self.paddle_height))
                pygame.draw.circle(self.window, self.WHITE, (self.ball_x, self.ball_y), self.ball_radius)

                # Dibuja el marcador
                score_text = self.font.render(f"{self.puntaje_jugador1} - {self.puntaje_jugador2}", True, self.WHITE)
                score_rect = score_text.get_rect(center=(self.width / 2, 50))
                self.window.blit(score_text, score_rect)

    def send_movement_message(self):
        message_to_send = f"Movement {self.ball_x} {self.ball_y} {self.paddle1_y} {self.paddle2_y}"
        self.protocol.send(message_to_send)


    def presionoUpArrow(self):
        while True:
            if keyboard.is_pressed('up arrow'):
                self.comandos['arriba'] = True
                time.sleep(0.5)

    def presionoDownArrow(self):
        while True:
            if keyboard.is_pressed('down arrow'):
                self.comandos['abajo'] = True
                time.sleep(0.5)

    def main(self):
        self.receiver_thread = threading.Thread(target=self.receive_data)
        self.Arriba_thread = threading.Thread(target=self.presionoUpArrow)
        self.Abajo_thread = threading.Thread(target=self.presionoDownArrow)

        self.receiver_thread.start()
        self.Arriba_thread.start()
        self.Abajo_thread.start()

        while self.game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Lógica para verificar si la bola sale del campo y asignar puntaje
            if self.ball_x - self.ball_radius < 0 or self.ball_x + self.ball_radius > self.width:
                if self.ball_x - self.ball_radius < 0:
                    self.puntaje_jugador2 += 1
                else:
                    self.puntaje_jugador1 += 1

                # Reinicia la posición de la bola
                self.ball_x = self.width // 2
                self.ball_y = self.height // 2
                self.paddle1_x, self.paddle1_y = 10, (self.height - self.paddle_height) // 2
                self.paddle2_x, self.paddle2_y = self.width - 20, (self.height - self.paddle_height) // 2

                # Verifica si algún jugador ha alcanzado 5 puntos
                if self.puntaje_jugador1 == 5:
                    self.game_over = True
                    self.winner = "Jugador 1"
                elif self.puntaje_jugador2 == 5:
                    self.game_over = True
                    self.winner = "Jugador 2"

            if self.game_over:
                # Dibuja el mensaje de que el juego terminó
                font = pygame.font.Font(None, 74)
                end_text = font.render("Game Over", True, self.WHITE)
                end_text_rect = end_text.get_rect(center=(self.width / 2, self.height / 2 - 50))
                self.window.blit(end_text, end_text_rect)
                
                # Dibuja todo
                self.draw_elements()
                
                # Dibuja el mensaje del ganador
                winner_text = font.render(f"Ganador: {self.winner}", True, self.WHITE)
                winner_text_rect = winner_text.get_rect(center=(self.width / 2, self.height / 2 + 50))
                self.window.blit(winner_text, winner_text_rect)

                # Actualiza la ventana
                pygame.display.flip()

                # Espera un evento de teclado para reiniciar
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        # Resetea las posiciones de los palos y la bola
                        self.paddle1_y = (self.height - self.paddle_height) // 2
                        self.paddle2_y = (self.height - self.paddle_height) // 2
                        self.ball_x = (self.width - self.ball_radius) // 2
                        self.ball_y = (self.height - self.ball_radius) // 2
                        self.puntaje_jugador1 = 0
                        self.puntaje_jugador2 = 0
                        self.game_over = True
                        break
                
                pygame.time.delay(5000)
                pygame.quit()
                sys.exit()
            else:
                # 4 if para revisar si el cliente presionó una tecla y mover la raqueta según su id
                if self.comandos['arriba'] and self.paddle1_y > 0 and self.Player_id == 1:
                    self.paddle1_y -= self.paddle_speed
                    self.send_movement_message()
                    self.comandos['arriba'] = False

                if self.comandos['abajo'] and self.paddle1_y < self.height - self.paddle_height and self.Player_id == 1:
                    self.paddle1_y += self.paddle_speed
                    self.send_movement_message()
                    self.comandos['abajo'] = False

                if self.comandos['arriba'] and self.paddle2_y > 0 and self.Player_id == 2:
                    self.paddle2_y -= self.paddle_speed
                    self.send_movement_message()
                    self.comandos['arriba'] = False

                if self.comandos['abajo'] and self.paddle2_y < self.height - self.paddle_height and self.Player_id == 2:
                    self.paddle2_y += self.paddle_speed
                    self.send_movement_message()
                    self.comandos['abajo'] = False
                
                # Lógica de movimiento de la bola
                self.ball_x += self.ball_speed_x
                self.ball_y += self.ball_speed_y
                if self.ball_y - self.ball_radius < 0 or self.ball_y + self.ball_radius > self.height:
                    self.ball_speed_y = -self.ball_speed_y

                # Lógica de detección de colisión con los palos
                if (self.paddle1_x < self.ball_x < self.paddle1_x + self.paddle_width and
                    self.paddle1_y < self.ball_y < self.paddle1_y + self.paddle_height) or (
                    self.paddle2_x < self.ball_x < self.paddle2_x + self.paddle_width and
                    self.paddle2_y < self.ball_y < self.paddle2_y + self.paddle_height):
                    self.ball_speed_x = -self.ball_speed_x
                
                if self.datos:
                    self.ball_x = int(self.datos[1])
                    self.ball_y = int(self.datos[2])
                    self.paddle1_y = int(self.datos[3])
                    self.paddle2_y = int(self.datos[4])
                    self.datos = []

                # Dibuja todo
                self.draw_elements()

                # Actualiza la ventana
                pygame.display.flip()
                pygame.time.Clock().tick(30)
                time.sleep(0.03)
        
        pygame.quit()
        sys.exit()
