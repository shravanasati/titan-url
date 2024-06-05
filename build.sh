python3.9 -m venv venv
source venv/bin/activate
echo "installing npm dependencies"
npm ci
npm run build
echo "installing python dependencies"
pip install -r requirements.txt