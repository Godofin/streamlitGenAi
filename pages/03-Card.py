import cv2
import numpy as np
import streamlit as st
import json
import requests

def load_data(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        st.error(f"File {filename} not found.")
        return None

def download_image_from_drive(url):
    response = requests.get(url)
    img_array = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def main():
    st.title("Detalhes do Incidente")
    
    data = load_data("output.json")
    if data is not None:

        image = download_image_from_drive(data["url_img"])
        if image is not None:
            st.image(image, caption="Cena do Incidente", use_column_width=True)
    
        st.subheader("Descrição do Incidente:")
        st.info(data["description"])
        
        # Detalhes Adicionais fora das colunas
        st.subheader("Detalhes Adicionais:")
        questions = [
            "Indicação de onde o veículo está localizado na imagem (esquerda, direita, centro, fundo)",
            "Informação da classe, cor e modelo do veículo envolvido no acidente",
            "Descrição do estado do veículo e definição de dados aparentes",
            "Estado do tráfego no momento do acidente (interditado, fluindo)",
            "Condições climáticas da Rodovia. (Chuva, Nublada, Ensolarada)",
            "Possíveis Obstáculos ou Perigos encontrados na rodovia.  (destroços, líquidos)",
            "Sinais de atividade humana no envolto do acidente. (Se alguma pessoa está tentando resolver a situação)",
            "Identificação Macro. (Identificar marcas, empresas, etc)"
        ]
        
        for idx, question in enumerate(questions, start=1):
            st.markdown(f"**Q{idx}) {question}**")  
            st.markdown(f"*{data[f'q{idx}']}*")  

    
        st.subheader("Ações Recomendadas:")
        st.error(data["call_problems"])

if __name__ == "__main__":
    main()
