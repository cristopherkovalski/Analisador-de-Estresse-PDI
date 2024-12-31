# Analisador-de-Estresse-PDI
Este projeto realiza a análise de emoções e status de estresse em imagens ou vídeos, utilizando bibliotecas como OpenCV, MTCNN e DeepFace. O script inclui detecção de rosto, análise emocional e pré-processamento de imagens para melhorar a precisão.
1. Clone este repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
2. Crie e ative um ambiente virtual (opcional, mas recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate
3. Instale as dependências:
    ```bash
    pip install -r requirements.txt

## Dependências do Sistema
Certifique-se de ter as seguintes dependências instaladas no sistema:
- OpenCV (cv2)
- MTCNN
- DeepFace

## Uso
1. Execute o script principal:
    ```bash
    python main.py

2. Uma janela gráfica aparecerá, permitindo que você selecione um arquivo:

Imagens: Formatos suportados incluem .jpg, .jpeg, .png.
Vídeos: Formatos suportados incluem .mp4, .avi, .mov.

3. Após o processamento:

Para imagens: Os resultados serão exibidos em uma janela.
#### Exemplo de Saída
Imagem:![Descrição da Imagem](https://drive.google.com/uc?export=view&id=193Gp-7-SIuaPauOYzg1T3ZT2ZXtHph3_)

Para vídeos: Um arquivo processado será salvo no mesmo diretório do vídeo original, com o prefixo processed_.
#### Exemplo de Saída
Vídeo: [ Assista ao vídeo](https://drive.google.com/file/d/1PB2CkURXwwVtUs0V-u2nG-UO2HEloWLk/view?usp=sharing)



