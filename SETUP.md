# Frontend-Backend Setup Guide

This guide will help you connect and run both the frontend and backend together.

## Prerequisites

- Node.js (v18+) and npm/bun
- Python 3.11+
- Supabase account
- Hugging Face API key
- Redis (optional, for production)

## Backend Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Create a `.env` file in the root directory with:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   HUGGINGFACE_API_KEY=your_hf_api_key
   ADMIN_SECRET_KEY=your_admin_secret
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=
   DAILY_TOKEN_LIMIT=100000
   ```

3. **Set up Supabase database:**
   - Run `database_setup.sql` in your Supabase SQL editor

4. **Start the backend:**
   ```bash
   uvicorn app.main:app --reload
   ```
   Backend will run on `http://localhost:8000`

## Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   bun install
   ```
   
   **Important:** You need to install Supabase client:
   ```bash
   npm install @supabase/supabase-js
   # or
   bun add @supabase/supabase-js
   ```

3. **Configure environment variables:**
   Create a `.env` file in the `frontend` directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   VITE_ADMIN_SECRET=your_admin_secret (optional)
   ```

4. **Start the frontend:**
   ```bash
   npm run dev
   # or
   bun run dev
   ```
   Frontend will run on `http://localhost:8080`

## Connecting Frontend and Backend

### 1. CORS Configuration
The backend CORS is configured to allow requests from `http://localhost:8080`. If you're using a different port, update `app/main.py`:

```python
allow_origins=[
    "http://localhost:8080",  # Your frontend URL
    # Add other origins as needed
],
```

### 2. Authentication Flow

1. **User signs in via Supabase Auth** (Login page)
2. **JWT token is stored** in localStorage by AuthContext
3. **All API calls** include the token in `Authorization: Bearer <token>` header
4. **Backend verifies token** with Supabase and extracts user info

### 3. Admin Access

To access admin endpoints:
1. Set user role to "admin" in Supabase (user metadata: `{"role": "admin"}`)
2. Optionally set `VITE_ADMIN_SECRET` in frontend `.env` or store in localStorage

## Testing the Connection

1. **Start both servers:**
   - Backend: `uvicorn app.main:app --reload`
   - Frontend: `npm run dev` (in frontend directory)

2. **Access the frontend:**
   - Open `http://localhost:8080`
   - You should be redirected to login page

3. **Sign in:**
   - Use Supabase Auth (email/password or OAuth)
   - After login, you'll be redirected to the query interface

4. **Test API calls:**
   - Submit a query on the home page
   - Check usage statistics
   - View query history

## Troubleshooting

### CORS Errors
- Ensure backend CORS includes your frontend URL
- Check that backend is running on port 8000
- Check browser console for specific CORS errors

### Authentication Errors
- Verify Supabase credentials in both `.env` files
- Check that JWT token is being stored in localStorage
- Verify user exists in Supabase and has proper metadata

### API Connection Errors
- Verify `VITE_API_BASE_URL` matches your backend URL
- Check backend logs for errors
- Ensure backend is running and accessible

### Admin Access Issues
- Verify user role is set to "admin" in Supabase user metadata
- Check that admin secret is configured if required

## Development Notes

- Frontend uses React Query for API calls and caching
- Authentication state is managed via AuthContext
- Protected routes require authentication
- Admin routes require both auth and admin role
- API client automatically includes auth tokens in requests




