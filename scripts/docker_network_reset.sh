#!/bin/bash
# Cleans up stale Docker networks and recreates external networks required by the compose stack.
# Run this after a Docker reset or /var/lib/docker wipe.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Stopping compose stack ==="
docker compose down --remove-orphans || true

echo "=== Removing orphaned bridge interfaces (lost after Docker reset) ==="
for br in $(ip link show type bridge | awk -F': ' '{print $2}' | grep '^br-'); do
    echo "  Removing $br"
    ip link set "$br" down 2>/dev/null || true
    ip link delete "$br" 2>/dev/null || true
done

echo "=== Verifying no conflicting routes remain ==="
ip route | grep '172\.' || echo "No 172.x routes found"

echo "=== Creating external networks ==="
# traefik_proxy: used by traefik, authentik, label-studio, outline, grafana
docker network inspect traefik_proxy >/dev/null 2>&1 || \
    docker network create --subnet 172.26.0.0/16 traefik_proxy

# authentik: internal network for authentik services
docker network inspect authentik >/dev/null 2>&1 || \
    docker network create --subnet 172.27.0.0/16 authentik

# prometheus_network: used by prometheus and exporters
docker network inspect prometheus_network >/dev/null 2>&1 || \
    docker network create --subnet 172.28.0.0/16 prometheus_network

echo "=== Current Docker networks ==="
docker network ls

echo "=== Starting compose stack ==="
docker compose up -d

echo "=== Done ==="
