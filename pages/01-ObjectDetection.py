import streamlit as st
import json
import cv2
from PIL import Image
import numpy as np
import io
import requests
from urllib.parse import urlparse, unquote

img_path = "../imgs/Selecionados/"


def draw_filled_rectangle_with_opacity(img, pt1, pt2, color, opacity=0.3):
    overlay = img.copy()
    cv2.rectangle(overlay, pt1, pt2, color, -1)

    # mix img/mask
    cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0, img)


def draw_partial_lines_rectangle(img, idt, pt1, pt2, color=(0, 255, 0), thickness=2, line_length_ratio=0.25):
    draw_filled_rectangle_with_opacity(img, pt1, pt2, color=(0, 255, 0, 50))

    x1, y1 = pt1
    x2, y2 = pt2

    height, width, channels = img.shape
    fontScale = width / 900
    thickness = max(1, int(width / 900))

    # comprimento da linha estatico
    line_length_x = int(line_length_ratio * (x2 - x1))
    line_length_y = int(line_length_ratio * (y2 - y1))

    # Desenhar segmentos de linha em cada vértice
    # upper left 
    cv2.line(img, (x1, y1), (x1 + line_length_x, y1), color, thickness)
    cv2.line(img, (x1, y1), (x1, y1 + line_length_y), color, thickness)
    
    # upper right 
    cv2.line(img, (x2, y1), (x2 - line_length_x, y1), color, thickness)
    cv2.line(img, (x2, y1), (x2, y1 + line_length_y), color, thickness)

    # lower left 
    cv2.line(img, (x1, y2), (x1 + line_length_x, y2), color, thickness)
    cv2.line(img, (x1, y2), (x1, y2 - line_length_y), color, thickness)

    # lower right
    cv2.line(img, (x2, y2), (x2 - line_length_x, y2), color, thickness)
    cv2.line(img, (x2, y2), (x2, y2 - line_length_y), color, thickness)

    center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
    text = str(idt)
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale, thickness)[0]
    text_x = center_x - text_size[0] // 2
    text_y = center_y + text_size[1] // 2

    # Center Id / Negrito
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        cv2.putText(img, text, (text_x + dx, text_y + dy), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0,0,0), thickness*4)
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, fontScale, color, thickness)


# Função para extrair o nome do arquivo dos cabeçalhos
def extract_filename_from_content_disposition(content_disposition):
    if "filename=" in content_disposition:
        filename = content_disposition.split('filename=')[1]
        filename = filename.strip('"').strip("'")
        return filename
    return None

# Função para baixar a imagem do Google Drive
def download_image_from_drive(url):
    response = requests.get(url)
    # print(response.headers)
    filename = extract_filename_from_content_disposition(response.headers['Content-Disposition'])
    # print(response.elapsed)
    # print(filename)
    img_array = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img, filename


def get_filename_from_url(url):
    # Analisa a URL
    parsed_url = urlparse(url)
    # Extrai o caminho e decodifica qualquer codificação percentual (ex: espaços)
    path = unquote(parsed_url.path)
    # Obtém apenas o nome do arquivo
    filename = path.split('/')[-1]
    return filename


def main():
    st.title('Seletor de Imagens')

    with open(r'./coordinates.json', 'r') as file:
        data_dict = json.load(file)

    # Interface do usuário para inserir a URL da imagem
    image_url = st.text_input("Enter the image URL from Google Drive:")

    if image_url:
        # Aqui, substitua 'image_url' pela URL direta de download, se necessário
        img, file_name = download_image_from_drive(image_url)
        # file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        # img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        original_img = img.copy()
        
        if file_name in data_dict:
            # Aplica marcações na cópia da imagem
            for idt, coords in data_dict[file_name].items():
                pt1, pt2 = tuple(coords[:2]), tuple(coords[2:])
                draw_partial_lines_rectangle(img, idt, pt1, pt2)
            
            # Converte as imagens de volta para PNG para exibição
            is_success_original, buffer_original = cv2.imencode(".png", original_img)
            io_buf_original = io.BytesIO(buffer_original)
            img_pil_original = Image.open(io_buf_original)

            is_success, buffer = cv2.imencode(".png", img)
            io_buf = io.BytesIO(buffer)
            img_pil = Image.open(io_buf)
            
            # Cria duas colunas para exibir as imagens
            col1, col2 = st.columns(2)
            with col1:
                st.image(img_pil_original, caption="Original Image")
            with col2:
                st.image(img_pil, caption="Processed Image")
            
            # Exibe IDs e coordenadas
            st.write("IDs and Coordinates:")
            for idt, coords in data_dict[file_name].items():
                st.write(f"ID: {idt}, Coordinates: {coords}")
        else:
            st.write("This image name does not match any key in the dictionary.")
        


# Executar o app
if __name__ == "__main__":
    main()
