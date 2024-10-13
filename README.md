
```bash
python -m venv .venv

source .venv/Scripts/activate

pip install -r requirements.txt

docker-compose up -d

uvicorn app:app --reload

```