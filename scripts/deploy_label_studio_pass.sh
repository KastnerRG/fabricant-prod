#!/bin/bash
NODE=$HOME/.nvm/versions/node/v24.3.0/bin/node
BW=$HOME/.nvm/versions/node/v24.3.0/lib/node_modules/@bitwarden/cli/build/bw.js
BW_SESSION=`cat .bw_session`
LABEL_ADMIN_PASSWD=`$NODE $BW --session $BW_SESSION get password "E4E Label Studio Admin Password"`
PG_PASSWD=`$NODE $BW --session $BW_SESSION get password "fabricant label_studio postgres"`
echo "LABEL_STUDIO_PASSWORD=\"$LABEL_ADMIN_PASSWD\"" > $HOME/fabricant-prod/.secrets/label_studio_admin_password_pg.env
echo "POSTGRES_USER=\"$PG_PASSWD\"" >> $HOME/fabricant-prod/.secrets/label_studio_admin_password_pg.env
