# Wine Rate

Aplicação web responsiva para registrar e avaliar vinhos degustados.
Django 5 · Django REST Framework · PostgreSQL · Bootstrap 5 · Chart.js.

Cada usuário acessa apenas os próprios vinhos. A leitura de rótulo por IA
(`POST /api/wines/identify-label`) **só devolve dados**: o registro é gravado
somente quando o usuário revisa e clica em "Salvar vinho".

## Rodar localmente (virtualenv)

Requisitos: Python 3.12+ e PostgreSQL 15+.

```bash
createdb winerate
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # ajuste DJANGO_SECRET_KEY e DATABASE_URL
python manage.py migrate
python manage.py createsuperuser
python manage.py test
python manage.py runserver
```

Gerar uma chave secreta:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Abra http://localhost:8000 . Localmente mantenha `DJANGO_DEBUG=True`
(com `False` o projeto força HTTPS).

## Rodar com Docker Compose

```bash
cp .env.example .env
docker compose up --build
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
```

## Leitura de rótulo

- `LABEL_VISION_PROVIDER=mock` (padrão): devolve dados fixos de exemplo, sem custo.
- `LABEL_VISION_PROVIDER=anthropic`: envia a foto a um modelo de visão. Defina
  `ANTHROPIC_API_KEY` e, se quiser, `LABEL_VISION_MODEL`.

A imagem é processada em memória e descartada; nada é armazenado.

## Endpoints

| Método | Rota | Observação |
|---|---|---|
| POST | `/api/register` | Cria conta, devolve token e abre sessão |
| POST | `/api/login` | Idem |
| GET | `/api/wines` | Filtros: `name`, `country`, `grape`, `rating`, `rating_min`, `tasting_year`; `ordering` |
| POST | `/api/wines` | O dono é definido no servidor |
| GET/PUT/PATCH/DELETE | `/api/wines/{id}` | 404 para vinho de outro usuário |
| POST | `/api/wines/identify-label` | Multipart com `image`; não grava nada |
| GET | `/api/dashboard` | Resumo, melhor vinho, último cadastrado e contagens |

Clientes externos usam `Authorization: Token <token>`.

## Deploy

- **Render:** `render.yaml` + `build.sh` (crie um Blueprint apontando para o repositório).
- **Railway:** `Procfile`; adicione o plugin PostgreSQL, defina as variáveis do
  `.env.example` e inclua `python manage.py collectstatic --noinput` no build.
- **VPS Linux:** modelos em `deploy/winerate.service` e `deploy/nginx-winerate.conf`
  (gunicorn por socket Unix + Nginx + Certbot).

Em produção defina sempre `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS` e
`DJANGO_CSRF_TRUSTED_ORIGINS` (com `https://`). Depois rode
`python manage.py check --deploy`.

## Migrações

As migrações iniciais já acompanham o projeto. Se alterar modelos:

```bash
python manage.py makemigrations
python manage.py migrate
```
