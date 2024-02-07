import streamlit as st
from openai import OpenAI
import json
import yaml

if 'result' not in st.session_state:
    st.session_state['result'] = None

def page_traffic_sentinel():
    client = OpenAI(api_key="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")
    st.title('Análise de Acidentes de Trânsito com AI')

    # Input da URL da imagem
    image_url = st.text_input("Digite a URL da imagem hospedada:")

    # Input de coordenadas
    coord_input = st.text_input("Digite as coordenadas (formato 'latitude, longitude'):")

    # Botão para análise da imagem
    if st.button("Analisar Imagem"):
        if image_url and coord_input:
            # Formata as coordenadas para o formato esperado pela API
            coordinates = {"latitude": coord_input.split(',')[0].strip(), "longitude": coord_input.split(',')[1].strip()}
            coordinates_str = f"{coordinates['latitude']}, {coordinates['longitude']}"

            # Envia a requisição para a API OpenAI
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Pense como um analista de trânsito para entender os motivos do veículo parado, veja a imagem e escreva uma breve descrição do evento em questão. Informando o possível tipo e causa do evento nas coordenadas: {coordinates_str}\n\nBaseado na imagem e nas coordenadas, você responda de maneira resumida, uma a duas linhas para cada pergunta\n\nQ1: Localização do Veículo. (Em que posição ele está na imagem?) \nQ2: Qual o tipo de veículo que está vinculado ao acidente. (Classe, Cor e Modelo)\nQ3: Estado do Veículo. (Se parece estar danificado, ou se foi apenas uma falha mecânica) \nQ4:Condições da Rodovia. (Fluxo da rodovia, interditada ou fluindo)\nQ5: Condições climáticas da Rodovia. (Chuva, Nublada, Ensolarada)\nQ6:Possíveis Obstáculos ou Perigos. (Algum destroço ou liquído na rodovia)\nQ7:Sinais de atividade. (Se alguma pessoa está tentando resolver a situação)\nQ8:Identificação Macro. (Identificar marcas, empresas, etc)n\nDentre as perguntas acima, informe o que é necessário fazer nas opções abaixo:\n\n- Acionar apenas a Polícia Rodoviária\n- Acionar Resgate e Polícia Rodoviária\n- Acionar Resgate, Polícia Rodoviária e Corpo de bombeiros\n\nDevolva a resposta apenas no formato abaixo, sem mais nenhum texto além desse\n\n## Exemplo da saída em JSON ##\n\n{{\n  \"description\": \"descrição do cenário de modo geral\",\n  \"q1\": \"Aproximadamente 15 veículos.\",\n  \"q2\": \"Sedan de cor clara.\",\n  \"q3\": \"Sim, uma faixa está obstruída e o fluxo nas faixas adjacentes está lento.\",\n  \"q4\": \"Clima claro e ensolarado.\",\n  \"q5\": \"Um pequeno grupo de pessoas está ao redor do acidente.\"\"q6\": \"Destroços na avenida.\",\n\"q7\": \"Uma pessoa resolvendo o problema.\"  \"q8\": \"Marca de iogurt.\"\"call_problems\": \"Acionar Resgate e Polícia Rodoviária.\"\n Retorne o texto em Português-brasil}}"                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    }
                ],
                max_tokens=3000,
            )

            # Exibe o resultado
            result = response.choices[0]
            st.write(result)

            # Armazena e exibe o resultado
            result = response.choices[0] if response.choices else None
            if result:
                st.text("Resultado:")
                st.write(result.message.content)

                # Constrói o objeto JSON com a URL da imagem incluída
                result_data = json.loads(result.message.content)
                result_data['url_img'] = image_url  # Adiciona a URL da imagem ao dicionário

                # Salva o resultado em um arquivo JSON
                try:
                    with open("output.json", "w", encoding='utf-8') as file:
                        json.dump(result_data, file, ensure_ascii=False, indent=4)
                    st.success("Arquivo JSON salvo automaticamente com sucesso.")
                except Exception as e:
                    st.error(f"Erro ao salvar o arquivo JSON: {e}")
        else:
            st.warning("Por favor, insira a URL da imagem e as coordenadas.")

# Chamar a função principal
page_traffic_sentinel()
