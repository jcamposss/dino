from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image
import time


# Variáveis globais
width, height = 800, 320
jumper_x, jumper_y = -200, -40
jumper_dy = 0
jumper_state = "ready"
obstacle_x, obstacle_dx = 200, -2
score = 0
lives = 3
gravity = -0.8
game_state = "start"
paused = False
resume_counter = 0
# Variáveis globais para os dois obstáculos
OBSTACLE_SPACING = 500  # Espaçamento fixo entre os obstáculos
second_obstacle_x = 400 + OBSTACLE_SPACING  # Segundo obstáculo começa ainda mais à frente
# Adicione uma nova variável global para a posição vertical do segundo obstáculo
second_obstacle_y = 5 # Altura inicial do segundo obstáculo
# Ajuste o tamanho da imagem do segundo obstáculo
SECOND_OBSTACLE_WIDTH = 40  # Largura ajustada da textura
SECOND_OBSTACLE_HEIGHT = 35  # Altura ajustada da textura


# Variáveis para texturas
background_texture = None
dinosaur_texture = None
dinosaur_ducking_texture = None
cactus_texture = None
second_obstacle_texture = None

# Função para carregar textura a partir de uma imagem
def load_texture(path):
    img = Image.open(path)
    img = img.convert("RGBA")
    img_data = img.tobytes()
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return texture_id

# Inicialização do OpenGL e texturas
def init():
    global background_texture, dinosaur_texture, dinosaur_ducking_texture, cactus_texture, second_obstacle_texture
    glClearColor(0, 0, 0, 1)
    glOrtho(-400, 400, -160, 160, -1, 1)
    glEnable(GL_TEXTURE_2D)
    background_texture = load_texture("background.png")
    dinosaur_texture = load_texture("Dino.png")
    dinosaur_ducking_texture = load_texture("Dino2.png")
    cactus_texture = load_texture("cacto.png")
    second_obstacle_texture = load_texture("passaro.png")

# Função para desenhar o plano de fundo
def draw_background():
    glBindTexture(GL_TEXTURE_2D, background_texture)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(-400, -160)
    glTexCoord2f(1, 1); glVertex2f(400, -160)
    glTexCoord2f(1, 0); glVertex2f(400, 160)
    glTexCoord2f(0, 0); glVertex2f(-400, 160)
    glEnd()

# Função para desenhar o dinossauro com textura
def draw_jumper():
    # Selecionar a textura com base no estado do dinossauro
    if jumper_state == "ducking":
        glBindTexture(GL_TEXTURE_2D, dinosaur_ducking_texture)  # Textura para dinossauro abaixado
    else:
        glBindTexture(GL_TEXTURE_2D, dinosaur_texture)  # Textura para dinossauro normal

    glPushMatrix()
    glTranslate(jumper_x, jumper_y, 0)

    if jumper_state == "ducking":
        # Dinossauro abaixado com textura reduzida
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(-20, 0)
        glTexCoord2f(1, 1); glVertex2f(20, 0)
        glTexCoord2f(1, 0); glVertex2f(20, 25)
        glTexCoord2f(0, 0); glVertex2f(-20, 25)
        glEnd()
    else:
        # Dinossauro em posição normal
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(-20, 0)
        glTexCoord2f(1, 1); glVertex2f(20, 0)
        glTexCoord2f(1, 0); glVertex2f(20, 50)
        glTexCoord2f(0, 0); glVertex2f(-20, 50)
        glEnd()

    glPopMatrix()

# Função para desenhar o obstáculo
def draw_obstacle():
    glBindTexture(GL_TEXTURE_2D, cactus_texture)
    glPushMatrix()
    glTranslate(obstacle_x, -40, 0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(-8, 0)
    glTexCoord2f(1, 1); glVertex2f(8, 0)
    glTexCoord2f(1, 0); glVertex2f(8, 30)
    glTexCoord2f(0, 0); glVertex2f(-8, 30)
    glEnd()
    glPopMatrix()

# Função para desenhar o segundo obstáculo
def draw_second_obstacle():
    glBindTexture(GL_TEXTURE_2D, second_obstacle_texture)
    glPushMatrix()
    glTranslate(second_obstacle_x, second_obstacle_y, 0)  # Use a nova posição Y
    glBegin(GL_QUADS)
    # Definir vértices alinhados ao tamanho da textura
    glTexCoord2f(0, 1); glVertex2f(-SECOND_OBSTACLE_WIDTH / 2, 0)  # Inferior esquerdo
    glTexCoord2f(1, 1); glVertex2f(SECOND_OBSTACLE_WIDTH / 2, 0)   # Inferior direito
    glTexCoord2f(1, 0); glVertex2f(SECOND_OBSTACLE_WIDTH / 2, SECOND_OBSTACLE_HEIGHT)  # Superior direito
    glTexCoord2f(0, 0); glVertex2f(-SECOND_OBSTACLE_WIDTH / 2, SECOND_OBSTACLE_HEIGHT)  # Superior esquerdo
    glEnd()
    glPopMatrix()
# Função para desenhar o texto (pontuação e vidas)
def draw_text(text, x, y, r, g, b):
    glPushMatrix()
    glColor3f(r, g, b)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glPopMatrix()

# Função para pular e abaixar o dinossauro
def key_down(key, x, y):
    global jumper_dy, jumper_state, game_state
    if game_state == "start" and key == b'\r':  # Inicia o jogo ao pressionar Enter
        reset_game()
        game_state = "play"
    elif game_state == "game_over" and key == b'\r':  # Reinicia o jogo ao pressionar Enter após Game Over
        reset_game()
        game_state = "play"
    elif game_state == "play":
        if key == GLUT_KEY_UP and jumper_state == "ready":
            jumper_dy = 12
            jumper_state = "jumping"
        elif key == GLUT_KEY_DOWN and jumper_state == "ready":
            jumper_state = "ducking"

def key_up(key, x, y):
    global jumper_state
    if key == GLUT_KEY_DOWN and jumper_state == "ducking":
        jumper_state = "ready"


def check_collision():
    global lives, game_state
    
    # Dimensões do dinossauro em estado normal e abaixado
    dino_width, dino_height = (40, 50) if jumper_state != "ducking" else (40, 25)
    
    # Bounding box do dinossauro
    dino_left = jumper_x - dino_width / 2
    dino_right = jumper_x + dino_width / 2
    dino_bottom = jumper_y
    dino_top = jumper_y + dino_height

    # Bounding box do primeiro obstáculo
    cactus_width, cactus_height = 16, 30
    cactus_left = obstacle_x - cactus_width / 2
    cactus_right = obstacle_x + cactus_width / 2
    cactus_bottom = -40
    cactus_top = cactus_bottom + cactus_height

    # Bounding box do segundo obstáculo
    second_width, second_height = 20, 35
    second_left = second_obstacle_x - second_width / 2
    second_right = second_obstacle_x + second_width / 2
    second_bottom = second_obstacle_y
    second_top = second_bottom + second_height

    # Verificar colisão com o primeiro obstáculo
    if (dino_right > cactus_left and dino_left < cactus_right and
        dino_top > cactus_bottom and dino_bottom < cactus_top):
        lives -= 1
        reset_obstacle()

    # Verificar colisão com o segundo obstáculo
    if (dino_right > second_left and dino_left < second_right and
        dino_top > second_bottom and dino_bottom < second_top):
        lives -= 1
        reset_second_obstacle()

    # Verificar Game Over
    if lives <= 0:
        game_state = "game_over"

# Função para reiniciar o obstáculo
def reset_obstacle():
    global obstacle_x
    obstacle_x = second_obstacle_x + OBSTACLE_SPACING  # Reposicionar com espaçamento fixo

# Função para reiniciar o segundo obstáculo
def reset_second_obstacle():
    global second_obstacle_x
    second_obstacle_x = obstacle_x + OBSTACLE_SPACING  # Reposicionar o segundo obstáculo no final da tela

def draw_pause_menu():
    # Fundo do menu
    glColor3f(0.1, 0.1, 0.1)  # Cinza escuro
    glBegin(GL_QUADS)
    glVertex2f(-150, 50)
    glVertex2f(150, 50)
    glVertex2f(150, -50)
    glVertex2f(-150, -50)
    glEnd()

    # Contorno do menu
    glColor3f(1, 1, 1)  # Branco
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(-150, 50)
    glVertex2f(150, 50)
    glVertex2f(150, -50)
    glVertex2f(-150, -50)
    glEnd()

    # Opção "Continuar Jogo"
    draw_text("1. Continuar Jogo", -120, 20, 1, 1, 1)
    # Opção "Reiniciar Jogo"
    draw_text("2. Reiniciar Jogo", -120, -10, 1, 1, 1)

# Função para gerenciar cliques do menu de pausa
# Função para gerenciar cliques do menu de pausa
def handle_pause_menu_click(x, y):
    global paused, resume_counter, game_state
    # Conversão da posição do clique para coordenadas do OpenGL
    gl_x = (x / width) * 800 - 400
    gl_y = 160 - (y / height) * 320

    print(f"Detectado clique em: ({gl_x}, {gl_y})")  # Para depuração

    if -150 <= gl_x <= 150:  # Dentro do menu horizontalmente
        if 0 <= gl_y <= 50:  # Opção "Continuar Jogo"
            print("Opção: Continuar Jogo")
            paused = False
            resume_counter = 5  # Contagem regressiva para retornar ao jogo
        elif -50 <= gl_y < 0:  # Opção "Reiniciar Jogo"
            print("Opção: Reiniciar Jogo")
            reset_game()
            reset_second_obstacle()
            paused = False
            game_state = "play"

# Modificar a função mouse_click para lidar com o menu de pausa
def mouse_click(button, state, x, y):
    global game_state, paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        print(f"Mouse clique detectado: ({x}, {y})")  # Para depuração
        if game_state == "start":  # Inicia o jogo com clique esquerdo
            reset_game()
            game_state = "play"
        elif game_state == "game_over":  # Reinicia o jogo com clique esquerdo
            reset_game()
            game_state = "play"
        elif paused:  # Gerencia cliques no menu de pausa
            handle_pause_menu_click(x, y)

# Função para resetar o jogo
def reset_game():
    global score, lives, jumper_y, jumper_dy, jumper_state, obstacle_dx, obstacle_x
    score = 0
    lives = 3
    jumper_y = -40
    jumper_dy = 0
    jumper_state = "ready"
    obstacle_dx = -5
    obstacle_x = 400

# Função para alternar a pausa usando a tecla Enter
def toggle_pause(key, x, y):
    global paused, game_state, resume_counter
    if key == b'\r' and game_state == "play":  # Tecla Enter para pausar ou retomar
        if paused:
            paused = False
            resume_counter = 5  # Contagem regressiva para retomar o jogo
        else:
            paused = True

# Atualização do jogo com ambos os obstáculos
def update(value):
    global jumper_y, jumper_dy, jumper_state, obstacle_x, obstacle_dx, second_obstacle_x, score, resume_counter

    if game_state == "play" and not paused:
        if resume_counter == 0:
            # Atualizar a posição do dinossauro
            if jumper_state == "jumping":
                jumper_dy += gravity
                jumper_y += jumper_dy
                if jumper_y <= -40:
                    jumper_y = -40
                    jumper_dy = 0
                    jumper_state = "ready"

            # Mover os obstáculos
            obstacle_x += obstacle_dx
            second_obstacle_x += obstacle_dx

            # Reposicionar o primeiro obstáculo ao sair da tela
            if obstacle_x < -400:
                reset_obstacle()
                score += 1
                obstacle_dx -= 0.5  # Aumentar a dificuldade progressivamente

            # Reposicionar o segundo obstáculo ao sair da tela
            if second_obstacle_x < -400:
                reset_second_obstacle()
                score += 1

            # Verificar colisões
            check_collision()
        else:
            resume_counter -= 1  # Contador de pausa

    glutPostRedisplay()
    glutTimerFunc(1000 if resume_counter > 0 else 16, update, 0)

# Função de exibição com estado de pausa
def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    draw_background()
    draw_jumper()
    draw_obstacle()
    draw_second_obstacle()

    if game_state == "start":
        draw_text("Clique para iniciar", -80, 0, 0, 0, 0)
    elif game_state == "play":
        if paused:
            draw_pause_menu()
        elif resume_counter > 0:
            draw_text(f"Voltando em: {resume_counter}", -80, 0, 0, 0, 0)
    elif game_state == "game_over":
        draw_text("Game Over", -50, 20, 1, 0, 0)
        draw_text("Clique para resetar", -80, 0, 0, 0, 0)
    
    draw_text(f"Pontuação: {score}", 190, -150, 0, 0, 0)
    draw_text(f"Vidas: {lives}", 320, -150, 0, 0, 0)
    draw_ground()

    glutSwapBuffers()

# Função para desenhar o chão
def draw_ground():
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    glVertex2f(-400, -40)
    glVertex2f(400, -40)
    glEnd()


# Configuração da janela
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutCreateWindow(b"Projeto Final")

init()
glutDisplayFunc(display)
glutKeyboardFunc(toggle_pause)
glutSpecialFunc(key_down)
glutSpecialUpFunc(key_up)
glutMouseFunc(mouse_click)
glutTimerFunc(16, update, 0)
glutMainLoop()