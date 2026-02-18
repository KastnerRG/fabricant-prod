# wikijs - database

#!/bin/bash
NODE=$HOME/.nvm/versions/node/v24.3.0/bin/node
BW=$HOME/.nvm/versions/node/v24.3.0/lib/node_modules/@bitwarden/cli/build/bw.js
BW_SESSION=`cat .bw_session`
WIKIJS_POSTGRESQL__PASSWORD=`$NODE $BW --session $BW_SESSION get password "wikijs - database"`
echo "DB_PASS=\"$WIKIJS_POSTGRESQL__PASSWORD\"" >> $HOME/fabricant-prod/.secrets/wikijs_db_password.env
echo "POSTGRES_PASSWORD=\"$WIKIJS_POSTGRESQL__PASSWORD\"" >> $HOME/fabricant-prod/.secrets/wikijs_db_password.env
