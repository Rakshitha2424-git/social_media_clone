# Gather frontend

React and Vite frontend for the FastAPI social media API. Deploy it as a Render
Static Site separately from the API.

The app supports account registration and sign-in, a searchable and paginated
feed, post creation and editing, draft publishing, voting, and deleting your
own posts. The signed-in account is shown in the header.
Posts can include up to five image or video attachments. Local uploads are
stored in the API's `uploads` directory; Docker Compose mounts that directory
so files persist when the API container is recreated. Local disk storage is
not suitable for deployments that replace or run multiple API instances.
Allowed formats are JPG, PNG, GIF, WebP, MP4, MOV, and WebM. Images are limited
to 10 MB each and videos to 100 MB each. Apply the database migration with
`alembic upgrade head` before starting the API.

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
