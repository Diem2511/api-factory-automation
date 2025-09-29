#!/usr/bin/env bash
set -Eeuo pipefail

echo "== Asegurar grupo docker =="
if ! getent group docker >/dev/null; then
  sudo groupadd docker
fi

echo "== Añadir tu usuario al grupo docker (idempotente) =="
sudo usermod -aG docker "$USER"

echo "== Habilitar y reiniciar servicio docker =="
sudo systemctl enable --now docker
sudo systemctl restart docker

echo "== Arreglar permisos del socket si hiciera falta =="
if [ -S /var/run/docker.sock ]; then
  ls -l /var/run/docker.sock || true
  if [ "$(stat -c %G /var/run/docker.sock)" != "docker" ]; then
    sudo chgrp docker /var/run/docker.sock
  fi
  sudo chmod 660 /var/run/docker.sock
fi

echo "== Ver grupos del usuario =="
id
groups

echo "== Probar acceso usando sg docker (sin relogin) =="
sg docker -c 'docker ps; docker compose version'

echo "== Reconstruir stack con sg docker =="
cd "/home/su/api-factory-automation"
sg docker -c 'docker compose down -v || true; docker compose up -d --build; docker compose ps'

echo "== Fin. Si tu shell actual no ve el grupo, ejecuta: newgrp docker"
