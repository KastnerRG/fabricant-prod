#!/bin/bash
NODE=$HOME/.nvm/versions/node/v24.3.0/bin/node
BW=$HOME/.nvm/versions/node/v24.3.0/lib/node_modules/@bitwarden/cli/build/bw.js
BW_SESSION=`cat .bw_session`
POSTGRES_PASSWORD=`$NODE $BW --session $BW_SESSION get password "Outline POSTGRES_PASSWORD"`
OIDC_CLIENT_SECRET=`$NODE $BW --session $BW_SESSION get password "Outline OIDC_CLIENT_SECRET"`
SECRET_KEY=`$NODE $BW --session $BW_SESSION get password "Outline SECRET_KEY"`
UTILS_SECRET=`$NODE $BW --session $BW_SESSION get password "Outline UTILS_SECRET"`
echo "POSTGRES_PASSWORD=\"$POSTGRES_PASSWORD\"" > $HOME/fabricant-prod/.secrets/outline_secrets.env
echo "OIDC_CLIENT_SECRET=\"$OIDC_CLIENT_SECRET\"" >> $HOME/fabricant-prod/.secrets/outline_secrets.env
echo "SECRET_KEY=\"$SECRET_KEY\"" >> $HOME/fabricant-prod/.secrets/outline_secrets.env
echo "UTILS_SECRET=\"$UTILS_SECRET\"" >> $HOME/fabricant-prod/.secrets/outline_secrets.env
echo "DATABASE_URL=\"postgres://outline_user:$POSTGRES_PASSWORD@outline_postgres:5432/outline\"" >> $HOME/fabricant-prod/.secrets/outline_secrets.env
