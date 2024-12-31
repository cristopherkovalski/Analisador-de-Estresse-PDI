from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog
import cv2
import os
from mtcnn import MTCNN
from deepface import DeepFace
import numpy as np

# Inicializa o detector MTCNN
detector = MTCNN()

# Função para pré-processamento de imagens
def preprocess_image(image_path):
    # Carregar imagem
    img = cv2.imread(image_path)

    # Converter para escala de cinza
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calcular brilho médio
    mean_brightness = np.mean(gray_image)

    # Definir limiares
    bright_threshold = 200  # Imagem muito clara
    dark_threshold = 50     # Imagem muito escura

    if mean_brightness > bright_threshold:
        # Imagem muito clara: aplicar CLAHE para melhorar contraste localmente
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_image = clahe.apply(gray_image)
        print("Imagem identificada como muito clara, aplicando CLAHE.")
    elif mean_brightness < dark_threshold:
        # Imagem muito escura: aplicar equalização do histograma
        enhanced_image = cv2.equalizeHist(gray_image)
        print("Imagem identificada como muito escura, aplicando equalização do histograma.")
    else:
        # Brilho normal: manter a imagem original
        enhanced_image = gray_image
        print("Imagem com brilho equilibrado, sem pré-processamento adicional.")

    # Converter de volta para BGR para compatibilidade com DeepFace
    processed_image = cv2.cvtColor(enhanced_image, cv2.COLOR_GRAY2BGR)

    return img, gray_image, enhanced_image, processed_image

# Função para análise de emoções em uma face
def detect_emotions_in_face(face):
    try:
        result = DeepFace.analyze(face, actions=['emotion'], enforce_detection=False)
        return result[0]['dominant_emotion']
    except Exception as e:
        print(f"Erro ao detectar emoção: {e}")
        return None

# Função para determinar o status de estresse
def determine_stress_status(emotion):
    stress_filter = ['fear', 'angry', 'sad']
    return "Estressado" if emotion in stress_filter else "Calmo"

# Função para processar imagens
def process_image(image_path):
    original_img, gray_img, equalized_img, processed_img = preprocess_image(image_path)

    # Exibir imagens intermediárias
    cv2.imshow("Imagem Original", original_img)
    cv2.imshow("Imagem em Escala de Cinza", gray_img)
    cv2.imshow("Imagem Equalizada", equalized_img)

    # Detectar rostos na imagem processada
    results = detector.detect_faces(processed_img)

    for result in results:
        x, y, width, height = result['box']
        face = processed_img[y:y + height, x:x + width]
        emotion = detect_emotions_in_face(face)
        stress_status = determine_stress_status(emotion)

        if emotion:
            cv2.putText(processed_img, f"{stress_status}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if stress_status == "Calmo" else (0, 0, 255), 2)
        cv2.rectangle(processed_img, (x, y), (x + width, y + height),
                      (0, 255, 0) if stress_status == "Calmo" else (0, 0, 255), 2)

    # Exibir imagem final com detecções
    cv2.imshow("Imagem Processada com Detecções", processed_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def process_frame(frame, last_box, no_detection_counter):
    results = detector.detect_faces(frame)
    if results:
        # Atualiza o box para a nova detecção
        for result in results:
            x, y, width, height = result['box']
            face = frame[y:y + height, x:x + width]
            emotion = detect_emotions_in_face(face)
            stress_status = determine_stress_status(emotion)

            if emotion:
                cv2.putText(frame, f"{stress_status}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if stress_status == "Calmo" else (0, 0, 255), 2)
            cv2.rectangle(frame, (x, y), (x + width, y + height),
                          (0, 255, 0) if stress_status == "Calmo" else (0, 0, 255), 2)

            last_box = (x, y, width, height)
        no_detection_counter = 0
    else:
        # Se não houver detecção, mantém o último box por um período
        if last_box and no_detection_counter < 10:  # Tolerância de até 10 frames
            x, y, width, height = last_box
            cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 255, 0), 2)
            no_detection_counter += 1
        elif no_detection_counter >= 10:
            last_box = None  # Limpa o box após tolerância

    return frame, last_box, no_detection_counter

# Função para processar vídeos
def process_video(video_path, output_path, frame_skip=3):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erro ao abrir o vídeo!")
        return

    # Configurar saída de vídeo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = int(cap.get(cv2.CAP_PROP_FPS)) // frame_skip  # Reduz o FPS na saída
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    last_box = None  # Última caixa de detecção
    no_detection_counter = 0  # Contador para frames sem detecção
    frame_count = 0  # Contador de frames

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_skip == 0:  # Pula frames conforme definido
                future = executor.submit(process_frame, frame, last_box, no_detection_counter)
                futures.append(future)

            frame_count += 1

        for future in futures:
            processed_frame, last_box, no_detection_counter = future.result()
            out.write(processed_frame)  # Escreve o frame processado no vídeo

    cap.release()
    out.release()
    print(f"Vídeo processado salvo em {output_path}")
    

def select_file():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal do Tkinter

    file_path = filedialog.askopenfilename(
        title="Selecione um arquivo",
        filetypes=[
            ("Imagens", "*.jpg;*.jpeg;*.png"),
            ("Vídeos", "*.mp4;*.avi;*.mov"),
            ("Todos os arquivos", "*.*")
        ]
    )

    if file_path:
        process_file(file_path)  # Processa o arquivo selecionado
    else:
        print("Nenhum arquivo selecionado.")

# Função principal para identificar o tipo de arquivo e processar
def process_file(file_path):
    if not os.path.exists(file_path):
        print("Arquivo não encontrado!")
        return

    file_ext = os.path.splitext(file_path)[-1].lower()

    if file_ext in ['.jpg', '.jpeg', '.png']:
        print("Processando imagem...")
        process_image(file_path)
    elif file_ext in ['.mp4', '.avi', '.mov']:
        print("Processando vídeo...")
        output_path = "processed_3frames_" + os.path.basename(file_path)
        process_video(file_path, output_path)
    else:
        print("Tipo de arquivo não suportado!")

# Executa o seletor de arquivos
if __name__ == "__main__":
    select_file()