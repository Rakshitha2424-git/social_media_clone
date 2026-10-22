# Gather frontend

React and Vite frontend for the FastAPI social media API. Deploy it as a Render
Static Site separately from the API.

The app supports account registration and sign-in, a searchable and paginated
feed, post creation and editing, draft publishing, voting, and deleting your
own posts. The signed-in account is shown in the header.

## Local development

In this directory, run:

```powershell
npm install
$env:VITE_API_BASE_URL = "http://localhost:8000"
npm run dev
```

Run the API separately with its local database and required environment settings.

## Render

Create a Static Site connected to this repository:

- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Environment variable `VITE_API_BASE_URL`: the public base URL of the FastAPI service, without a trailing slash

Set `CORS_ORIGINS` on the API web service to the deployed frontend's exact Render
URL (for example, `https://your-frontend.onrender.com`). The API allows Vite's
local development URLs by default.
