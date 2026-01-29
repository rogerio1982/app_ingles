# Imagem base
FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia o requirements primeiro (boa prática)
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

# Expõe a porta usada pela aplicação
EXPOSE 5000

# Comando para rodar o app
CMD ["python", "app.py"]
