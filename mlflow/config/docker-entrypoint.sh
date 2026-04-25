#!/bin/sh
set -e

exec mlflow server \
  --backend-store-uri "$MLFLOW_BACKEND_STORE_URI" \
  --artifacts-destination "${MLFLOW_ARTIFACTS_DESTINATION:-/mlflow/artifacts}" \
  --serve-artifacts \
  --app-name oidc-auth \
  --host 0.0.0.0 \
  --port 5000
