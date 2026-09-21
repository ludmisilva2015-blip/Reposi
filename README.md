# Catroid APK Converter — starter

Esta pasta contém a primeira API do projeto.

## Executar

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Abra `http://127.0.0.1:8000/docs`.

Endpoints:
- `GET /health`
- `POST /analyze` — recebe um arquivo `.catrobat` e valida o pacote ZIP.

Esta versão ainda não gera APK.
