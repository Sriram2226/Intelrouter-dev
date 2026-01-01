# IntelRouter

Intelligent API Gateway for LLM Routing based on query difficulty and budget constraints.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your credentials:
- Supabase URL and keys
- Hugging Face API key
- Redis connection details
- Admin secret key

3. Set up Supabase tables:
   - Run the SQL script in `database_setup.sql` in your Supabase SQL editor
   - If you have an existing database, use `database_migration.sql` to migrate

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Query
- `POST /api/query` - Process query and get LLM response

### Dashboard (User)
- `GET /api/me` - Get current user info
- `GET /api/usage/today` - Get today's usage
- `GET /api/queries/history` - Get query history
- `GET /api/overrides/remaining` - Get remaining overrides

### Admin
- `GET /api/admin/metrics` - Get system metrics
- `GET /api/admin/costs` - Get cost breakdown
- `GET /api/admin/routing-stats` - Get routing statistics

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

Admin endpoints additionally require `X-Admin-Secret: <secret>` header.

