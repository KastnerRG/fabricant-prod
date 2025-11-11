#!/bin/bash
NODE=$HOME/.nvm/versions/node/v24.3.0/bin/node
BW=$HOME/.nvm/versions/node/v24.3.0/lib/node_modules/@bitwarden/cli/build/bw.js
BW_SESSION=`cat .bw_session`
AUTHENTIK_TRAEFIK_TOKEN=`$NODE $BW --session $BW_SESSION get password "Authentik Traefik Token"`
echo "AUTHENTIK_TOKEN=\"$AUTHENTIK_TRAEFIK_TOKEN\"" > $HOME/fabricant-prod/.secrets/authentik_traefik_token.env
