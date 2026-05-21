FROM python:3.12-slim

# Éviter l'écriture de fichiers .pyc sur disque et forcer la sortie standard sans buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système requises (outils de compilation, wget, curl, ca-certificates, git, et polices/librairies graphiques)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    ca-certificates \
    tar \
    xz-utils \
    git \
    build-essential \
    libfontconfig1 \
    libxt6 \
    && rm -rf /var/lib/apt/lists/*

# Installer Go-Task
RUN curl -sL https://taskfile.dev/install.sh | sh -s -- -b /usr/local/bin

# Installer Typst (compilation PDF ultra-rapide)
ENV TYPST_VERSION="0.11.0"
RUN wget -O /tmp/typst.tar.xz "https://github.com/typst/typst/releases/download/v${TYPST_VERSION}/typst-x86_64-unknown-linux-musl.tar.xz" \
    && tar -xf /tmp/typst.tar.xz -C /tmp/ \
    && mv /tmp/typst-x86_64-unknown-linux-musl/typst /usr/local/bin/ \
    && rm -rf /tmp/typst.tar.xz /tmp/typst-x86_64-unknown-linux-musl

# Installer Quarto CLI (détection automatique de la dernière version stable de GitHub si non spécifiée)
ARG QUARTO_VERSION="latest"
RUN if [ "$QUARTO_VERSION" = "latest" ]; then \
        QUARTO_VERSION=$(curl -s https://api.github.com/repos/quarto-dev/quarto-cli/releases/latest | grep '"tag_name":' | sed -E 's/.*"tag_name": "v?([^"]+)".*/\1/'); \
    fi \
    && echo "Installing Quarto version: ${QUARTO_VERSION}" \
    && wget -O /tmp/quarto.deb "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb" \
    && dpkg -i /tmp/quarto.deb || apt-get install -f -y \
    && rm -f /tmp/quarto.deb

# Copier uniquement les requirements.txt pour optimiser le cache de build Docker
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Configurer le noyau Jupyter (Kernel) pour Quarto
RUN python -m ipykernel install --user --name=venv-projet --display-name="Python (Projet Data Science)"

# Copier le reste du code du projet
COPY . .

# Exposer le port par défaut de Quarto Preview
EXPOSE 4815

# Commande par défaut pour lancer quarto preview sur le rapport
# --host 0.0.0.0 : pour rendre le serveur accessible depuis l'hôte
# --port 4815    : port fixe à exposer
# --no-browser   : désactive l'ouverture auto d'un navigateur interne au conteneur
CMD ["quarto", "preview", "report/rapport.qmd", "--host", "0.0.0.0", "--port", "4815", "--no-browser"]
