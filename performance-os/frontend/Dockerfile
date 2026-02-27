# ─── Stage 1: Build ────────────────────────────────────────────────────────────
# Use Node 20 on Alpine to compile the React/Vite application.
# This stage is discarded after the build — it never ends up in the final image.
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies first to leverage Docker layer caching.
# Only re-runs npm install if package.json or package-lock.json changes.
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the source code and build for production.
# The built output lands in /app/dist
COPY . .
RUN npm run build

# ─── Stage 2: Serve ────────────────────────────────────────────────────────────
# Use a minimal Nginx Alpine image — much smaller than Node (only ~22MB).
# This is the ONLY stage that becomes the final Docker image.
FROM nginx:1.25-alpine

# Copy our custom Nginx configuration (enables SPA fallback, gzip, caching)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the compiled React app from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Nginx starts by default — no CMD needed
