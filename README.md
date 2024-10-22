# fabricant
fabricant.ucsd.edu configuration

# Bootstrapping
1. Create and install a GitHub deploy key
2. Ensure that the system can SSH into itself
3. Install Python3.12
4. Clone this repo
```
git clone git@github.com:UCSD-E4E/kastner-ml.git /home/e4eadmin/
```
5. Create a venv at `/home/e4eadmin/kastner-ml/.venv`
```
python3.12 -m venv /home/e4eadmin/kastner-ml/.venv`
```
6. Activate venv
```
source /home/e4eadmin/kastner-ml/.venv/
```
7. Install dependencies
```
python -m pip install --upgrade pip poetry
cd /home/e4eadmin/kastner-ml/.venv/
poetry install
```
9. Install Bitwarden Client
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash # install nvm
source ~/.bashrc # activate nvm
nvm install v22.9.0 # install node 22.9.0
nvm exec v22.9.0 # activate node
npm install -g @bitwarden/cli # installs bw
bw config server https://vault.e4e-gateway.ucsd.edu # configures bw to our vault
bw login # Logs in
```
10. Bootstrap creds
```
bw unlock --raw > .bw_session
```
8. Install
```
ansible-playbook playbook.yml
```