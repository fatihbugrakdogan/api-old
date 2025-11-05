# Environment Variables Setup

This document describes all environment variables needed to run this application.

## Quick Start

1. Copy the appropriate example below to create your `.env` file (production) or `.env.local` (development)
2. Fill in the actual values for your environment
3. Never commit `.env` files to version control

## Required Environment Variables

### Project Configuration
- `PROJECT_NAME` - Name of your project

### Security (Optional - auto-generated if not provided)
- `SECRET_KEY` - Secret key for JWT token signing (auto-generated if not set)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiration (default: 10080 = 7 days)
- `REFRESH_TOKEN_EXPIRE_MINUTES` - Refresh token expiration (default: 43200 = 30 days)

### CORS Configuration
- `BACKEND_CORS_ORIGINS` - Comma-separated list of allowed origins (e.g., `http://localhost,https://app.com`)

### Asana Integration
- `ASANA_REDIRECT_URL` - OAuth callback URL for Asana
- `ASANA_CLIENT_ID` - Asana OAuth client ID
- `ASANA_CLIENT_SECRET` - Asana OAuth client secret
- `ASANA_WEBHOOK_URI` - Webhook endpoint for Asana events
- `ASANA_APP_REDIRECT_URL` - Redirect URL after authentication

### Database
- `MONGO_URL` - MongoDB connection string
- `MONGO_DB_NAME` - MongoDB database name

### Temporal.io
- `TEMPORAL_URL` - Temporal server URL (e.g., `http://localhost:7233`)
- `TEMPORAL_ADDRESS` - Temporal server address (e.g., `localhost:7233`)
- `TEMPORAL_API_KEY` - Temporal API key (for Temporal Cloud)
- `TEMPORAL_NAMESPACE` - Temporal namespace (default: `default`)

### Monitoring
- `SENTRY_DSN` - Sentry DSN for error tracking

### Build Dependencies
- `GITHUB_TOKEN` - GitHub Personal Access Token (required for Docker builds to access private bento repository)

---

## .env.local (Local Development)

Create a `.env.local` file with these values. **At minimum, you MUST provide the required fields marked with ⚠️**:

```env
# Project Configuration
PROJECT_NAME=YourProjectName-Dev

# Security
SECRET_KEY=local-dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# CORS Origins (local development)
BACKEND_CORS_ORIGINS=http://localhost,http://localhost:3000,http://localhost:8080

# Asana Integration (use test/dev credentials) ⚠️ REQUIRED
ASANA_REDIRECT_URL=http://localhost/auth/asana/callback
ASANA_CLIENT_ID=your-dev-asana-client-id
ASANA_CLIENT_SECRET=your-dev-asana-client-secret
ASANA_WEBHOOK_URI=http://localhost/webhooks/asana
ASANA_APP_REDIRECT_URL=http://localhost/dashboard

# MongoDB (local) ⚠️ REQUIRED
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=your_database_name_dev

# Temporal.io (local) ⚠️ REQUIRED
TEMPORAL_URL=http://localhost:7233
TEMPORAL_ADDRESS=localhost:7233
TEMPORAL_API_KEY=
TEMPORAL_NAMESPACE=default

# Sentry ⚠️ REQUIRED (can use empty string for dev)
SENTRY_DSN=

# GitHub Token (for private dependencies) ⚠️ REQUIRED for Docker builds
GITHUB_TOKEN=your_github_personal_access_token
```

---

## .env (Production)

Create a `.env` file with:

```env
# Project Configuration
PROJECT_NAME=YourProjectName-Production

# Security (IMPORTANT: Use strong keys in production!)
SECRET_KEY=generate-a-strong-random-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# CORS Origins (production domains)
BACKEND_CORS_ORIGINS=https://yourapp.com,https://www.yourapp.com,https://api.yourapp.com

# Asana Integration (production credentials)
ASANA_REDIRECT_URL=https://api.yourapp.com/auth/asana/callback
ASANA_CLIENT_ID=your-production-asana-client-id
ASANA_CLIENT_SECRET=your-production-asana-client-secret
ASANA_WEBHOOK_URI=https://api.yourapp.com/webhooks/asana
ASANA_APP_REDIRECT_URL=https://yourapp.com/dashboard

# MongoDB (production)
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=your_database_name_prod

# Temporal.io (production - Temporal Cloud)
TEMPORAL_URL=https://your-namespace.tmprl.cloud:7233
TEMPORAL_ADDRESS=your-namespace.tmprl.cloud:7233
TEMPORAL_API_KEY=your-production-temporal-api-key
TEMPORAL_NAMESPACE=your-namespace

# Sentry (production error tracking)
SENTRY_DSN=https://your-production-sentry-dsn@sentry.io/project-id

# GitHub Token (required for Docker builds)
GITHUB_TOKEN=your_github_personal_access_token
```

---

## Docker Build Usage

When building with Docker, pass the GitHub token as a build argument:

### Docker CLI
```bash
docker build --build-arg GITHUB_TOKEN=$GITHUB_TOKEN -t your-app .
```

### Docker Compose
The `docker-compose.yml` is already configured to pass the token:
```bash
export GITHUB_TOKEN=your_token_here
docker-compose build
docker-compose up
```

---

## Generating a SECRET_KEY

If you want to set a custom SECRET_KEY (recommended for production), generate one using Python:

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## Creating a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Docker Build Token")
4. Select scopes: `repo` (for private repository access)
5. Generate and save the token securely
6. Add it to your `.env` file as `GITHUB_TOKEN`

**Security Note:** Never commit this token to version control!

---

## Troubleshooting

### Error: "Field required [type=missing] MONGO_URL"
This means you're missing required environment variables. Make sure your `.env` or `.env.local` file contains ALL required fields marked with ⚠️.

### Error: "OSError: [Errno 22] Invalid argument: '/proc/...'"
This was fixed by changing the Docker `WORKDIR` from `/` to `/code`. Make sure you're using the updated Dockerfile.

### Can't connect to MongoDB
If using Docker, make sure MongoDB is accessible from the container:
- For local MongoDB: use `mongodb://host.docker.internal:27017` instead of `localhost`
- For MongoDB Atlas: use the full connection string

---

## Important Security Notes

1. **Never commit `.env` files to git** - They should be in `.gitignore`
2. **Rotate tokens regularly** - Especially if they may have been exposed
3. **Use different credentials** for development and production
4. **Revoke exposed tokens immediately** - If a token is accidentally committed
5. **Use environment-specific values** - Don't use production credentials in development

