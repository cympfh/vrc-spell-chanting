FROM python:3.11-slim

# Install node
RUN apt update && apt install -y curl
RUN curl -L git.io/nodebrew | perl - setup
RUN $HOME/.nodebrew/nodebrew install-binary v19.5.0 && \
    $HOME/.nodebrew/nodebrew use v19.5.0
ENV PATH "/root/.nodebrew/current/bin:$PATH"

WORKDIR /app

# Build apps
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt
COPY . .
RUN cd web && npm i && npm run build

# Clean up
RUN apt remove -y curl && \
    apt autoremove -y && \
    apt clean -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.nodebrew && \
    rm -rf /app/web/node_modules && \
    rm -rf /app/web/src
