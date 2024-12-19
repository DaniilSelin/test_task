FROM ubuntu:latest
LABEL authors="DaniilSelin)"

WORKDIR /eKom

COPY . /eKom

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libpq-dev \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-dev


RUN python3 -m venv venv

RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV PYTHONPATH=/eKom

EXPOSE 5000

# Этот скрипт не мой, т. к. DNS от docker не разреал имя mongo
# ПОэтому я решил просто заранее получать его ip и с ним уже работать
RUN echo '#!/bin/bash\n' \
         'MONGO_IP=$(getent hosts mongo | awk "{ print \$1 }")\n' \
         'if [ -z "$MONGO_IP" ]; then\n' \
         '  echo "Warning: MongoDB IP not found. Using localhost:27017 as fallback.";\n' \
         '  MONGO_IP="localhost";\n' \
         'else\n' \
         '  echo "MongoDB IP found: $MONGO_IP";\n' \
         'fi\n' \
         'sed -i "s|localhost:27017|$MONGO_IP:27017|g" /eKom/.env\n' \
         'echo "Environment variable updated in /eKom/.env";\n' \
         'exec "$@"\n' > /start.sh && chmod +x /start.sh

# Используем этот скрипт как точку входа
ENTRYPOINT ["/start.sh"]

CMD ["./venv/bin/python3", "-m", "flask", "run"]