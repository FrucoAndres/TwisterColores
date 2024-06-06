import random
import cv2
import mediapipe as mp
import time
from gtts import gTTS
import pygame
import threading
import numpy as np

#Función para generar un archivo de audio a partir de un texto
#tiene cómo parametros el texto y el nombre que tendrá el archivo, además del idioma con el que se va a guardar
def text_to_audio(text, filename="output.mp3", lang="es"):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    print(f"Archivo de audio guardado como {filename}")

#Función para reproducir el archivo de audio en un hilo separado
def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

# Generar los archivos de audio
text = "amarillo."
audio_filename1 = "amarillo.mp3"
text_to_audio(text, audio_filename1)

text = "azul"
audio_filename2 = "azul.mp3"
text_to_audio(text, audio_filename2)

text = "rojo"
audio_filename3 = "rojo.mp3"
text_to_audio(text, audio_filename3)

text = "¡Muy bien!"
audio_filename4 = "felicitar1.mp3"
text_to_audio(text, audio_filename4)

text = "Modo daltonico activado, por favor selecciona una de las opciones"
audio_filename5 = "modo_on.mp3"
text_to_audio(text, audio_filename5)

text = "Modo daltonico desactivado"
audio_filename6 = "modo_off.mp3"
text_to_audio(text, audio_filename6)

text = "¡Exacto!"
audio_filename7 = "felicitar2.mp3"
text_to_audio(text, audio_filename7)

text = "¡Correcto!"
audio_filename8 = "felicitar3.mp3"
text_to_audio(text, audio_filename8)

#Lista de audios de felicitacion
audio_list = []
audio_list.append(audio_filename4)
audio_list.append(audio_filename7)
audio_list.append(audio_filename8)

#Intervalo de tiempo en segundos para la nueva reproducción del audio para colores
intervalo = 2

#Intervalo de tiempo en segundos para la nueva reproducción del audio en colores secundarios
intervalo2 = 1

last_played_time = 0

#Variables para el control de modos
order = 1

#Variable para controlar los aciertos en la combinaciòn de colores
aciertos = 0

#Boleanos para controlar que botones o anuncios mostrar
instructions = True

primaryColors = False

secondaryColors = False

color1 = False

color2 = False

#Boleanos para controlar el tipo de miopia

color_blindness = False

protanopia = False

deuteranopia = False

tritanopia = False

#Matriz de transformación de colores para simular protanopía
#Dificultad para percibir el color rojo
protanopia_matrix = np.array([
    [0.567, 0.433, 0],
    [0.558, 0.442, 0],
    [0, 0.242, 0.758]
])

#Matriz de transformación de colores para simular Deuteranopía
#Dificultad para percibir el color verde y el rojo
deuteranopia_matrix = np.array([
    [0.56667, 0.43333, 0],
    [0.55833, 0.44167, 0],
    [0, 0.24167, 0.75833]
])

#Matriz de transformación de colores para simular Tritanopía
#Dificultad para percibir el color azul
tritanopia_matrix = np.array([
    [0.95, 0.05, 0],
    [0, 0.433, 0.567],
    [0, 0.475, 0.525]
])

#Transformar el frame a alguno de los modos de daltonismo
def simulate_color_blindness(frame, matrix):
    return cv2.transform(frame, matrix)

#Función para verificar si un punto está dentro de un rango
def is_point_in_range(point, x_range, y_range):
    x = point[0]
    y = point[1]
    if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
        
        return True

#Diccionario el cual contiene el color en GBR y los límites en (x,y) de los circulos que lo conforman
secondaryColection = {
    
    1: [(0, 128, 0), (610, 670), (400, 460)],
    2: [(0, 82, 2547), (400, 460), (820, 880)],
    3: [(182, 89, 155), (610, 670),(820, 880)]
    
}

#Funcion para determinar si la ubicación de los puntos es correcta para el color secundario
def verify_secondary_color(point1, point2):
    #Llamar la constante de orden
    global order
    global aciertos
    
    #Verificar si los puntos están en el lugar correspondiente
    if(is_point_in_range(point1, secondaryColection[order][1], (540, 600)) == True and is_point_in_range(point2, secondaryColection[order][2], (540, 600)) == True):
            order += 1  
            aciertos += 1 
            return True
            
    elif(is_point_in_range(point2, secondaryColection[order][1], (540, 600)) == True and is_point_in_range(point1, secondaryColection[order][2], (540, 600)) == True):
            order += 1
            aciertos += 1
            return True
            
            
#Funcion para mostrar las instrucciones    
def draw_instruction_box(frame, text, size=(400, 400), color=(0, 255, 0), alpha=0.5):
    #Tomar una copia del frame para dibujar
    overlay = frame.copy()
    alto, ancho, _ = overlay.shape
    centro_x = ancho // 2
    centro_y = alto // 2

    # Dibujar el rectángulo en el frame
    cv2.rectangle(overlay, (centro_x - size[0]//2, centro_y - size[1]//2), 
                  (centro_x + size[0]//2, centro_y + size[1]//2), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    #Fuente del texto de los círculos
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    #Calcular el desplazamiento según el número de líneas
    lines = text.split("\n")
    y_offset = (len(lines) - 1) * 10
    
    #Ajustar el tamaño del texto para que quepa en el botón
    max_text_width = max(cv2.getTextSize(line, font, 0.5, 1)[0][0] for line in lines)
    max_text_height = cv2.getTextSize("A", font, 0.5, 1)[0][1]  # Altura aproximada de un carácter
    text_scale = min((size[0] - 200) / max_text_width, (size[1] - 200) / (max_text_height * len(lines)))

    # Añadir el texto según fuente, posición y demás parámetros
    for i, line in enumerate(lines):
        text_size = cv2.getTextSize(line, font, text_scale, 1)[0]
        text_x = centro_x - text_size[0] // 2
        text_y = centro_y + text_size[1] // 2 - y_offset + i * (max_text_height * text_scale + 5)
        cv2.putText(frame, line, (int(text_x), int(text_y)), font, text_scale, (0, 0, 0), 1)
        
#Función para mostrar el puntaje que lleva el jugador        
def draw_score_box(frame, aciertos, size=(250, 250), color=(0, 255, 0), alpha=0.5):
    # Definir el texto a mostrar
    text = f"Puntaje total\n \n \nAciertos: {aciertos}"
    
    # Tomar una copia del frame para dibujar
    overlay = frame.copy()
    alto, ancho, _ = overlay.shape
    centro_x = ancho // 2
    centro_y = alto // 2

    # Dibujar el rectángulo en el frame
    cv2.rectangle(overlay, (centro_x - size[0]//2, centro_y - size[1]//2), 
                  (centro_x + size[0]//2, centro_y + size[1]//2), color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Fuente del texto de los círculos
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Calcular el desplazamiento según el número de líneas
    lines = text.split("\n")
    y_offset = (len(lines) - 1) * 10
    
    # Ajustar el tamaño del texto para que quepa en el botón
    max_text_width = max(cv2.getTextSize(line, font, 0.5, 1)[0][0] for line in lines)
    max_text_height = cv2.getTextSize("A", font, 0.5, 1)[0][1]  # Altura aproximada de un carácter
    text_scale = min((size[0] - 200) / max_text_width, (size[1] - 200) / (max_text_height * len(lines)))

    # Añadir el texto según fuente, posición y demás parámetros
    for i, line in enumerate(lines):
        text_size = cv2.getTextSize(line, font, text_scale, 1)[0]
        text_x = centro_x - text_size[0] // 2
        text_y = centro_y + text_size[1] // 2 - y_offset + i * (max_text_height * text_scale + 5)
        cv2.putText(frame, line, (int(text_x), int(text_y)), font, text_scale, (0, 0, 0), 1)

#Funcion para dibujar un cuadrado con un texto con parametros más especificos
def draw_label(frame, text, position=(50, 50), size=(200, 50), bg_color=(0, 255, 0), text_color=(0, 0, 0), alpha=0.5):
    # Tomar una copia del frame para dibujar
    overlay = frame.copy()
    
    # Calcular las coordenadas del rectángulo
    top_left = position
    bottom_right = (top_left[0] + size[0], top_left[1] + size[1])
    
    # Dibujar el rectángulo en el frame
    cv2.rectangle(overlay, top_left, bottom_right, bg_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Fuente del texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Calcular el tamaño del texto y ajustar la escala
    text_size = cv2.getTextSize(text, font, 0.5, 1)[0]
    text_scale = min(size[0] / (text_size[0] + 20), size[1] / (text_size[1] + 20))
    
    # Calcular las coordenadas del texto para centrarlo
    text_x = top_left[0] + (size[0] - text_size[0] * text_scale) // 2
    text_y = top_left[1] + (size[1] + text_size[1] * text_scale) // 2
    
    # Añadir el texto
    cv2.putText(frame, text, (int(text_x), int(text_y)), font, text_scale, text_color, 1)
              
#Funcion para dibujar un boton con texto en la pantalla, tiene como parametros el frame, posicion, texto, tamaño, color y transparencia
def draw_button(frame, position, text, size=40, color=(0, 255, 0), alpha=1.0):

    #Tomar una copia del frame para dibujar
    overlay = frame.copy()
    #Dibujar el circulo en el frame
    cv2.circle(overlay, position, size, color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    #Fuente del texto de los circulos
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    #tratar el desplazamiento según el numero de lineas
    lines = text.split()
    y_offset = (len(lines) - 1) * 10
    
    #Segun el numero de palabras añadit el texto según fuente, posición y demás parametros
    for i, line in enumerate(lines):
        text_size = cv2.getTextSize(line, font, 0.5, 1)[0]
        text_x = position[0] - text_size[0] // 2
        text_y = position[1] + text_size[1] // 2 - y_offset + i * 20
        cv2.putText(frame, line, (text_x, text_y), font, 0.5, (0, 0, 0), 1)    
        
    return(int(position[0]), int(position[1]))   

#Funcion para dibujar y los colores secundarios por odern
def draw_secondary_colors(frame, order, size=60, alpha=1):

    # Definir alto y ancho según el frame que se tome
    height, width, _ = frame.shape
    # Con el alto y ancho definir las posiciones de los círculos
    center_x = width // 2
    center_y = height // 2
    position = (center_x, center_y)
    
    #Crear una copia del frame
    overlay = frame.copy()
    
    color = secondaryColection[order][0]
    #Mostrar el circulo
    cv2.circle(overlay, position, size, color, -1)
    
    # Añadirle la opacidad al círculo ya existente
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        

#Funcion para dibujar los tres circulos de los colores primarios, definiendo colores, tamaño, espacio entre ellos y transparencia
def draw_center_circles(frame, colors=[(0, 255, 255), (255, 0, 0), (0, 0, 255)], size=60, spacing=150, alpha=0.4):

    #Definir alto y ancho según el frame que se tome
    height, width, _ = frame.shape
    #Con el alto y ancho definir las posiciones de los círculos
    center_x = width // 2
    center_y = height - 300// 2
    positions = [
        (center_x - size - spacing, center_y),
        (center_x, center_y),
        (center_x + size + spacing, center_y)
    ]
    
    # Crear una copia del frame
    overlay = frame.copy()
    
    #Por cada posición y color, dibujar un círculo en la pantalla
    for position, color in zip(positions, colors):
        cv2.circle(overlay, position, size, color, -1)
    
    #Añadirle la opacidad al círculo ya existente
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
#Herramientas para dibujo de mediapipe
mp_draw = mp.solutions.drawing_utils

#Variable para manos de mediapipe
mp_hands = mp.solutions.hands

#Definir el label, en este caso uno de video
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

#Establecer una resolución más ancha
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # 1280 es común para 720p (16:9)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # 720p

#Obtén la resolución real después de intentar configurarla
fwidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
fheight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Resolución de la cámara: {fwidth}x{fheight}")

#Definir el modo de las manos, para se hace captura dinámica, se detectan dos manos con undice de confianza mayor o igual al 50%
with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5) as hands:
    
    #Capturar frame a frame siempre y cuando sea exitosa la captura
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        
        #Definir y procesar los frame
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = frame.shape
        
        #Dibujar botones en la parte superior (semi-transparentes)
        draw_button(frame, (50 , 70), 'Modo Daltonico', alpha=0.7)
        
        if color_blindness == True:
            draw_button(frame, (50 , 200), 'Pro', alpha=0.7)
            draw_button(frame, (50 , 330), 'Deu', alpha=0.7)
            draw_button(frame, (50 , 460), 'Tri', alpha=0.7)
            draw_button(frame, (50 , 590), 'Cancelar', color= (820, 880), alpha=0.7)
            
        draw_button(frame, (fwidth // 4, 70), 'Colores Primarios', alpha=0.7)
        draw_button(frame, (fwidth * 2// 4, 70), 'Colores Secundarios', alpha=0.7)
        
        #Verificar si la opcion de colores secundarios está activada para mostrar el boton de puntaje
        if secondaryColors == True:
            draw_button(frame, (fwidth * 3// 4, 70), 'Puntaje', alpha=0.7)
        
        #Verificar el límite de indices para los colores secundarios
        if order == 4:
            order = random.randint(1,2)
            
        #Dibujar segunOpcion
        if instructions == True:
            draw_instruction_box(frame, "Instrucciones:\n \n \nMueve tu dedo indice hacia una\n \nde las opciones para practicar:\n \nColores primarios o secundarios.")
        elif primaryColors == True:
            draw_center_circles(frame)
        else:
            secondaryColors = True
            draw_center_circles(frame)
            draw_secondary_colors(frame, order)
        results = hands.process(frame_rgb)

        #Colecciones para los dos puntos
        x_tips = []
        y_tips = []
        #Dibujar landmarks de los dedos indices y verificar opciones
        if results.multi_hand_landmarks:
            x_tips.clear
            y_tips.clear
            for hand_landmarks in results.multi_hand_landmarks:
                x1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * width)
                y1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * height)
                x_tips.append(x1)
                y_tips.append(y1)
                cv2.circle(frame, (x1,y1), 3, (255, 0, 0), 3)
                if is_point_in_range((x1, y1),(610, 670),(50, 90)) == True:
                    instructions = False
                    primaryColors = False
                    secondaryColors = True
                elif is_point_in_range((x1, y1),(300, 340),(50, 90)) == True:
                    instructions = False
                    primaryColors = True
                    secondaryColors = False
                
                if secondaryColors == True:
                    if is_point_in_range((x1, y1),(940, 980),(50, 90)) == True:
                        draw_score_box(frame,aciertos)
                        
                current_time2 = time.time() 
                if is_point_in_range((x1, y1),(30, 70),(50, 90)) == True:
                    if (current_time2 - last_played_time) >= 5:
                        threading.Thread(target=play_audio, args=(audio_filename5,)).start()
                        last_played_time = current_time2
                    color_blindness = True
                    
                if color_blindness == True:
                    if is_point_in_range((x1, y1),(30, 70),(180, 220)) == True:
                        protanopia = True
                        deuteranopia = False
                        tritanopia = False
                    elif is_point_in_range((x1, y1),(30, 70),(310, 350)) == True:
                        deuteranopia = True
                        protanopia = False
                        tritanopia = False
                    elif is_point_in_range((x1, y1),(30, 70),(440, 480)) == True:
                        tritanopia = True
                        protanopia = False
                        deuteranopia = False
                    elif is_point_in_range((x1, y1),(30, 70),(570, 610)) == True:
                        color_blindness = False
                        tritanopia = False
                        protanopia = False
                        deuteranopia = False
                        if (current_time2 - last_played_time) >= 5:
                            threading.Thread(target=play_audio, args=(audio_filename6,)).start()
                            last_played_time = current_time2
                        
                    
        if primaryColors == True:
            #Tomar el tiempo actual
            current_time = time.time() 
            for i in range(0, len(x_tips)):
                if is_point_in_range((x_tips[i], y_tips[i]),(400, 460),(540, 600)):
                    
                    if (current_time - last_played_time) >= intervalo:
                        threading.Thread(target=play_audio, args=(audio_filename1,)).start()
                        last_played_time = current_time
                    
                    draw_label(frame, "Amarillo", position=(120, 150), size=(250, 40), bg_color=(0, 255, 255), text_color=(0, 0, 0), alpha=0.7)    
                elif is_point_in_range((x_tips[i], y_tips[i]),(610, 670),(540, 600)):
                    
                    if (current_time - last_played_time) >= intervalo:
                        threading.Thread(target=play_audio, args=(audio_filename2,)).start()
                        last_played_time = current_time
        
                    draw_label(frame, "Azul", position=(520, 150), size=(250, 40), bg_color=(255, 0, 0), text_color=(0, 0, 0), alpha=0.7)
                elif is_point_in_range((x_tips[i], y_tips[i]),(820, 880),(540, 600)):
                    
                    if (current_time - last_played_time) >= intervalo:
                        threading.Thread(target=play_audio, args=(audio_filename3,)).start()
                        last_played_time = current_time
                    draw_label(frame, "Rojo", position=(920, 150), size=(250, 40), bg_color=(0, 0, 255), text_color=(0, 0, 0), alpha=0.7)
                    
            
                        
        #Verificar si se leyeron los dos puntos y está habilitada la opción de colores secundarios            
        if secondaryColors == True and len(x_tips) == 2:
                current_time = time.time() 
                if verify_secondary_color((x_tips[0],y_tips[0]),(x_tips[1],y_tips[1])) == True:
                    audio = random.randint(0,2)
                    if (current_time - last_played_time) >= intervalo2:
                        threading.Thread(target=play_audio, args=(audio_list[audio],)).start()
                        last_played_time = current_time
        
        #Verificar que modos de daltonismo están activos para mostrar en el frame   
        if protanopia == True:
            frame = simulate_color_blindness(frame, protanopia_matrix)
        elif deuteranopia == True:
            frame = simulate_color_blindness(frame, deuteranopia_matrix)
        elif tritanopia == True:             
            frame = simulate_color_blindness(frame, tritanopia_matrix)
                    
        alto, ancho, _ = frame.shape
        centro_x = ancho // 2
        centro_y = alto // 2               
        cv2.imshow("Video", frame)
        
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
cap.read()        
cv2.destroyAllWindows()