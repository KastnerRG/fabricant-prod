#!/bin/bash
NODE=$HOME/.nvm/versions/node/v24.3.0/bin/node
BW=$HOME/.nvm/versions/node/v24.3.0/lib/node_modules/@bitwarden/cli/build/bw.js
BW_SESSION=`cat .bw_session`
AUTHENTIK_SECRET_KEY=`$NODE $BW --session $BW_SESSION get password "authentik secret key"`
AUTHENTIK_POSTGRESQL__PASSWORD=`$NODE $BW --session $BW_SESSION get password "9157437f-bdb0-49c5-8538-ac0638b8d145"`
echo "AUTHENTIK_SECRET_KEY=\"$AUTHENTIK_SECRET_KEY\"" > $HOME/fabricant-prod/.secrets/authentik_admin_password.env
echo "AUTHENTIK_POSTGRESQL__PASSWORD=\"$AUTHENTIK_POSTGRESQL__PASSWORD\"" >> $HOME/fabricant-prod/.secrets/authentik_admin_password.env
