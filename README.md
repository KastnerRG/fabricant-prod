# fabricant
fabricant.ucsd.edu configuration

# Bootstrapping
1. Create and install a GitHub deploy key
2. Ensure that the system can SSH into itself
3. Install Python3.12
4. Clone this repo
```
git clone git@github.com:KastnerRG/fabricant.git /home/fabricant-admin/fabricant
```
5. Install Bitwarden Client
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash # install nvm
source ~/.bashrc # activate nvm
nvm install v24.3.0 # install node 24.3.0
nvm exec v24.3.0 # activate node
npm install -g @bitwarden/cli # installs bw
bw config server https://vault.e4e-gateway.ucsd.edu # configures bw to our vault
bw login # Logs in
```
6. Bootstrap creds
```
bw unlock --raw > ~/fabricant-prod/.bw_session
```
7. Create a venv at `~/fabricant-prod/.venv`
```
python3.12 -m venv ~/fabricant-prod/.venv
```
8. Activate venv
```
source ~/fabricant-prod/.venv/bin/activate
```
9. Install dependencies
```
python -m pip install --upgrade pip poetry
cd ~/fabricant-prod/
poetry install
```
10. Install
```
ansible-playbook playbook.yml
```