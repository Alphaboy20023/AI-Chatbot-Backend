## Quick orientation

This repo is a small Django REST project (Django 5.2.x) with a simple rule-based AI assistant component. The fastest way to become productive here is to read the key files below and follow the targeted examples and gotchas in this doc.

## Big-picture architecture

- Django project: `victorAi/` (standard startproject layout). Entry: `manage.py` and `victorAi/settings.py`.
- Main app: `victorAiApp/` — contains models, serializers, very small views, and a rule-based prompt table in `ai_prompts.py`.
- API surface: DRF APIViews / serializers are used to accept user messages and persist conversation data; authentication uses `rest_framework_simplejwt`.
- Data flow (simplified): incoming request -> serializer -> models: `UserChat`, `VictorAi`, `AiMemory`. Conversation history is stored in `AiMemory.messages` (JSON list).

## Key files to read first (examples)
- `victorAiApp/models.py` — custom user model `CustomUser`, `TimeStampField` abstract base, `VictorAi`, `UserChat`, `AiMemory` (look at `log_user_message` / `log_ai_reply`).
- `victorAiApp/serializers.py` — where message handling and rule-based reply generation live (see `AiSerializer.generate_response`, `ConversationSerializer.create`).
- `victorAiApp/ai_prompts.py` — simple PROMPTS dict used for canned replies.
- `victorAiApp/views.py` — minimal views; `RegisterView` exists, `AiView` is incomplete.
- `victorAi/settings.py` — project settings (DB: sqlite3, REST framework + JWT, DEBUG=True). Note `AUTH_USER_MODEL` is set and must match the app's model.

## Project-specific conventions & patterns

- Custom user: `CustomUser` extends `AbstractUser` and `UserManager` is supplied. The code uses username as the `USERNAME_FIELD`.
- Timestamp mixin: `TimeStampField` is an abstract model used by other models to share `created_at`/`updated_at`.
- Memory store: `AiMemory.messages` is a JSON list (default=list). The code appends dicts and expects ISO timestamps.
- Rule-based AI: `ai_prompts.PROMPTS` is a plain dict of keyword-to-reply. Serializers call a response-generator which scans keywords.

## Critical developer workflows (how to run / test quickly)

Typical local sequence (PowerShell, Windows):

1) Create & activate venv

   $ python -m venv .venv; .\.venv\Scripts\Activate.ps1

2) Install deps (project has no requirements.txt; use these minimal packages):

   $ pip install "Django==5.2.5" djangorestframework djangorestframework-simplejwt

3) Run migrations and start server

   $ python manage.py migrate
   $ python manage.py runserver

4) Run tests

   $ python manage.py test

Note: adjust package versions if you add a `requirements.txt` later.

## Concrete examples / expected API shapes

- Register (from `RegisterView` + `UserSerializer`): POST /register with body:
  { "username": "alice", "email": "a@example.com", "password": "secret" }

- Conversation: code stores user messages in `UserChat` and AI replies in `VictorAi`. `AiMemory.messages` contains list items like {"role": "user", "content": "...", "timestamp": "..."}.

## Known issues and gotchas for agents to watch for

These are discovered from reading the code. If you edit files, address these deliberately and add tests.

- settings mismatch: `victorAi/settings.py` currently sets `AUTH_USER_MODEL = 'my_app.CustomUser'`, but the project defines `CustomUser` in `victorAiApp`. Update settings to `'victorAiApp.CustomUser'` before creating users.
- `serializers.UserSerializer.create` contains a bug: `validated_data['username', '']` is invalid indexing; use `validated_data.get('username', '')`.
- `serializers.ConversationSerializer.create` calls `PROMPTS.generate_response(chat)` but `PROMPTS` is a dict. Replace with a function call or reuse `AiSerializer.generate_response`.
- `ConversationSerializer` also creates `VictorAi` without the required `user_chat` foreign key. Ensure `VictorAi` is created with `user_chat=chat`.
- `views.AiView` is incomplete — expect to implement endpoints here. Search for TODOs and failing tests after changes.
- Security: `DEBUG=True` and a checked-in SECRET_KEY — don't push this to production. Treat as a development environment.

## How to extend or change response logic (recommended minimal contract)

- Inputs: a `UserChat` instance (has `.message`) and optionally a `CustomUser`.
- Output: a string reply and a saved `VictorAi` instance linked to the `UserChat`.
- Error modes: missing `user` on request (unauthenticated), empty message, and DB save errors. Propagate DRF validation errors.

Implementation hint: create a small helper (e.g., `victorAiApp/ai.py`) with:

- def generate_response_from_prompts(user_chat: UserChat) -> str

So callers (serializers/views) can import and call a single function instead of reusing dict methods.

## Tests & quality gates

- Add small unit tests for:
  - `AiSerializer.generate_response` behavior against `ai_prompts.PROMPTS` keywords.
  - `ConversationSerializer.create` happy path (creates UserChat, VictorAi, updates AiMemory).
- Smoke test: run `python manage.py migrate` then `python manage.py test`.

## Where to look next when debugging

- Check for stack traces in the console when running server; common failures will be `AUTH_USER_MODEL` mismatches, serializer key errors, or missing fields when creating models.
- Grep for `PROMPTS` and `user_chat` usage to find all places that must be updated consistently.

---

If anything in this file is unclear or you want me to expand an area (example requests/responses, tests, or a small helper module I can add), tell me which part and I'll iterate.
