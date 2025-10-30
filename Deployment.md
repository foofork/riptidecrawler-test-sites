# Deployment Architecture Guide - 13 Test Sites

> **Complete implementation guide for deploying 13 EventMesh test sites with automatic URL provisioning**

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Architecture 1: Hetzner VPS + Coolify](#architecture-1-hetzner-vps--coolify)
3. [Architecture 2: Google Cloud Run](#architecture-2-google-cloud-run)
4. [Architecture 3: Koyeb](#architecture-3-koyeb)
5. [Local Development Workflow](#local-development-workflow)
6. [Staging vs Production Strategy](#staging-vs-production-strategy)
7. [Provider Switching Guide](#provider-switching-guide)
8. [Health Monitoring](#health-monitoring)
9. [Decision Matrix](#decision-matrix)

---

## Architecture Overview

### Test Sites Matrix

| Site # | Name | Description | Port |
|--------|------|-------------|------|
| 1 | Astro Basic | Simple Astro SSR | 4321 |
| 2 | Next.js App | Next.js with API routes | 3000 |
| 3 | SvelteKit | Full-stack SvelteKit | 5173 |
| 4 | Remix | Remix with actions | 3001 |
| 5 | Qwik City | Qwik framework | 5174 |
| 6 | Solid Start | SolidJS meta-framework | 3002 |
| 7 | Nuxt | Vue.js meta-framework | 3003 |
| 8 | Fresh | Deno-based framework | 8000 |
| 9 | Analog | Angular meta-framework | 5175 |
| 10 | Gatsby | Static + SSR Gatsby | 9000 |
| 11 | Eleventy Serverless | 11ty with serverless | 8080 |
| 12 | Hydrogen | Shopify Hydrogen | 3004 |
| 13 | RedwoodJS | Full-stack RedwoodJS | 8910 |

### Common Requirements

- **SSL/HTTPS**: Automatic certificate provisioning
- **Automatic deployment**: Git push → Deploy
- **Zero-downtime deployments**: Rolling updates
- **Health checks**: Per-site monitoring
- **Container-based**: Docker/Podman
- **CI/CD integration**: GitHub Actions
- **Environment management**: Secrets, configs
- **Rollback capability**: Quick reversion

---

## Architecture 1: Hetzner VPS + Coolify

### Cost: $4-7/month (most cost-effective)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet (HTTPS/443)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Hetzner VPS (CPX11 or CX21)                     │
│                   1.39.XX.XXX                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Coolify (Self-hosted PaaS)                │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Caddy Reverse Proxy (Auto SSL via Let's Encrypt) │  │
│  │  │           *.1.39.XX.XXX.sslip.io                 │  │
│  │  └─────────┬───────────────────────────────────────┘  │  │
│  │            │                                            │  │
│  │  ┌─────────┴────────────────────────────────────────┐  │  │
│  │  │          Docker Engine + Containers              │  │  │
│  │  │  ┌─────────────────────────────────────────┐    │  │  │
│  │  │  │ astro-1.39.XX.XXX.sslip.io   (Port 4321)│    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ nextjs-2.39.XX.XXX.sslip.io  (Port 3000)│    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ sveltekit-3.39.XX.XXX.sslip.io (5173)   │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ remix-4.39.XX.XXX.sslip.io   (3001)     │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ qwik-5.39.XX.XXX.sslip.io    (5174)     │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ solid-6.39.XX.XXX.sslip.io   (3002)     │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ nuxt-7.39.XX.XXX.sslip.io    (3003)     │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ fresh-8.39.XX.XXX.sslip.io   (8000)     │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ analog-9.39.XX.XXX.sslip.io  (5175)     │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ gatsby-10.39.XX.XXX.sslip.io (9000)     │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ eleventy-11.39.XX.XXX.sslip.io (8080)   │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ hydrogen-12.39.XX.XXX.sslip.io (3004)   │    │  │  │
│  │  │  ├─────────────────────────────────────────┤    │  │  │
│  │  │  │ redwood-13.39.XX.XXX.sslip.io (8910)    │    │  │  │
│  │  │  └─────────────────────────────────────────┘    │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │     PostgreSQL (Coolify metadata)               │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Data Flow:
1. User → https://astro-1.39.XX.XXX.sslip.io
2. DNS → sslip.io resolves to 1.39.XX.XXX
3. Caddy → Terminates SSL, routes to container port 4321
4. Container → Serves Astro app
5. Response → Back through Caddy with HTTPS
```

### How It Works

#### 1. **Container Deployment**

Coolify manages Docker containers with:
- **One container per site** (13 containers total)
- **Automatic builds** from Git repos
- **Health checks** with auto-restart
- **Resource limits** per container

#### 2. **Subdomain Strategy (sslip.io)**

Using sslip.io for wildcard DNS:
```
astro-1.39.185.42.sslip.io    → Resolves to 1.39.185.42
nextjs-2.39.185.42.sslip.io   → Resolves to 1.39.185.42
[name]-[ip-with-dots].sslip.io → Resolves to IP
```

**Why sslip.io?**
- No DNS configuration needed
- Free wildcard DNS
- Works with any IP
- Alternative: nip.io (same concept)

#### 3. **Reverse Proxy (Caddy)**

Caddy configuration (auto-generated by Coolify):
```
astro-1.39.185.42.sslip.io {
    reverse_proxy localhost:4321
    tls {
        on_demand
    }
}

nextjs-2.39.185.42.sslip.io {
    reverse_proxy localhost:3000
    tls {
        on_demand
    }
}
# ... repeat for all 13 sites
```

**Features:**
- **Automatic HTTPS**: Let's Encrypt integration
- **HTTP/2 & HTTP/3**: Modern protocols
- **Auto-renewal**: Certificates renewed automatically
- **Zero-config SSL**: No manual certificate management

#### 4. **Deployment Workflow**

```
Developer → git push → GitHub → Webhook → Coolify → Build & Deploy
                                              ↓
                                        Docker Build
                                              ↓
                                        Health Check
                                              ↓
                                        Rolling Update
                                              ↓
                                        Live on HTTPS
```

### Step-by-Step Deployment Guide

#### Phase 1: VPS Setup (15 minutes)

```bash
# 1. Create Hetzner VPS
# Go to: https://console.hetzner.cloud
# - Select CX21 (2 vCPU, 4GB RAM) - €4.90/month
# - Choose Ubuntu 22.04
# - Add SSH key
# - Note the IP address (e.g., 1.39.185.42)

# 2. SSH into VPS
ssh root@1.39.185.42

# 3. Update system
apt update && apt upgrade -y

# 4. Install Docker
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 5. Install Coolify (one command!)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# 6. Access Coolify
# Open browser: http://1.39.185.42:8000
# Create admin account
# Coolify will auto-configure SSL for itself
```

#### Phase 2: Coolify Configuration (20 minutes)

```bash
# Via Coolify Web UI:

# 1. Add Git Source
Settings → Sources → Add Source
- GitHub (authenticate with OAuth)
- Or GitLab/Gitea

# 2. Create Project
Projects → New Project → "EventMesh Test Sites"

# 3. Add Environment
Environments → New Environment → "Production"

# 4. Configure Domain Template
Settings → Domain Template
Base Domain: {APP_NAME}-{SERVER_IP}.sslip.io
```

#### Phase 3: Deploy All 13 Sites (10 minutes)

For each site, use Coolify UI:

```bash
# Example for Site 1 (Astro)
1. Applications → New Application → Docker Compose

2. Configuration:
   Name: astro-basic
   Git Repository: https://github.com/yourusername/eventmesh
   Branch: main
   Build Pack: Dockerfile
   Dockerfile Path: ./sites/01-astro-basic/Dockerfile

3. Domain:
   Auto-generated: astro-1.39.185.42.sslip.io

4. Environment Variables:
   PORT=4321
   NODE_ENV=production

5. Deploy Settings:
   Auto Deploy: ✅ (on git push)
   Health Check Path: /

6. Click "Deploy"

# Repeat for sites 2-13 with respective configs
```

#### Phase 4: Automated Deployment Script

```bash
# Create deployment script for all sites
cat > /root/deploy-all-sites.sh << 'EOF'
#!/bin/bash

VPS_IP="1.39.185.42"
COOLIFY_API_TOKEN="your-api-token-here"
COOLIFY_URL="http://localhost:8000"

# Site configurations
declare -A SITES=(
    ["astro-basic"]="4321:./sites/01-astro-basic"
    ["nextjs-app"]="3000:./sites/02-nextjs-app"
    ["sveltekit"]="5173:./sites/03-sveltekit"
    ["remix"]="3001:./sites/04-remix"
    ["qwik-city"]="5174:./sites/05-qwik-city"
    ["solid-start"]="3002:./sites/06-solid-start"
    ["nuxt"]="3003:./sites/07-nuxt"
    ["fresh"]="8000:./sites/08-fresh"
    ["analog"]="5175:./sites/09-analog"
    ["gatsby"]="9000:./sites/10-gatsby"
    ["eleventy"]="8080:./sites/11-eleventy-serverless"
    ["hydrogen"]="3004:./sites/12-hydrogen"
    ["redwood"]="8910:./sites/13-redwood"
)

for SITE_NAME in "${!SITES[@]}"; do
    IFS=':' read -r PORT PATH <<< "${SITES[$SITE_NAME]}"

    echo "Deploying $SITE_NAME..."

    curl -X POST "$COOLIFY_URL/api/v1/deploy" \
        -H "Authorization: Bearer $COOLIFY_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"name\": \"$SITE_NAME\",
            \"repository\": \"https://github.com/yourusername/eventmesh\",
            \"branch\": \"main\",
            \"dockerfile_path\": \"$PATH/Dockerfile\",
            \"port\": $PORT,
            \"domain\": \"$SITE_NAME-$VPS_IP.sslip.io\",
            \"auto_deploy\": true
        }"

    sleep 5
done

echo "All sites deployed!"
EOF

chmod +x /root/deploy-all-sites.sh
./deploy-all-sites.sh
```

### Example URLs for All 13 Sites

```
1.  https://astro-1.39.185.42.sslip.io
2.  https://nextjs-2.39.185.42.sslip.io
3.  https://sveltekit-3.39.185.42.sslip.io
4.  https://remix-4.39.185.42.sslip.io
5.  https://qwik-5.39.185.42.sslip.io
6.  https://solid-6.39.185.42.sslip.io
7.  https://nuxt-7.39.185.42.sslip.io
8.  https://fresh-8.39.185.42.sslip.io
9.  https://analog-9.39.185.42.sslip.io
10. https://gatsby-10.39.185.42.sslip.io
11. https://eleventy-11.39.185.42.sslip.io
12. https://hydrogen-12.39.185.42.sslip.io
13. https://redwood-13.39.185.42.sslip.io
```

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-hetzner.yml
name: Deploy to Hetzner + Coolify

on:
  push:
    branches: [main]
    paths:
      - 'sites/**'
      - '.github/workflows/deploy-hetzner.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        site:
          - name: astro-basic
            path: sites/01-astro-basic
            port: 4321
          - name: nextjs-app
            path: sites/02-nextjs-app
            port: 3000
          - name: sveltekit
            path: sites/03-sveltekit
            port: 5173
          - name: remix
            path: sites/04-remix
            port: 3001
          - name: qwik-city
            path: sites/05-qwik-city
            port: 5174
          - name: solid-start
            path: sites/06-solid-start
            port: 3002
          - name: nuxt
            path: sites/07-nuxt
            port: 3003
          - name: fresh
            path: sites/08-fresh
            port: 8000
          - name: analog
            path: sites/09-analog
            port: 5175
          - name: gatsby
            path: sites/10-gatsby
            port: 9000
          - name: eleventy
            path: sites/11-eleventy-serverless
            port: 8080
          - name: hydrogen
            path: sites/12-hydrogen
            port: 3004
          - name: redwood
            path: sites/13-redwood
            port: 8910

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Check if site changed
        id: changed
        uses: dorny/paths-filter@v2
        with:
          filters: |
            site:
              - '${{ matrix.site.path }}/**'

      - name: Trigger Coolify deployment
        if: steps.changed.outputs.site == 'true'
        run: |
          curl -X POST "${{ secrets.COOLIFY_URL }}/api/v1/deploy" \
            -H "Authorization: Bearer ${{ secrets.COOLIFY_API_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "name": "${{ matrix.site.name }}",
              "force": true
            }'

      - name: Wait for deployment
        if: steps.changed.outputs.site == 'true'
        run: |
          sleep 30
          SITE_URL="https://${{ matrix.site.name }}-${{ secrets.VPS_IP }}.sslip.io"

          for i in {1..10}; do
            if curl -sSf "$SITE_URL" > /dev/null; then
              echo "✅ Site deployed successfully!"
              exit 0
            fi
            echo "Waiting for site to be ready... ($i/10)"
            sleep 10
          done

          echo "❌ Deployment health check failed"
          exit 1

      - name: Notify deployment status
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Deployment of ${{ matrix.site.name }} ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Pros & Cons

#### ✅ Pros
1. **Most cost-effective**: $4-7/month for ALL 13 sites
2. **Full control**: Root access, no vendor lock-in
3. **Simple scaling**: Upgrade VPS as needed
4. **Automatic SSL**: Let's Encrypt via Caddy
5. **Git integration**: Auto-deploy on push
6. **One-click rollback**: Coolify UI feature
7. **Resource monitoring**: Built-in dashboards
8. **No cold starts**: Always warm
9. **Custom domains**: Easy to add later
10. **Backup support**: Database + volumes

#### ❌ Cons
1. **Manual VPS setup**: Initial 15-minute setup
2. **Single point of failure**: One VPS down = all sites down
3. **Resource limits**: Shared 4GB RAM / 2 vCPU
4. **Manual scaling**: Need to upgrade VPS manually
5. **Self-managed**: You handle updates, security patches
6. **No auto-scaling**: Fixed capacity
7. **Limited global edge**: Single datacenter location

### Setup Time Estimate

- **Initial setup**: 45 minutes (one-time)
  - VPS creation: 5 minutes
  - Coolify installation: 15 minutes
  - First site deployment: 10 minutes
  - Remaining 12 sites: 15 minutes
- **Subsequent deployments**: 1 minute per site (automatic)
- **Maintenance**: 1 hour/month (updates, monitoring)

### Ongoing Maintenance Burden

**Weekly (10 minutes)**
- Monitor resource usage in Coolify dashboard
- Check deployment logs for errors
- Review SSL certificate renewals

**Monthly (1 hour)**
- Update Coolify: `coolifyctl update`
- Update Docker: `apt update && apt upgrade docker-ce`
- Review and clean old Docker images: `docker system prune -a`
- Backup Coolify database

**Quarterly (2 hours)**
- Security updates: `apt update && apt upgrade`
- Review and optimize container resources
- Test disaster recovery process

### Scaling Strategy

**Vertical Scaling (Easiest)**
```bash
# Upgrade VPS in Hetzner Cloud Console
# CX21 (4GB) → CX31 (8GB) → CX41 (16GB)
# No downtime if done properly
```

**Horizontal Scaling (Advanced)**
```bash
# Add second VPS for high-traffic sites
# Use Coolify's built-in load balancer
# Or migrate specific sites to dedicated VPS
```

---

## Architecture 2: Google Cloud Run

### Cost: $0-8/month (likely free tier)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Internet (HTTPS/443)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Google Cloud Load Balancer                      │
│                (Auto SSL Certificate)                         │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴──────────┬──────────────┬───────────────┐
    │                   │               │               │
    ▼                   ▼               ▼               ▼
┌────────┐      ┌────────┐      ┌────────┐      ┌────────┐
│ Cloud  │ .... │ Cloud  │      │ Cloud  │      │ Cloud  │
│ Run    │      │ Run    │      │ Run    │      │ Run    │
│ Service│      │ Service│      │ Service│      │ Service│
│ 1      │      │ 2      │      │ 3      │      │ 13     │
└────────┘      └────────┘      └────────┘      └────────┘
    │                │               │               │
    ▼                ▼               ▼               ▼
┌────────────────────────────────────────────────────────────┐
│            Artifact Registry (Container Images)             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  gcr.io/PROJECT/astro-basic:latest                   │  │
│  │  gcr.io/PROJECT/nextjs-app:latest                    │  │
│  │  gcr.io/PROJECT/sveltekit:latest                     │  │
│  │  ... (13 images total)                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘

Auto-scaling:
- 0 instances when no traffic (free!)
- Scale to N instances under load
- Cold start: 1-3 seconds
- Automatic HTTPS
- Global CDN

URLs:
- astro-basic-ABC123-uc.a.run.app
- nextjs-app-ABC123-uc.a.run.app
- sveltekit-ABC123-uc.a.run.app
- ... (13 services)
```

### How It Works

#### 1. **13 Separate Cloud Run Services**

Each test site = One Cloud Run service:
```
eventmesh-astro-basic      → Container from gcr.io/PROJECT/astro-basic
eventmesh-nextjs-app       → Container from gcr.io/PROJECT/nextjs-app
eventmesh-sveltekit        → Container from gcr.io/PROJECT/sveltekit
... (13 total)
```

**Service Configuration:**
```yaml
# Each service config
CPU: 1 vCPU (free tier: 2 million requests/month)
Memory: 512 MiB (can increase if needed)
Min instances: 0 (scale to zero = free when idle)
Max instances: 10 (auto-scale under load)
Timeout: 60 seconds
Concurrency: 80 requests per instance
```

#### 2. **URL Structure (*.run.app)**

Google Cloud Run auto-generates URLs:
```
https://astro-basic-a1b2c3d4e5-uc.a.run.app
https://nextjs-app-a1b2c3d4e5-uc.a.run.app
https://sveltekit-a1b2c3d4e5-uc.a.run.app

Format: https://[SERVICE-NAME]-[HASH]-[REGION].a.run.app

Where:
- SERVICE-NAME: Your chosen name (e.g., astro-basic)
- HASH: Auto-generated unique ID
- REGION: uc (us-central), ew (europe-west), etc.
```

**Custom Domains (Optional):**
```bash
# Map custom domain to any service
gcloud run domain-mappings create \
  --service=astro-basic \
  --domain=astro.example.com \
  --region=us-central1
```

#### 3. **Container Registry Approach**

Using Artifact Registry (newer than GCR):
```bash
# Enable Artifact Registry
gcloud artifacts repositories create eventmesh \
  --repository-format=docker \
  --location=us-central1

# Registry URL
us-central1-docker.pkg.dev/PROJECT-ID/eventmesh/[IMAGE]
```

#### 4. **Deployment Automation**

```
GitHub → Push → Actions → Build Container → Push to Artifact Registry → Deploy to Cloud Run
   ↓                            ↓                      ↓                        ↓
  main                    Docker build            gcloud push             gcloud run deploy
                               ↓                       ↓                        ↓
                          Tag: git-sha           Authenticate           Update service
                                                                              ↓
                                                                        Health check
                                                                              ↓
                                                                        Live traffic
```

### Step-by-Step Deployment Guide

#### Phase 1: Google Cloud Setup (10 minutes)

```bash
# 1. Create Google Cloud account
# Go to: https://console.cloud.google.com
# - Sign in with Google account
# - Accept free trial ($300 credit)

# 2. Create project
gcloud projects create eventmesh-test --name="EventMesh Test Sites"
gcloud config set project eventmesh-test

# 3. Enable APIs
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com

# 4. Create Artifact Registry repository
gcloud artifacts repositories create eventmesh \
  --repository-format=docker \
  --location=us-central1 \
  --description="EventMesh test site containers"

# 5. Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev

# 6. Set default region
gcloud config set run/region us-central1
```

#### Phase 2: Build and Push Containers (20 minutes)

```bash
# Build script for all sites
cat > build-all-containers.sh << 'EOF'
#!/bin/bash

PROJECT_ID="eventmesh-test"
REGION="us-central1"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/eventmesh"

# Site configurations
declare -A SITES=(
    ["astro-basic"]="sites/01-astro-basic"
    ["nextjs-app"]="sites/02-nextjs-app"
    ["sveltekit"]="sites/03-sveltekit"
    ["remix"]="sites/04-remix"
    ["qwik-city"]="sites/05-qwik-city"
    ["solid-start"]="sites/06-solid-start"
    ["nuxt"]="sites/07-nuxt"
    ["fresh"]="sites/08-fresh"
    ["analog"]="sites/09-analog"
    ["gatsby"]="sites/10-gatsby"
    ["eleventy"]="sites/11-eleventy-serverless"
    ["hydrogen"]="sites/12-hydrogen"
    ["redwood"]="sites/13-redwood"
)

for SITE_NAME in "${!SITES[@]}"; do
    SITE_PATH="${SITES[$SITE_NAME]}"
    IMAGE_NAME="${REGISTRY}/${SITE_NAME}:latest"

    echo "Building $SITE_NAME..."

    # Build container
    docker build -t "$IMAGE_NAME" "$SITE_PATH"

    # Push to Artifact Registry
    docker push "$IMAGE_NAME"

    echo "✅ $SITE_NAME built and pushed"
done

echo "All containers built and pushed!"
EOF

chmod +x build-all-containers.sh
./build-all-containers.sh
```

#### Phase 3: Deploy to Cloud Run (15 minutes)

```bash
# Deploy script for all sites
cat > deploy-all-cloudrun.sh << 'EOF'
#!/bin/bash

PROJECT_ID="eventmesh-test"
REGION="us-central1"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/eventmesh"

# Site configurations with ports
declare -A SITES=(
    ["astro-basic"]="4321"
    ["nextjs-app"]="3000"
    ["sveltekit"]="5173"
    ["remix"]="3001"
    ["qwik-city"]="5174"
    ["solid-start"]="3002"
    ["nuxt"]="3003"
    ["fresh"]="8000"
    ["analog"]="5175"
    ["gatsby"]="9000"
    ["eleventy"]="8080"
    ["hydrogen"]="3004"
    ["redwood"]="8910"
)

for SITE_NAME in "${!SITES[@]}"; do
    PORT="${SITES[$SITE_NAME]}"
    IMAGE="${REGISTRY}/${SITE_NAME}:latest"

    echo "Deploying $SITE_NAME to Cloud Run..."

    gcloud run deploy "eventmesh-${SITE_NAME}" \
      --image="$IMAGE" \
      --platform=managed \
      --region="$REGION" \
      --allow-unauthenticated \
      --port="$PORT" \
      --memory=512Mi \
      --cpu=1 \
      --min-instances=0 \
      --max-instances=10 \
      --timeout=60s \
      --concurrency=80 \
      --set-env-vars="PORT=$PORT,NODE_ENV=production"

    # Get service URL
    SERVICE_URL=$(gcloud run services describe "eventmesh-${SITE_NAME}" \
      --region="$REGION" \
      --format="value(status.url)")

    echo "✅ $SITE_NAME deployed: $SERVICE_URL"
done

echo "All sites deployed!"
EOF

chmod +x deploy-all-cloudrun.sh
./deploy-all-cloudrun.sh
```

#### Phase 4: Get All Service URLs

```bash
# List all deployed services with URLs
gcloud run services list --format="table(SERVICE,URL)" --region=us-central1
```

### Example URLs for All 13 Sites

```
https://eventmesh-astro-basic-a1b2c3d4e5-uc.a.run.app
https://eventmesh-nextjs-app-f6g7h8i9j0-uc.a.run.app
https://eventmesh-sveltekit-k1l2m3n4o5-uc.a.run.app
https://eventmesh-remix-p6q7r8s9t0-uc.a.run.app
https://eventmesh-qwik-city-u1v2w3x4y5-uc.a.run.app
https://eventmesh-solid-start-z6a7b8c9d0-uc.a.run.app
https://eventmesh-nuxt-e1f2g3h4i5-uc.a.run.app
https://eventmesh-fresh-j6k7l8m9n0-uc.a.run.app
https://eventmesh-analog-o1p2q3r4s5-uc.a.run.app
https://eventmesh-gatsby-t6u7v8w9x0-uc.a.run.app
https://eventmesh-eleventy-y1z2a3b4c5-uc.a.run.app
https://eventmesh-hydrogen-d6e7f8g9h0-uc.a.run.app
https://eventmesh-redwood-i1j2k3l4m5-uc.a.run.app
```

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-cloudrun.yml
name: Deploy to Google Cloud Run

on:
  push:
    branches: [main]
    paths:
      - 'sites/**'
      - '.github/workflows/deploy-cloudrun.yml'

env:
  PROJECT_ID: eventmesh-test
  REGION: us-central1
  REGISTRY: us-central1-docker.pkg.dev

jobs:
  deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        site:
          - name: astro-basic
            path: sites/01-astro-basic
            port: 4321
          - name: nextjs-app
            path: sites/02-nextjs-app
            port: 3000
          - name: sveltekit
            path: sites/03-sveltekit
            port: 5173
          - name: remix
            path: sites/04-remix
            port: 3001
          - name: qwik-city
            path: sites/05-qwik-city
            port: 5174
          - name: solid-start
            path: sites/06-solid-start
            port: 3002
          - name: nuxt
            path: sites/07-nuxt
            port: 3003
          - name: fresh
            path: sites/08-fresh
            port: 8000
          - name: analog
            path: sites/09-analog
            port: 5175
          - name: gatsby
            path: sites/10-gatsby
            port: 9000
          - name: eleventy
            path: sites/11-eleventy-serverless
            port: 8080
          - name: hydrogen
            path: sites/12-hydrogen
            port: 3004
          - name: redwood
            path: sites/13-redwood
            port: 8910

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Check if site changed
        id: changed
        uses: dorny/paths-filter@v2
        with:
          filters: |
            site:
              - '${{ matrix.site.path }}/**'

      - name: Authenticate to Google Cloud
        if: steps.changed.outputs.site == 'true'
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_CREDENTIALS }}

      - name: Set up Cloud SDK
        if: steps.changed.outputs.site == 'true'
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        if: steps.changed.outputs.site == 'true'
        run: |
          gcloud auth configure-docker ${{ env.REGISTRY }}

      - name: Build container image
        if: steps.changed.outputs.site == 'true'
        run: |
          IMAGE_NAME="${{ env.REGISTRY }}/${{ env.PROJECT_ID }}/eventmesh/${{ matrix.site.name }}:${{ github.sha }}"
          IMAGE_LATEST="${{ env.REGISTRY }}/${{ env.PROJECT_ID }}/eventmesh/${{ matrix.site.name }}:latest"

          docker build \
            -t "$IMAGE_NAME" \
            -t "$IMAGE_LATEST" \
            ${{ matrix.site.path }}

          docker push "$IMAGE_NAME"
          docker push "$IMAGE_LATEST"

      - name: Deploy to Cloud Run
        if: steps.changed.outputs.site == 'true'
        run: |
          gcloud run deploy "eventmesh-${{ matrix.site.name }}" \
            --image="${{ env.REGISTRY }}/${{ env.PROJECT_ID }}/eventmesh/${{ matrix.site.name }}:${{ github.sha }}" \
            --platform=managed \
            --region="${{ env.REGION }}" \
            --allow-unauthenticated \
            --port="${{ matrix.site.port }}" \
            --memory=512Mi \
            --cpu=1 \
            --min-instances=0 \
            --max-instances=10 \
            --timeout=60s \
            --concurrency=80 \
            --set-env-vars="PORT=${{ matrix.site.port }},NODE_ENV=production,GIT_SHA=${{ github.sha }}" \
            --quiet

      - name: Get service URL
        if: steps.changed.outputs.site == 'true'
        id: url
        run: |
          SERVICE_URL=$(gcloud run services describe "eventmesh-${{ matrix.site.name }}" \
            --region="${{ env.REGION }}" \
            --format="value(status.url)")
          echo "url=$SERVICE_URL" >> $GITHUB_OUTPUT

      - name: Test deployment
        if: steps.changed.outputs.site == 'true'
        run: |
          for i in {1..5}; do
            if curl -sSf "${{ steps.url.outputs.url }}" > /dev/null; then
              echo "✅ Deployment successful!"
              exit 0
            fi
            echo "Waiting for service to be ready... ($i/5)"
            sleep 10
          done
          echo "❌ Deployment health check failed"
          exit 1

      - name: Output deployment info
        if: steps.changed.outputs.site == 'true'
        run: |
          echo "### Deployment Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Site:** ${{ matrix.site.name }}" >> $GITHUB_STEP_SUMMARY
          echo "**URL:** ${{ steps.url.outputs.url }}" >> $GITHUB_STEP_SUMMARY
          echo "**Image:** ${{ env.REGISTRY }}/${{ env.PROJECT_ID }}/eventmesh/${{ matrix.site.name }}:${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
```

### Pros & Cons

#### ✅ Pros
1. **Free tier**: Likely $0/month (2M requests free)
2. **Zero maintenance**: Fully managed, no servers
3. **Auto-scaling**: 0 to N instances automatically
4. **Global edge**: Multi-region deployment
5. **Automatic HTTPS**: Managed SSL certificates
6. **High availability**: 99.95% SLA
7. **Git integration**: Deploy from GitHub Actions
8. **Instant rollback**: One command revert
9. **No cold storage**: Scale to zero = no cost
10. **Built-in monitoring**: Stackdriver integration

#### ❌ Cons
1. **Cold starts**: 1-3 second delay when scaling from zero
2. **Vendor lock-in**: Google Cloud specific
3. **Complex URLs**: Long *.run.app domains (custom domains cost extra)
4. **Request limits**: 60-second timeout, 32 MB response
5. **No SSH access**: Container-only, no shell
6. **Pricing complexity**: Can exceed free tier unexpectedly
7. **Limited regions**: Not available everywhere
8. **Stateless only**: No persistent storage (need Cloud Storage)

### Setup Time Estimate

- **Initial setup**: 30 minutes (one-time)
  - Google Cloud account: 5 minutes
  - Project setup: 10 minutes
  - Build all containers: 10 minutes
  - Deploy all services: 5 minutes
- **Subsequent deployments**: Automatic (30 seconds per site via GitHub Actions)
- **Maintenance**: 10 minutes/month (review logs, costs)

### Ongoing Maintenance Burden

**Weekly (5 minutes)**
- Check Cloud Run logs for errors
- Review request metrics in console

**Monthly (10 minutes)**
- Review billing (ensure free tier)
- Check cold start metrics
- Update base container images

**Quarterly (30 minutes)**
- Review security updates
- Optimize container sizes
- Test disaster recovery

### Cost Optimization Tips

```bash
# 1. Stay in free tier
# - 2 million requests/month FREE
# - 360,000 GB-seconds/month FREE
# - 180,000 vCPU-seconds/month FREE

# 2. Use smallest viable containers
FROM node:20-alpine  # Use alpine, not full node image
RUN npm ci --production  # Production deps only

# 3. Enable scale-to-zero
--min-instances=0  # Free when idle

# 4. Optimize concurrency
--concurrency=80  # Handle more requests per instance

# 5. Set reasonable timeouts
--timeout=60s  # Don't pay for stuck requests

# 6. Use request-based pricing
# Free tier = 2M requests = ~650 req/day per site = plenty for tests

# 7. Monitor costs
gcloud billing accounts list
gcloud billing budgets list

# 8. Set budget alerts
gcloud billing budgets create \
  --billing-account=ABC-123 \
  --display-name="EventMesh Budget" \
  --budget-amount=10USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90
```

---

## Architecture 3: Koyeb

### Cost: $20/month (flat rate for unlimited apps)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  Internet (HTTPS/443)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Koyeb Global Edge Network                       │
│          (Automatic SSL + DDoS Protection)                   │
└────────┬────────┬────────┬────────┬────────┬────────────────┘
         │        │        │        │        │
    ┌────┴───┐ ┌─┴────┐ ┌─┴────┐ ┌─┴────┐ ┌─┴────┐
    │ US East│ │US West│ │Europe│ │ Asia │ │Global│
    └────┬───┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
         │        │        │        │        │
         └────────┴────────┴────────┴────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Koyeb Control Plane                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              13 Koyeb Apps (Services)                 │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │ astro-basic.koyeb.app         (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ nextjs-app.koyeb.app          (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ sveltekit.koyeb.app           (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ remix.koyeb.app               (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ qwik-city.koyeb.app           (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ solid-start.koyeb.app         (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ nuxt.koyeb.app                (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ fresh.koyeb.app               (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ analog.koyeb.app              (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ gatsby.koyeb.app              (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ eleventy.koyeb.app            (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ hydrogen.koyeb.app            (Auto HTTPS)      │  │  │
│  │  ├─────────────────────────────────────────────────┤  │  │
│  │  │ redwood.koyeb.app             (Auto HTTPS)      │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │        Container Registry Integration                 │  │
│  │  - Docker Hub (public/private)                       │  │
│  │  - GitHub Container Registry                         │  │
│  │  - GitLab Container Registry                         │  │
│  │  - Private registries                                │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Features:
- Global CDN (150+ PoPs)
- Auto-scaling (0-N instances)
- Zero-downtime deploys
- Built-in observability
- Git integration
- Environment variables per app
```

### How It Works

#### 1. **Multi-App Deployment Strategy**

Each test site = One Koyeb App (Service):
```
Koyeb App 1:  astro-basic      → Deploy from Docker/Git
Koyeb App 2:  nextjs-app       → Deploy from Docker/Git
Koyeb App 3:  sveltekit        → Deploy from Docker/Git
... (13 total apps)
```

**App Configuration:**
```yaml
# Each app spec
Instance Type: nano (512 MB RAM, 0.1 vCPU)
Regions: fra (Frankfurt) or was (Washington DC)
Scaling: Auto (min: 1, max: 3)
Health Checks: HTTP on /
Deployment: Rolling update
```

#### 2. **Subdomain Structure (*.koyeb.app)**

Koyeb auto-generates subdomains:
```
https://astro-basic-yourorg.koyeb.app
https://nextjs-app-yourorg.koyeb.app
https://sveltekit-yourorg.koyeb.app

Format: https://[APP-NAME]-[ORG-NAME].koyeb.app

Where:
- APP-NAME: Your chosen app name
- ORG-NAME: Your Koyeb organization slug
- koyeb.app: Koyeb's domain (free SSL)
```

**Custom Domains:**
```bash
# Add custom domain via CLI
koyeb domain create astro.example.com \
  --app astro-basic \
  --type CNAME
```

#### 3. **Docker Registry Integration**

Koyeb supports multiple registries:

**Option A: Docker Hub**
```bash
# Public image
koyeb app create astro-basic \
  --docker docker.io/username/astro-basic:latest

# Private image
koyeb secret create dockerhub-creds \
  --docker-hub-username=user \
  --docker-hub-password=pass
```

**Option B: GitHub Container Registry**
```bash
# Using GHCR
koyeb app create nextjs-app \
  --docker ghcr.io/username/nextjs-app:latest \
  --registry-secret ghcr-token
```

**Option C: Git-based deployment**
```bash
# Deploy directly from Git (Koyeb builds container)
koyeb app create sveltekit \
  --git github.com/username/eventmesh \
  --git-branch main \
  --git-workdir sites/03-sveltekit \
  --git-buildpack dockerfile
```

#### 4. **Deployment Workflow**

```
Developer → git push → GitHub → Webhook → Koyeb → Build/Pull → Deploy
                                              ↓
                                        Health Check
                                              ↓
                                        Rolling Update
                                              ↓
                                        Live on HTTPS
                                              ↓
                                        Global CDN
```

### Step-by-Step Deployment Guide

#### Phase 1: Koyeb Account Setup (5 minutes)

```bash
# 1. Create Koyeb account
# Go to: https://app.koyeb.com/auth/signup
# - Sign up with GitHub (easiest)
# - Or email + password

# 2. Install Koyeb CLI
curl -fsSL https://cli.koyeb.com/install.sh | sh

# 3. Authenticate CLI
koyeb login

# 4. Create organization (if needed)
# Done via web UI: https://app.koyeb.com/organization

# 5. Verify authentication
koyeb organization list
```

#### Phase 2: Prepare Docker Images (Option A)

```bash
# If using Docker Hub registry

# 1. Login to Docker Hub
docker login

# 2. Build and push all images
cat > koyeb-build-push.sh << 'EOF'
#!/bin/bash

DOCKER_USERNAME="your-dockerhub-username"

# Site configurations
declare -A SITES=(
    ["astro-basic"]="sites/01-astro-basic"
    ["nextjs-app"]="sites/02-nextjs-app"
    ["sveltekit"]="sites/03-sveltekit"
    ["remix"]="sites/04-remix"
    ["qwik-city"]="sites/05-qwik-city"
    ["solid-start"]="sites/06-solid-start"
    ["nuxt"]="sites/07-nuxt"
    ["fresh"]="sites/08-fresh"
    ["analog"]="sites/09-analog"
    ["gatsby"]="sites/10-gatsby"
    ["eleventy"]="sites/11-eleventy-serverless"
    ["hydrogen"]="sites/12-hydrogen"
    ["redwood"]="sites/13-redwood"
)

for SITE_NAME in "${!SITES[@]}"; do
    SITE_PATH="${SITES[$SITE_NAME]}"
    IMAGE="$DOCKER_USERNAME/eventmesh-$SITE_NAME:latest"

    echo "Building $SITE_NAME..."
    docker build -t "$IMAGE" "$SITE_PATH"

    echo "Pushing $SITE_NAME..."
    docker push "$IMAGE"

    echo "✅ $SITE_NAME ready for Koyeb"
done
EOF

chmod +x koyeb-build-push.sh
./koyeb-build-push.sh
```

#### Phase 3: Deploy All Apps to Koyeb (15 minutes)

```bash
# Deploy all 13 apps via Koyeb CLI
cat > koyeb-deploy-all.sh << 'EOF'
#!/bin/bash

DOCKER_USERNAME="your-dockerhub-username"

# Site configurations with ports
declare -A SITES=(
    ["astro-basic"]="4321"
    ["nextjs-app"]="3000"
    ["sveltekit"]="5173"
    ["remix"]="3001"
    ["qwik-city"]="5174"
    ["solid-start"]="3002"
    ["nuxt"]="3003"
    ["fresh"]="8000"
    ["analog"]="5175"
    ["gatsby"]="9000"
    ["eleventy"]="8080"
    ["hydrogen"]="3004"
    ["redwood"]="8910"
)

for SITE_NAME in "${!SITES[@]}"; do
    PORT="${SITES[$SITE_NAME]}"
    IMAGE="$DOCKER_USERNAME/eventmesh-$SITE_NAME:latest"

    echo "Deploying $SITE_NAME to Koyeb..."

    koyeb app create "eventmesh-$SITE_NAME" \
      --docker "$IMAGE" \
      --ports "$PORT:http" \
      --routes "/:$PORT" \
      --regions fra \
      --instance-type nano \
      --min-scale 1 \
      --max-scale 3 \
      --env PORT="$PORT" \
      --env NODE_ENV=production \
      --health-checks "/:http:$PORT" \
      --auto-deploy

    echo "✅ $SITE_NAME deployed"
    sleep 5
done

echo "All apps deployed! Getting URLs..."
koyeb app list
EOF

chmod +x koyeb-deploy-all.sh
./koyeb-deploy-all.sh
```

#### Phase 4: Git-Based Deployment (Option B - Recommended)

```bash
# Deploy directly from Git (no Docker registry needed)
cat > koyeb-deploy-git.sh << 'EOF'
#!/bin/bash

GITHUB_REPO="github.com/yourusername/eventmesh"

# Site configurations
declare -A SITES=(
    ["astro-basic"]="4321:sites/01-astro-basic"
    ["nextjs-app"]="3000:sites/02-nextjs-app"
    ["sveltekit"]="5173:sites/03-sveltekit"
    ["remix"]="3001:sites/04-remix"
    ["qwik-city"]="5174:sites/05-qwik-city"
    ["solid-start"]="3002:sites/06-solid-start"
    ["nuxt"]="3003:sites/07-nuxt"
    ["fresh"]="8000:sites/08-fresh"
    ["analog"]="5175:sites/09-analog"
    ["gatsby"]="9000:sites/10-gatsby"
    ["eleventy"]="8080:sites/11-eleventy-serverless"
    ["hydrogen"]="3004:sites/12-hydrogen"
    ["redwood"]="8910:sites/13-redwood"
)

for SITE_NAME in "${!SITES[@]}"; do
    IFS=':' read -r PORT WORKDIR <<< "${SITES[$SITE_NAME]}"

    echo "Deploying $SITE_NAME from Git..."

    koyeb app create "eventmesh-$SITE_NAME" \
      --git "$GITHUB_REPO" \
      --git-branch main \
      --git-workdir "$WORKDIR" \
      --git-buildpack dockerfile \
      --ports "$PORT:http" \
      --routes "/:$PORT" \
      --regions fra \
      --instance-type nano \
      --min-scale 1 \
      --max-scale 3 \
      --env PORT="$PORT" \
      --env NODE_ENV=production \
      --health-checks "/:http:$PORT"

    echo "✅ $SITE_NAME deployed from Git"
    sleep 5
done

echo "All apps deployed!"
EOF

chmod +x koyeb-deploy-git.sh
./koyeb-deploy-git.sh
```

### Example URLs for All 13 Sites

```
https://eventmesh-astro-basic-yourorg.koyeb.app
https://eventmesh-nextjs-app-yourorg.koyeb.app
https://eventmesh-sveltekit-yourorg.koyeb.app
https://eventmesh-remix-yourorg.koyeb.app
https://eventmesh-qwik-city-yourorg.koyeb.app
https://eventmesh-solid-start-yourorg.koyeb.app
https://eventmesh-nuxt-yourorg.koyeb.app
https://eventmesh-fresh-yourorg.koyeb.app
https://eventmesh-analog-yourorg.koyeb.app
https://eventmesh-gatsby-yourorg.koyeb.app
https://eventmesh-eleventy-yourorg.koyeb.app
https://eventmesh-hydrogen-yourorg.koyeb.app
https://eventmesh-redwood-yourorg.koyeb.app
```

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-koyeb.yml
name: Deploy to Koyeb

on:
  push:
    branches: [main]
    paths:
      - 'sites/**'
      - '.github/workflows/deploy-koyeb.yml'

env:
  KOYEB_TOKEN: ${{ secrets.KOYEB_API_TOKEN }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        site:
          - name: astro-basic
            path: sites/01-astro-basic
            port: 4321
          - name: nextjs-app
            path: sites/02-nextjs-app
            port: 3000
          - name: sveltekit
            path: sites/03-sveltekit
            port: 5173
          - name: remix
            path: sites/04-remix
            port: 3001
          - name: qwik-city
            path: sites/05-qwik-city
            port: 5174
          - name: solid-start
            path: sites/06-solid-start
            port: 3002
          - name: nuxt
            path: sites/07-nuxt
            port: 3003
          - name: fresh
            path: sites/08-fresh
            port: 8000
          - name: analog
            path: sites/09-analog
            port: 5175
          - name: gatsby
            path: sites/10-gatsby
            port: 9000
          - name: eleventy
            path: sites/11-eleventy-serverless
            port: 8080
          - name: hydrogen
            path: sites/12-hydrogen
            port: 3004
          - name: redwood
            path: sites/13-redwood
            port: 8910

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Check if site changed
        id: changed
        uses: dorny/paths-filter@v2
        with:
          filters: |
            site:
              - '${{ matrix.site.path }}/**'

      - name: Install Koyeb CLI
        if: steps.changed.outputs.site == 'true'
        run: |
          curl -fsSL https://cli.koyeb.com/install.sh | sh
          sudo mv koyeb /usr/local/bin/

      - name: Trigger Koyeb deployment
        if: steps.changed.outputs.site == 'true'
        run: |
          # Use Koyeb API to trigger redeploy
          curl -X POST "https://app.koyeb.com/v1/apps/eventmesh-${{ matrix.site.name }}/deployments" \
            -H "Authorization: Bearer ${{ env.KOYEB_TOKEN }}" \
            -H "Content-Type: application/json" \
            -d '{
              "definition": {
                "git": {
                  "repository": "${{ github.repository }}",
                  "branch": "main",
                  "workdir": "${{ matrix.site.path }}"
                }
              }
            }'

      - name: Wait for deployment
        if: steps.changed.outputs.site == 'true'
        run: |
          sleep 60

          # Get app URL
          APP_URL="https://eventmesh-${{ matrix.site.name }}-${{ secrets.KOYEB_ORG }}.koyeb.app"

          for i in {1..10}; do
            if curl -sSf "$APP_URL" > /dev/null; then
              echo "✅ Deployment successful!"
              exit 0
            fi
            echo "Waiting for app to be ready... ($i/10)"
            sleep 10
          done

          echo "❌ Deployment health check failed"
          exit 1

      - name: Output deployment info
        if: steps.changed.outputs.site == 'true'
        run: |
          echo "### Deployment Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Site:** ${{ matrix.site.name }}" >> $GITHUB_STEP_SUMMARY
          echo "**URL:** https://eventmesh-${{ matrix.site.name }}-${{ secrets.KOYEB_ORG }}.koyeb.app" >> $GITHUB_STEP_SUMMARY
```

### Pros & Cons

#### ✅ Pros
1. **Flat pricing**: $20/month unlimited apps
2. **Zero maintenance**: Fully managed platform
3. **Global CDN**: 150+ PoPs worldwide
4. **Auto-scaling**: 0-N instances
5. **Simple URLs**: Clean *.koyeb.app domains
6. **Git integration**: Deploy from GitHub directly
7. **Zero-downtime**: Rolling deployments
8. **Automatic HTTPS**: Managed SSL
9. **DDoS protection**: Built-in security
10. **Observability**: Built-in logs, metrics
11. **Multi-region**: Deploy to US/EU/Asia
12. **No cold starts**: Always warm (min: 1 instance)

#### ❌ Cons
1. **Fixed cost**: $20/month (not free)
2. **Instance limits**: Nano tier has CPU/RAM constraints
3. **Vendor lock-in**: Koyeb-specific
4. **Limited free tier**: Only 1 app free
5. **Build time**: Longer than pre-built containers
6. **Resource limits**: 512 MB RAM on nano tier
7. **Region choices**: Limited to 3 regions
8. **No spot pricing**: No cost optimization options

### Setup Time Estimate

- **Initial setup**: 20 minutes (one-time)
  - Account creation: 5 minutes
  - CLI installation: 2 minutes
  - Deploy all 13 apps: 13 minutes
- **Subsequent deployments**: Automatic (1-2 minutes per site via webhook)
- **Maintenance**: 5 minutes/month (review logs)

### Ongoing Maintenance Burden

**Weekly (5 minutes)**
- Check deployment logs for errors
- Review app health in dashboard

**Monthly (10 minutes)**
- Review billing ($20 flat)
- Check scaling metrics
- Update base images if needed

**Quarterly (30 minutes)**
- Review security updates
- Optimize app configurations
- Test failover scenarios

### CI/CD Setup

**Webhook-based deployment:**
```bash
# 1. Get Koyeb API token
koyeb token create github-actions

# 2. Add to GitHub Secrets
# KOYEB_API_TOKEN = token from step 1
# KOYEB_ORG = your-org-name

# 3. Webhook is auto-configured when using git deployment
# Koyeb listens to GitHub push events
# No manual webhook setup needed!
```

**Manual trigger via API:**
```bash
# Trigger deployment via API
curl -X POST "https://app.koyeb.com/v1/apps/APP_ID/deployments" \
  -H "Authorization: Bearer $KOYEB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"definition": {"git": {"branch": "main"}}}'
```

---

## Local Development Workflow

### Docker Compose Setup

```yaml
# docker-compose.yml (project root)
version: '3.8'

services:
  # Site 1: Astro Basic
  astro-basic:
    build:
      context: ./sites/01-astro-basic
      dockerfile: Dockerfile
    ports:
      - "4321:4321"
    environment:
      - PORT=4321
      - NODE_ENV=development
    volumes:
      - ./sites/01-astro-basic:/app
      - /app/node_modules
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.astro.rule=Host(`astro.localhost`)"

  # Site 2: Next.js App
  nextjs-app:
    build:
      context: ./sites/02-nextjs-app
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - PORT=3000
      - NODE_ENV=development
    volumes:
      - ./sites/02-nextjs-app:/app
      - /app/node_modules
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.nextjs.rule=Host(`nextjs.localhost`)"

  # Site 3: SvelteKit
  sveltekit:
    build:
      context: ./sites/03-sveltekit
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      - PORT=5173
      - NODE_ENV=development
    volumes:
      - ./sites/03-sveltekit:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 4: Remix
  remix:
    build:
      context: ./sites/04-remix
      dockerfile: Dockerfile
    ports:
      - "3001:3001"
    environment:
      - PORT=3001
      - NODE_ENV=development
    volumes:
      - ./sites/04-remix:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 5: Qwik City
  qwik-city:
    build:
      context: ./sites/05-qwik-city
      dockerfile: Dockerfile
    ports:
      - "5174:5174"
    environment:
      - PORT=5174
      - NODE_ENV=development
    volumes:
      - ./sites/05-qwik-city:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 6: Solid Start
  solid-start:
    build:
      context: ./sites/06-solid-start
      dockerfile: Dockerfile
    ports:
      - "3002:3002"
    environment:
      - PORT=3002
      - NODE_ENV=development
    volumes:
      - ./sites/06-solid-start:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 7: Nuxt
  nuxt:
    build:
      context: ./sites/07-nuxt
      dockerfile: Dockerfile
    ports:
      - "3003:3003"
    environment:
      - PORT=3003
      - NODE_ENV=development
    volumes:
      - ./sites/07-nuxt:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 8: Fresh (Deno)
  fresh:
    build:
      context: ./sites/08-fresh
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - DENO_ENV=development
    volumes:
      - ./sites/08-fresh:/app
    restart: unless-stopped

  # Site 9: Analog
  analog:
    build:
      context: ./sites/09-analog
      dockerfile: Dockerfile
    ports:
      - "5175:5175"
    environment:
      - PORT=5175
      - NODE_ENV=development
    volumes:
      - ./sites/09-analog:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 10: Gatsby
  gatsby:
    build:
      context: ./sites/10-gatsby
      dockerfile: Dockerfile
    ports:
      - "9000:9000"
    environment:
      - PORT=9000
      - NODE_ENV=development
    volumes:
      - ./sites/10-gatsby:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 11: Eleventy Serverless
  eleventy:
    build:
      context: ./sites/11-eleventy-serverless
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - NODE_ENV=development
    volumes:
      - ./sites/11-eleventy-serverless:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 12: Hydrogen
  hydrogen:
    build:
      context: ./sites/12-hydrogen
      dockerfile: Dockerfile
    ports:
      - "3004:3004"
    environment:
      - PORT=3004
      - NODE_ENV=development
    volumes:
      - ./sites/12-hydrogen:/app
      - /app/node_modules
    restart: unless-stopped

  # Site 13: RedwoodJS
  redwood:
    build:
      context: ./sites/13-redwood
      dockerfile: Dockerfile
    ports:
      - "8910:8910"
    environment:
      - PORT=8910
      - NODE_ENV=development
    volumes:
      - ./sites/13-redwood:/app
      - /app/node_modules
    restart: unless-stopped

  # Reverse proxy (optional - for *.localhost domains)
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    restart: unless-stopped

networks:
  default:
    name: eventmesh-local
```

### Local Development Commands

```bash
# Start all 13 sites
docker-compose up

# Start specific site
docker-compose up astro-basic

# Start subset of sites
docker-compose up astro-basic nextjs-app sveltekit

# Build all containers
docker-compose build

# Rebuild specific site
docker-compose build astro-basic

# View logs
docker-compose logs -f astro-basic

# Stop all
docker-compose down

# Clean up
docker-compose down -v  # Remove volumes
docker system prune -a  # Clean all Docker artifacts
```

### Local Development Script

```bash
# dev.sh - Development helper script
cat > dev.sh << 'EOF'
#!/bin/bash

case "$1" in
  start)
    echo "Starting all EventMesh test sites..."
    docker-compose up -d
    echo "✅ All sites running!"
    echo ""
    echo "Access sites:"
    echo "- Astro:      http://localhost:4321"
    echo "- Next.js:    http://localhost:3000"
    echo "- SvelteKit:  http://localhost:5173"
    echo "- Remix:      http://localhost:3001"
    echo "- Qwik:       http://localhost:5174"
    echo "- Solid:      http://localhost:3002"
    echo "- Nuxt:       http://localhost:3003"
    echo "- Fresh:      http://localhost:8000"
    echo "- Analog:     http://localhost:5175"
    echo "- Gatsby:     http://localhost:9000"
    echo "- Eleventy:   http://localhost:8080"
    echo "- Hydrogen:   http://localhost:3004"
    echo "- Redwood:    http://localhost:8910"
    echo ""
    echo "Traefik dashboard: http://localhost:8080"
    ;;

  stop)
    echo "Stopping all sites..."
    docker-compose down
    echo "✅ All sites stopped"
    ;;

  restart)
    echo "Restarting all sites..."
    docker-compose restart
    echo "✅ All sites restarted"
    ;;

  logs)
    if [ -z "$2" ]; then
      docker-compose logs -f
    else
      docker-compose logs -f "$2"
    fi
    ;;

  build)
    if [ -z "$2" ]; then
      echo "Rebuilding all sites..."
      docker-compose build
    else
      echo "Rebuilding $2..."
      docker-compose build "$2"
    fi
    echo "✅ Build complete"
    ;;

  clean)
    echo "Cleaning Docker artifacts..."
    docker-compose down -v
    docker system prune -a -f
    echo "✅ Cleanup complete"
    ;;

  status)
    docker-compose ps
    ;;

  *)
    echo "EventMesh Development Helper"
    echo ""
    echo "Usage: ./dev.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start           Start all sites"
    echo "  stop            Stop all sites"
    echo "  restart         Restart all sites"
    echo "  logs [site]     View logs (all or specific site)"
    echo "  build [site]    Rebuild containers (all or specific)"
    echo "  clean           Clean up Docker artifacts"
    echo "  status          Show running containers"
    echo ""
    echo "Examples:"
    echo "  ./dev.sh start"
    echo "  ./dev.sh logs astro-basic"
    echo "  ./dev.sh build nextjs-app"
    ;;
esac
EOF

chmod +x dev.sh
```

---

## Staging vs Production Strategy

### Environment Configuration

```bash
# Environment structure
environments/
├── local/          # docker-compose.yml
├── staging/        # staging configs
└── production/     # production configs
```

### Approach 1: Branch-Based Environments

```yaml
# GitHub Actions workflow
name: Multi-Environment Deployment

on:
  push:
    branches:
      - main        # → Production
      - staging     # → Staging
      - develop     # → Development

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Determine environment
        id: env
        run: |
          if [ "${{ github.ref }}" == "refs/heads/main" ]; then
            echo "environment=production" >> $GITHUB_OUTPUT
            echo "url_suffix=prod" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref }}" == "refs/heads/staging" ]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
            echo "url_suffix=staging" >> $GITHUB_OUTPUT
          else
            echo "environment=development" >> $GITHUB_OUTPUT
            echo "url_suffix=dev" >> $GITHUB_OUTPUT
          fi

      - name: Deploy to environment
        run: |
          # Deploy logic based on ${{ steps.env.outputs.environment }}
          echo "Deploying to ${{ steps.env.outputs.environment }}"
```

### Approach 2: Subdomain-Based Environments

**Hetzner + Coolify:**
```
Production:  astro.example.com
Staging:     astro-staging.example.com
Development: astro-dev-1.39.185.42.sslip.io
```

**Google Cloud Run:**
```
Production:  astro-prod-abc123.a.run.app
Staging:     astro-staging-abc123.a.run.app
Development: astro-dev-abc123.a.run.app
```

**Koyeb:**
```
Production:  astro-prod-yourorg.koyeb.app
Staging:     astro-staging-yourorg.koyeb.app
Development: astro-dev-yourorg.koyeb.app
```

### Environment Variables Management

```yaml
# .env.production
NODE_ENV=production
API_URL=https://api.example.com
ANALYTICS=enabled
DEBUG=false

# .env.staging
NODE_ENV=staging
API_URL=https://api-staging.example.com
ANALYTICS=disabled
DEBUG=true

# .env.development
NODE_ENV=development
API_URL=http://localhost:4000
ANALYTICS=disabled
DEBUG=true
```

**GitHub Secrets per environment:**
```bash
# Production secrets
PROD_DATABASE_URL=postgresql://...
PROD_API_KEY=xyz123

# Staging secrets
STAGING_DATABASE_URL=postgresql://...
STAGING_API_KEY=abc456
```

---

## Provider Switching Guide

### Migration Checklist

```bash
# Pre-migration checklist
□ Export environment variables from current provider
□ Backup databases (if any)
□ Document current URLs
□ Test containers locally
□ Prepare DNS changes (if using custom domains)
□ Notify users of potential downtime
```

### Hetzner → Google Cloud Run

```bash
# 1. Export Coolify app configs
# (Manual step - note env vars, ports, etc.)

# 2. Build containers for Cloud Run
./build-all-containers.sh  # From Cloud Run section

# 3. Deploy to Cloud Run
./deploy-all-cloudrun.sh

# 4. Test Cloud Run URLs
for i in {1..13}; do
  curl -I https://eventmesh-site$i-abc.a.run.app
done

# 5. Update DNS (if using custom domains)
# Point CNAME to Cloud Run

# 6. Decommission Hetzner VPS
# Cancel subscription in Hetzner Cloud Console
```

### Google Cloud Run → Koyeb

```bash
# 1. Images already in Artifact Registry
# Can re-use or push to Docker Hub

# 2. Deploy to Koyeb from registry
./koyeb-deploy-all.sh  # From Koyeb section

# 3. Test Koyeb URLs
koyeb app list

# 4. Update DNS
# Point CNAME to Koyeb

# 5. Delete Cloud Run services
gcloud run services delete eventmesh-astro-basic --region=us-central1 --quiet
# Repeat for all 13 services
```

### Koyeb → Hetzner

```bash
# 1. Provision Hetzner VPS
# Follow Hetzner setup from Architecture 1

# 2. Install Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# 3. Deploy to Coolify
# Via UI or API (see Hetzner section)

# 4. Test sslip.io URLs
for i in {1..13}; do
  curl -I https://site$i-1.39.185.42.sslip.io
done

# 5. Update DNS
# Point to Hetzner IP

# 6. Delete Koyeb apps
koyeb app delete eventmesh-astro-basic
# Repeat for all 13 apps
```

### Zero-Downtime Migration Strategy

```bash
# 1. Deploy to new provider (in parallel)
# 2. Test new URLs thoroughly
# 3. Update DNS with low TTL (60 seconds)
# 4. Monitor traffic shifting to new provider
# 5. After 24 hours, decommission old provider
```

---

## Rollback Procedures

### Hetzner + Coolify Rollback

```bash
# Via Coolify UI:
# 1. Navigate to app
# 2. Click "Deployments" tab
# 3. Find previous successful deployment
# 4. Click "Redeploy"

# Via CLI (manual):
ssh root@1.39.185.42
cd /data/coolify/applications/APP_ID
docker-compose restart  # Restart current
# Or manually revert to previous image

# Time to rollback: 1-2 minutes
```

### Google Cloud Run Rollback

```bash
# List revisions
gcloud run revisions list \
  --service=eventmesh-astro-basic \
  --region=us-central1

# Rollback to previous revision
gcloud run services update-traffic eventmesh-astro-basic \
  --to-revisions=eventmesh-astro-basic-00001-abc=100 \
  --region=us-central1

# Time to rollback: 10-30 seconds
```

### Koyeb Rollback

```bash
# Via Koyeb UI:
# 1. Navigate to app
# 2. Click "Deployments"
# 3. Select previous deployment
# 4. Click "Redeploy"

# Via API:
curl -X POST "https://app.koyeb.com/v1/apps/APP_ID/deployments/DEPLOYMENT_ID/redeploy" \
  -H "Authorization: Bearer $KOYEB_TOKEN"

# Time to rollback: 30-60 seconds
```

### Automated Rollback on Failure

```yaml
# GitHub Actions with auto-rollback
- name: Deploy and verify
  id: deploy
  run: |
    # Deploy
    ./deploy.sh

    # Health check
    if ! curl -sSf "$DEPLOYMENT_URL"; then
      echo "Health check failed!"
      exit 1
    fi

- name: Rollback on failure
  if: failure() && steps.deploy.outcome == 'failure'
  run: |
    echo "Deployment failed, rolling back..."
    ./rollback.sh
```

---

## Health Monitoring

### Per-Architecture Monitoring

#### Hetzner + Coolify

```bash
# Built-in Coolify monitoring
# - Dashboard shows: CPU, RAM, Network, Disk
# - Per-app health checks
# - Automatic restart on failure

# External monitoring setup:
# 1. Install monitoring agent
apt install prometheus-node-exporter

# 2. Configure uptime monitoring
# Use UptimeRobot, Pingdom, or StatusCake
# Monitor: https://astro-1.39.185.42.sslip.io/health

# 3. Set up alerts
# Email/Slack on downtime
```

#### Google Cloud Run

```bash
# Built-in Cloud Monitoring (Stackdriver)
# - Request count, latency, errors
# - Container CPU, memory
# - Cold start metrics

# Set up alerts:
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Cloud Run Error Alert" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=60s

# View logs:
gcloud run logs read eventmesh-astro-basic \
  --region=us-central1 \
  --limit=50
```

#### Koyeb

```bash
# Built-in Koyeb observability
# - Request metrics
# - Response times
# - Error rates
# - Instance health

# View metrics via CLI:
koyeb app get eventmesh-astro-basic --metrics

# View logs:
koyeb app logs eventmesh-astro-basic --follow

# Set up webhooks for alerts:
koyeb webhook create deployment-alerts \
  --url https://your-webhook-url.com \
  --events deployment.failed,deployment.crashed
```

### Universal Health Check Script

```bash
# health-check-all.sh
cat > health-check-all.sh << 'EOF'
#!/bin/bash

# Configuration
PROVIDER="$1"  # hetzner | cloudrun | koyeb

case "$PROVIDER" in
  hetzner)
    BASE_URL="1.39.185.42.sslip.io"
    SITES=("astro" "nextjs" "sveltekit" "remix" "qwik" "solid" "nuxt" "fresh" "analog" "gatsby" "eleventy" "hydrogen" "redwood")
    ;;
  cloudrun)
    BASE_URL="a.run.app"
    SITES=("eventmesh-astro-basic-abc123-uc" "eventmesh-nextjs-app-abc123-uc" ...)
    ;;
  koyeb)
    BASE_URL="yourorg.koyeb.app"
    SITES=("eventmesh-astro-basic" "eventmesh-nextjs-app" ...)
    ;;
esac

echo "Health Check Report - $(date)"
echo "================================"

FAILED=0
for SITE in "${SITES[@]}"; do
  URL="https://${SITE}-${BASE_URL}"

  if curl -sSf -o /dev/null -w "%{http_code}" "$URL" | grep -q "200"; then
    echo "✅ $SITE - OK"
  else
    echo "❌ $SITE - FAILED"
    FAILED=$((FAILED + 1))
  fi
done

echo "================================"
echo "Total: ${#SITES[@]} sites"
echo "Failed: $FAILED sites"

if [ $FAILED -gt 0 ]; then
  exit 1
fi
EOF

chmod +x health-check-all.sh

# Run health checks
./health-check-all.sh hetzner
./health-check-all.sh cloudrun
./health-check-all.sh koyeb
```

### Scheduled Health Checks (GitHub Actions)

```yaml
# .github/workflows/health-check.yml
name: Health Check All Sites

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:  # Manual trigger

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run health checks
        run: |
          ./health-check-all.sh ${{ secrets.PROVIDER }}

      - name: Notify on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: 'Health check failed for EventMesh test sites!'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Decision Matrix

### Quick Comparison Table

| Feature | Hetzner + Coolify | Google Cloud Run | Koyeb |
|---------|-------------------|------------------|-------|
| **Cost/month** | $4-7 | $0-8 (likely free) | $20 |
| **Setup time** | 45 min | 30 min | 20 min |
| **Maintenance** | 1 hr/month | 10 min/month | 5 min/month |
| **SSL/HTTPS** | ✅ Auto (Let's Encrypt) | ✅ Auto (Google) | ✅ Auto (Koyeb) |
| **Auto-deploy** | ✅ Git webhooks | ✅ GitHub Actions | ✅ Git webhooks |
| **Scaling** | Manual (upgrade VPS) | Auto (0-N) | Auto (0-N) |
| **Cold starts** | ❌ None (always on) | ✅ 1-3s | ❌ None (min: 1) |
| **Global CDN** | ❌ Single datacenter | ✅ Global | ✅ 150+ PoPs |
| **Custom domains** | ✅ Easy | ✅ Easy | ✅ Easy |
| **Vendor lock-in** | ❌ Low (Docker) | ⚠️ Medium (GCP) | ⚠️ Medium (Koyeb) |
| **Control** | ✅ Full (root) | ❌ None (PaaS) | ❌ None (PaaS) |
| **Free tier** | ❌ No | ✅ Yes | ⚠️ 1 app only |
| **Rollback** | ✅ 1-2 min | ✅ 10-30s | ✅ 30-60s |
| **Monitoring** | Built-in dashboard | Stackdriver | Built-in observability |
| **Best for** | Cost-conscious, control | Free tier, global | Simplicity, flat pricing |

### Recommendation by Use Case

#### 1. **Long-term testing (6+ months)**
**Choose: Hetzner + Coolify**
- Lowest cost over time
- Full control for experiments
- No surprise bills

#### 2. **Short-term testing (1-3 months)**
**Choose: Google Cloud Run**
- Free tier covers usage
- Zero setup overhead
- Easy to tear down

#### 3. **Production-ready testing**
**Choose: Koyeb**
- No cold starts
- Global CDN
- Predictable pricing

#### 4. **Learning/experimentation**
**Choose: Hetzner + Coolify**
- Root access for learning
- Flexible configuration
- Self-hosting experience

#### 5. **Proof of concept for stakeholders**
**Choose: Koyeb**
- Professional URLs
- Fast global performance
- Reliable uptime

### Cost Projection (12 months)

| Provider | Month 1-3 | Month 4-6 | Month 7-12 | Total |
|----------|-----------|-----------|------------|-------|
| Hetzner | $15 | $15 | $30 | $60 |
| Cloud Run | $0 | $0 | $0-24 | $0-24 |
| Koyeb | $60 | $60 | $120 | $240 |

**Winner for cost: Google Cloud Run (if staying in free tier)**
**Runner-up: Hetzner + Coolify ($60/year)**

---

## Complete Implementation Timeline

### Week 1: Initial Setup

**Day 1-2: Choose provider**
- Review decision matrix
- Consider budget, timeline, technical requirements
- Set up account

**Day 3-4: Deploy first 3 sites**
- Follow step-by-step guide
- Test deployment workflow
- Debug any issues

**Day 5-7: Deploy remaining 10 sites**
- Automate deployment
- Document URLs
- Set up monitoring

### Week 2: CI/CD & Automation

**Day 8-10: GitHub Actions**
- Implement deployment workflow
- Test auto-deploy on push
- Add health checks

**Day 11-12: Monitoring & Alerts**
- Set up uptime monitoring
- Configure alerts
- Test rollback procedures

**Day 13-14: Documentation**
- Document all URLs
- Create runbooks
- Train team members

### Ongoing: Maintenance

**Weekly:**
- Review deployment logs
- Check resource usage
- Monitor costs

**Monthly:**
- Security updates
- Performance optimization
- Cost review

---

## Quick Start Cheat Sheet

```bash
# HETZNER + COOLIFY
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
# Access: http://YOUR_IP:8000
# Deploy via UI

# GOOGLE CLOUD RUN
gcloud run deploy APP_NAME \
  --image=IMAGE_URL \
  --region=us-central1 \
  --allow-unauthenticated

# KOYEB
koyeb app create APP_NAME \
  --git github.com/user/repo \
  --git-branch main

# DOCKER COMPOSE (LOCAL)
docker-compose up -d

# HEALTH CHECK ALL
./health-check-all.sh PROVIDER
```

---

## Conclusion

All three architectures provide viable solutions for deploying 13 EventMesh test sites. Choose based on:

1. **Budget priority** → Hetzner + Coolify ($4-7/month)
2. **Free tier priority** → Google Cloud Run ($0)
3. **Simplicity priority** → Koyeb ($20/month)

Each architecture is production-ready, with automatic HTTPS, CI/CD integration, and straightforward rollback procedures.

**Next steps:**
1. Review decision matrix
2. Choose architecture
3. Follow step-by-step guide
4. Deploy first site
5. Scale to all 13 sites
6. Set up monitoring
7. Enjoy automated deployments!
# Hosting Provider Comparison for 13 Small Test Sites (2025)

**Research Date**: January 2025
**Use Case**: Deploy 13 small Docker containers (~150MB each) for testing
**Budget Target**: <$20/month total

---

## Executive Summary

After comprehensive research of 12 hosting platforms, the **clear winner** for your use case is:

**🏆 WINNER: Hetzner VPS + Coolify/Traefik** - Total cost: €3.49-6/month (~$4-7/month)

**Runner-up options**:
1. **Google Cloud Run** - Potentially free under generous free tier
2. **Fly.io** - ~$0-5/month with free tier
3. **Koyeb** - $0-10/month with free tier

---

## Detailed Platform Comparison

### 1. Fly.io

**Monthly Cost for 13 Sites**: $0-5/month (likely free)

| Metric | Details |
|--------|---------|
| **Free Tier** | 3 shared VMs (256MB RAM each, 1 CPU)<br>3GB volume storage<br>160GB outbound transfer |
| **Subdomain Strategy** | `app-name.fly.dev` (automatic) |
| **Docker Support** | ⭐⭐⭐⭐⭐ Excellent - Native Docker support |
| **Deployment Complexity** | 3/10 - Very simple (`fly launch`) |
| **Uptime SLA** | No official SLA on free tier |
| **Scaling Cost** | Shared CPU 1GB RAM: $5.70/month<br>Storage: $0.15/GB/month |

**Pros**:
- Generous free tier (3 VMs free)
- Automatic SSL/TLS
- Global edge network
- Excellent Docker support
- Simple CLI deployment
- Each app gets automatic subdomain

**Cons**:
- Free tier only covers 3 apps (would need paid for 10 more)
- Limited to 256MB RAM per free VM
- Machines sleep after inactivity on free tier
- Cost adds up quickly beyond free tier (~$57/month for 10 additional VMs)

**Verdict**: Good for 1-3 apps, too expensive for 13 apps ($60+/month total)

---

### 2. Railway.app

**Monthly Cost for 13 Sites**: $30-50/month

| Metric | Details |
|--------|---------|
| **Free Tier** | One-time $5 credit (not monthly) |
| **Subdomain Strategy** | `*.up.railway.app` (automatic) |
| **Docker Support** | ⭐⭐⭐⭐⭐ Excellent - Docker & Nixpacks |
| **Deployment Complexity** | 2/10 - Very simple (Git push or CLI) |
| **Uptime SLA** | 99.9% for paid plans |
| **Pricing Model** | $5/month subscription + usage-based<br>Pay only for actual resource consumption |

**Pros**:
- Beautiful developer experience
- Automatic deployments from Git
- Usage-based pricing (pay for what you use)
- Excellent documentation
- Built-in databases
- Each service gets subdomain

**Cons**:
- No ongoing free tier (one-time $5 credit)
- $5 trial depletes quickly for 24/7 apps
- Would need Hobby plan ($5/month base + usage)
- Estimated $20-40/month for 13 small apps
- Too expensive for budget

**Verdict**: Great platform but exceeds budget for 13 sites

---

### 3. Render.com

**Monthly Cost for 13 Sites**: $91/month (free tier sleeps)

| Metric | Details |
|--------|---------|
| **Free Tier** | Unlimited web services<br>512MB RAM, 0.1 CPU each<br>100GB bandwidth/month<br>**Services sleep after 15 min inactivity** |
| **Subdomain Strategy** | `app-name.onrender.com` (automatic) |
| **Docker Support** | ⭐⭐⭐⭐⭐ Excellent - Native Docker images |
| **Deployment Complexity** | 2/10 - Very simple (Git connect or Dockerfile) |
| **Uptime SLA** | 99.95% for paid services |
| **Paid Pricing** | Starter: $7/month per service<br>Pro: $85/month per service |

**Pros**:
- Generous free tier with unlimited services
- Automatic SSL certificates
- Great Git integration
- Background workers, cron jobs
- Native Docker support
- PostgreSQL, Redis included

**Cons**:
- Free tier sleeps after 15 minutes (dealbreaker for 24/7 testing)
- Paid tier: $7/service = $91/month for 13 sites
- **WAY over budget**
- Spin-up time on free tier (slow wake-up)

**Verdict**: Free tier unusable (sleeps), paid tier too expensive ($91/month)

---

### 4. DigitalOcean App Platform

**Monthly Cost for 13 Sites**: $65/month minimum

| Metric | Details |
|--------|---------|
| **Free Tier** | 3 static sites only (no containers) |
| **Subdomain Strategy** | `*.ondigitalocean.app` (automatic) |
| **Docker Support** | ⭐⭐⭐⭐ Good - Docker Hub, GitHub CR, DO CR |
| **Deployment Complexity** | 3/10 - Simple via UI or doctl CLI |
| **Uptime SLA** | 99.99% |
| **Container Pricing** | Shared 512MB: $5/month<br>Shared 1GB: $12/month |

**Pros**:
- Reliable infrastructure
- Autoscaling
- No hidden bandwidth fees
- Integration with DO ecosystem
- Automatic deployments

**Cons**:
- No free tier for containers
- $5/container minimum = $65/month for 13 sites
- **Over budget by 3x**
- Limited resources on basic tier

**Verdict**: Too expensive at $65/month minimum

---

### 5. Google Cloud Run

**Monthly Cost for 13 Sites**: $0-8/month (likely FREE)

| Metric | Details |
|--------|---------|
| **Free Tier** | 2 million requests/month<br>180,000 vCPU-seconds/month<br>360,000 GiB-seconds/month<br>**Very generous limits** |
| **Subdomain Strategy** | `*.run.app` (automatic per region) |
| **Docker Support** | ⭐⭐⭐⭐⭐ Excellent - Container-native |
| **Deployment Complexity** | 4/10 - Requires GCP setup, moderate learning curve |
| **Uptime SLA** | 99.95% |
| **Beyond Free** | CPU: $0.0000336/vCPU-sec<br>Memory: $0.0000035/GiB-sec<br>Requests: $0.40/million |

**Pros**:
- EXTREMELY generous free tier
- Pay only for actual execution time
- Scales to zero (no idle costs)
- Global CDN
- Per-second billing
- 13 small test sites likely stay under free tier
- Automatic SSL

**Cons**:
- GCP complexity (billing, IAM, projects)
- Cold start latency (~1-3 seconds)
- Requires Google account setup
- Learning curve for GCP console
- Multiple services require organization

**Verdict**: ⭐ Excellent choice - likely FREE for 13 test sites

---

### 6. AWS App Runner

**Monthly Cost for 13 Sites**: $40-65/month

| Metric | Details |
|--------|---------|
| **Free Tier** | None (no free tier) |
| **Subdomain Strategy** | `*.awsapprunner.com` (automatic) |
| **Docker Support** | ⭐⭐⭐⭐ Good - ECR or public registries |
| **Deployment Complexity** | 5/10 - AWS complexity, IAM roles, ECR setup |
| **Uptime SLA** | 99.9% |
| **Pricing** | Provisioned (idle): $0.007/GB-hour<br>Active: $0.064/vCPU-hour + memory<br>~$3-5/month per small service |

**Pros**:
- Integrates with AWS ecosystem
- No load balancer costs ($15 savings)
- Automatic scaling
- Pay-per-second billing
- Pause when idle (reduced costs)

**Cons**:
- No free tier
- AWS complexity (IAM, VPC, ECR)
- $3-5/service = $39-65/month for 13 sites
- **Over budget**
- Steep learning curve

**Verdict**: Too expensive and complex for simple test sites

---

### 7. Koyeb

**Monthly Cost for 13 Sites**: $0-20/month

| Metric | Details |
|--------|---------|
| **Free Tier** | 1 web service (512MB RAM, 0.1 vCPU)<br>1 database<br>5 custom domains<br>**Scales to zero** |
| **Subdomain Strategy** | `*.koyeb.app` (automatic) |
| **Docker Support** | ⭐⭐⭐⭐⭐ Excellent - Native Docker support |
| **Deployment Complexity** | 2/10 - Very simple (Git or Docker) |
| **Uptime SLA** | 99.9% |
| **Eco Instances** | $1.61/month per instance minimum |

**Pros**:
- One free service (always-on)
- Scale to zero (cost-effective)
- Global edge network
- Simple deployment
- 12 additional eco instances: ~$19/month
- Total: ~$20/month for 13 sites ✅

**Cons**:
- Requires credit card for free tier
- Free tier limited to 1 service
- Less mature platform
- Smaller community

**Verdict**: ⭐ Excellent budget option at ~$20/month total

---

### 8-9. Self-Hosted VPS Options

#### Option A: Hetzner VPS + Coolify (RECOMMENDED)

**Monthly Cost for 13 Sites**: €3.49-6/month (~$4-7/month)

| Metric | Details |
|--------|---------|
| **VPS Cost** | Hetzner CAX11 (ARM): €3.49/month<br>2GB RAM, 1 vCPU, 40GB SSD<br>OR CX21: €5.49/month (4GB RAM, 2 vCPU) |
| **Coolify** | Self-hosted: FREE forever<br>Cloud: $4/month (optional) |
| **Subdomain Strategy** | Wildcard DNS + Traefik/Caddy<br>Configure `*.yourdomain.com` |
| **Docker Support** | ⭐⭐⭐⭐⭐ Perfect - Full Docker Compose |
| **Deployment Complexity** | 6/10 - Initial setup required, then simple |
| **Uptime SLA** | 99.9% (Hetzner) |

**Setup**:
1. Provision Hetzner VPS (€3.49-5.49/month)
2. Install Coolify (free, self-hosted)
3. Configure Traefik for automatic routing
4. Point wildcard DNS to VPS IP
5. Deploy apps via Git or Docker Compose

**Pros**:
- **Cheapest option overall** (€3.49/month!)
- Full control over infrastructure
- 13 sites easily fit in 2GB RAM
- Coolify provides Heroku-like UI
- Automatic SSL via Let's Encrypt
- No per-app fees
- Can host 50+ small sites on one VPS
- Best price/performance ratio

**Cons**:
- Requires DNS setup (need domain)
- Initial learning curve for Coolify/Traefik
- You manage server updates
- Single point of failure (one VPS)
- Need basic Linux knowledge

**Verdict**: 🏆 BEST VALUE - Perfect for $20 budget, overkill in savings

---

#### Option B: Hetzner VPS + Traefik (Manual Setup)

**Monthly Cost**: €3.49-5.49/month (~$4-6/month)

Same as Option A but manual Docker Compose + Traefik configuration instead of Coolify UI.

**Deployment Complexity**: 7/10 (higher learning curve)

**Pros**: More control, no additional tools
**Cons**: More manual configuration, steeper learning curve

---

#### Option C: DigitalOcean/Linode VPS

**Monthly Cost**: $5-10/month

| Provider | Cost | Specs |
|----------|------|-------|
| **Linode** | $5/month | 1GB RAM, 1 vCPU, 25GB SSD |
| **DigitalOcean** | $6/month | 1GB RAM, 1 vCPU, 25GB SSD |

Similar to Hetzner but:
- More expensive ($5-10 vs €3.49)
- Better documentation/tutorials
- Larger community
- Same setup complexity

**Verdict**: Works but Hetzner offers better value

---

### 10. Coolify Cloud (Managed)

**Monthly Cost**: $4-10/month + VPS costs

| Metric | Details |
|--------|---------|
| **Coolify Cloud** | $4/month (managed dashboard)<br>BYOS (bring your own VPS) |
| **Total Cost** | $4 + €3.49 VPS = ~$8/month |
| **Deployment Complexity** | 4/10 - Easier than self-hosted |

**Pros**:
- Managed Coolify updates
- Automatic backups
- Easy dashboard access
- Still bring your own VPS (cost-effective)

**Cons**:
- Additional $4/month fee
- Still need VPS

**Verdict**: Good compromise between managed and self-hosted

---

### 11. Dokku (Self-Hosted PaaS)

**Monthly Cost**: VPS cost only (~$4-5/month)

| Metric | Details |
|--------|---------|
| **Software Cost** | FREE (open-source) |
| **VPS Required** | Any VPS (Hetzner, DO, Linode) |
| **Subdomain Strategy** | Wildcard DNS required |
| **Docker Support** | ⭐⭐⭐⭐⭐ Excellent - Heroku-like buildpacks |
| **Deployment Complexity** | 7/10 - Command-line heavy |

**Pros**:
- Free software
- Heroku-like `git push` deployment
- Full control
- Plugin ecosystem

**Cons**:
- Steeper learning curve than Coolify
- Command-line only (no GUI)
- Manual SSL setup
- Less user-friendly

**Verdict**: Great for developers comfortable with CLI, harder for beginners

---

### 12. Kamal (Basecamp)

**Monthly Cost**: VPS cost only (~$4-5/month)

| Metric | Details |
|--------|---------|
| **Software Cost** | FREE (open-source) |
| **Deployment Complexity** | 8/10 - For experienced devops |
| **Docker Support** | ⭐⭐⭐⭐⭐ Native Docker orchestration |

**Pros**:
- Modern deployment tool
- Zero-downtime deployments
- Multi-server support
- Created by Basecamp (37signals)

**Cons**:
- Higher complexity
- Requires deep Docker knowledge
- Command-line only
- Best for production, overkill for test sites

**Verdict**: Powerful but too complex for simple test sites

---

## Ranked Comparison Table

| Rank | Provider | Monthly Cost | Complexity (1-10) | Free Tier | Subdomains | Docker Support | Best For |
|------|----------|--------------|-------------------|-----------|------------|----------------|----------|
| 🥇 1 | **Hetzner + Coolify** | **€3.49-6** (~$4-7) | 6/10 | N/A (VPS) | Wildcard DNS | ⭐⭐⭐⭐⭐ | **13+ sites, max savings** |
| 🥈 2 | **Google Cloud Run** | **$0-8** (likely free) | 4/10 | Very generous | Auto `*.run.app` | ⭐⭐⭐⭐⭐ | **Low-traffic test sites** |
| 🥉 3 | **Koyeb** | **$0-20** | 2/10 | 1 service | Auto `*.koyeb.app` | ⭐⭐⭐⭐⭐ | **Simple managed hosting** |
| 4 | **Fly.io** | $0-60 | 3/10 | 3 VMs | Auto `*.fly.dev` | ⭐⭐⭐⭐⭐ | **1-3 apps only** |
| 5 | **Coolify Cloud** | $8-12 | 4/10 | None | Wildcard DNS | ⭐⭐⭐⭐⭐ | **Managed self-host** |
| 6 | **Linode/DO VPS** | $5-10 | 7/10 | $100 trial | Wildcard DNS | ⭐⭐⭐⭐⭐ | **Self-host with support** |
| 7 | **Railway** | $30-50 | 2/10 | $5 one-time | Auto `*.up.railway.app` | ⭐⭐⭐⭐⭐ | **Developer experience** |
| 8 | **AWS App Runner** | $40-65 | 5/10 | None | Auto AWS domains | ⭐⭐⭐⭐ | **AWS ecosystem only** |
| 9 | **DigitalOcean App** | $65+ | 3/10 | 3 static only | Auto DO domains | ⭐⭐⭐⭐ | **DO users only** |
| 10 | **Render** | $91+ (or free+sleep) | 2/10 | Unlimited (sleeps) | Auto `*.onrender.com` | ⭐⭐⭐⭐⭐ | **Free hobby projects** |

---

## Final Recommendations

### 🏆 WINNER: Hetzner VPS + Coolify

**Cost**: €3.49-6/month (~$4-7/month)
**Why**: Cheapest, most flexible, supports 13+ sites easily

**Setup Steps**:
1. Create Hetzner account
2. Deploy CAX11 or CX21 VPS (€3.49-5.49/month)
3. Install Coolify: `curl -fsSL https://get.coolify.io | bash`
4. Configure wildcard DNS (optional: use nip.io for free subdomains)
5. Deploy Docker Compose apps via Coolify UI

**Expected Performance**: All 13 sites run comfortably on 2-4GB RAM VPS

---

### 🥈 Runner-up: Google Cloud Run

**Cost**: $0-8/month (likely FREE)
**Why**: Generous free tier, scales to zero, no infrastructure management

**Best if**:
- You want zero infrastructure management
- Sites have low/intermittent traffic
- You can tolerate cold starts
- You don't want to manage servers

**Setup**: Simpler than VPS but requires GCP knowledge

---

### 🥉 Third Place: Koyeb

**Cost**: ~$20/month (1 free + 12 eco instances)
**Why**: Simple, managed, right at budget

**Best if**:
- You want fully managed hosting
- Budget is exactly $20/month
- You want simple Git-based deployment
- No server management desired

---

## Cost Breakdown Comparison

| Provider | Setup Cost | Monthly Cost | Annual Cost |
|----------|------------|--------------|-------------|
| **Hetzner + Coolify** | €0 | €3.49-6 | €42-72 ($46-79) |
| **Google Cloud Run** | $0 | $0-8 | $0-96 |
| **Koyeb** | $0 | $0-20 | $0-240 |
| **Fly.io** | $0 | $0-60 | $0-720 |
| **Railway** | $0 | $30-50 | $360-600 |
| **Render** | $0 | $0 (sleeps) or $91 | $0 or $1,092 |
| **DO App Platform** | $0 | $65 | $780 |
| **AWS App Runner** | $0 | $40-65 | $480-780 |

---

## Additional Considerations

### Subdomain Strategy Without Buying Domains

If you don't want to buy a domain:

1. **Platform-provided subdomains** (easiest):
   - Fly.io: `app-name.fly.dev`
   - Render: `app-name.onrender.com`
   - Railway: `app-name.up.railway.app`
   - Koyeb: `app-name.koyeb.app`
   - Google Cloud Run: `app-name-hash.run.app`

2. **Free wildcard DNS services** (for VPS):
   - `nip.io`: `site1.123.456.789.100.nip.io` (points to your IP)
   - `sslip.io`: Similar to nip.io
   - `traefik.me`: Traefik-friendly DNS

3. **Namecheap/Porkbun cheap domains**:
   - `.xyz` domain: ~$1-2/year
   - `.tech` domain: ~$3-5/year
   - Then use wildcard DNS for all 13 sites

---

## Stability and Uptime Comparison

| Provider | SLA | Reported Uptime | Notes |
|----------|-----|-----------------|-------|
| Google Cloud Run | 99.95% | Excellent | Google infrastructure |
| Hetzner | 99.9% | Very good | German reliability |
| DigitalOcean | 99.99% | Excellent | Mature platform |
| Fly.io | No SLA (free) | Good | Edge network |
| Render | 99.95% (paid) | Good | Occasional issues |
| Railway | 99.9% | Good | Had major outage June 2025 |
| Koyeb | 99.9% | Good | Smaller platform |
| AWS App Runner | 99.9% | Excellent | AWS infrastructure |

---

## Docker Compose Support

| Provider | Native Docker Compose | Notes |
|----------|----------------------|-------|
| Hetzner + Coolify | ✅ Full support | Docker Compose files work perfectly |
| Hetzner + Traefik | ✅ Full support | Manual setup required |
| Google Cloud Run | ❌ Single container | No Compose (multi-container needs GKE) |
| Fly.io | ⚠️ Fly.toml conversion | Not native Compose, needs conversion |
| Render | ⚠️ Limited | Supports via render.yaml |
| Railway | ⚠️ Limited | Supports but prefers individual services |
| Koyeb | ❌ Single container | No multi-container support |
| DO App Platform | ⚠️ Limited | Prefers single containers |

**Winner for Docker Compose**: Self-hosted VPS options (Hetzner + Coolify/Traefik)

---

## Implementation Difficulty Scale

**1-3 (Easy)**:
- Railway (2/10) - Just connect Git
- Render (2/10) - Connect Git or Dockerfile
- Koyeb (2/10) - Simple UI
- Fly.io (3/10) - CLI-based but well-documented

**4-5 (Moderate)**:
- Google Cloud Run (4/10) - GCP setup needed
- Coolify Cloud (4/10) - VPS setup + managed Coolify
- AWS App Runner (5/10) - AWS complexity

**6-7 (Intermediate)**:
- Hetzner + Coolify (6/10) - VPS + Coolify self-install
- Linode/DO VPS (7/10) - Manual Docker + Traefik setup
- Dokku (7/10) - CLI-heavy setup

**8-10 (Advanced)**:
- Kamal (8/10) - Advanced Docker orchestration
- Kubernetes (10/10) - Overkill for this use case

---

## Final Verdict

### For Absolute Best Value:
**🏆 Hetzner VPS (€3.49) + Coolify (free)**
- Total: ~$4-7/month
- Saves $156-192/year vs managed alternatives
- 6/10 complexity (worth the savings)

### For Zero Infrastructure Management:
**🥈 Google Cloud Run**
- Likely FREE under generous free tier
- 4/10 complexity
- Best for low-traffic test sites

### For Simplicity at Budget:
**🥉 Koyeb**
- $20/month (exactly at budget)
- 2/10 complexity
- Managed, simple, works

---

## Action Plan

**Recommended approach**:

1. **Start with Google Cloud Run** (FREE trial):
   - Deploy all 13 sites
   - Test if they stay under free tier
   - If yes, keep it (FREE!)
   - If no, move to option 2

2. **If GCP exceeds free tier, move to Hetzner + Coolify**:
   - Cost: €3.49-6/month
   - One-time setup (~2-3 hours)
   - Long-term savings

3. **Fallback: Koyeb** if you want managed:
   - $20/month
   - Zero server management
   - Right at budget

---

## Resources

### Hetzner + Coolify Setup:
- Coolify docs: https://coolify.io/docs
- Hetzner VPS: https://www.hetzner.com/cloud
- Tutorial: https://coolify.io/docs/installation

### Google Cloud Run:
- Pricing calculator: https://cloud.google.com/run/pricing
- Quickstart: https://cloud.google.com/run/docs/quickstarts

### Koyeb:
- Pricing: https://www.koyeb.com/pricing
- Docs: https://www.koyeb.com/docs

---

**Last Updated**: January 2025
**Research Methodology**: Web search across 12 platforms, pricing verified from official sources
# Template & Boilerplate Evaluation Report
## Rapid Test Site Development for EventMesh

**Research Date:** October 30, 2025
**Purpose:** Identify reusable templates to accelerate test site implementation
**Goal:** Find fastest path to implementation vs build from scratch

---

## Executive Summary

This report evaluates 25+ existing templates, frameworks, and boilerplates across 5 categories to determine the optimal approach for building EventMesh test sites. Key findings:

- **FastAPI Full Stack Template** provides 80% of needed infrastructure (Docker, auth, DB)
- **Faker.js** offers comprehensive test data generation (70+ locales, all data types)
- **Existing test sites** (toscrape.com, httpbin) provide reference implementations
- **Estimated time savings:** 3-5 days by adapting templates vs building from scratch

---

## Category 1: FastAPI Templates & Boilerplates

### 1.1 FastAPI Full Stack Template (Official)
**Repository:** https://github.com/fastapi/full-stack-fastapi-template
**Stars:** 38,700+ ⭐
**Last Updated:** February 2025
**License:** MIT
**Maintenance:** Actively maintained by tiangolo

#### What It Provides Out-of-Box
- FastAPI backend with SQLModel ORM
- React frontend with TypeScript
- PostgreSQL database
- Docker Compose for dev/prod
- JWT authentication + password recovery
- GitHub Actions CI/CD
- Traefik proxy with automatic HTTPS
- Admin dashboard with user management
- Interactive API docs (Swagger/OpenAPI)
- Dark mode support
- Playwright E2E testing

#### Setup Complexity
**Low-Moderate** (1-2 hours)
- Clone/fork repository
- Run `copier copy` for guided setup
- Configure `.env` files
- `docker-compose up` and ready

#### Adaptation Time vs Build Time
- **Adapt:** 4-8 hours (strip frontend, customize models, add test data)
- **Build from scratch:** 2-3 days (setup Docker, DB, auth, docs, testing)
- **Time savings:** 2-2.5 days

#### Fitness for EventMesh Test Sites
**Excellent fit (95%)**

**Direct usage:**
- ✅ E-commerce site (product catalog, auth, checkout)
- ✅ Blog/CMS site (posts, comments, users)
- ✅ REST API test site (all CRUD operations)
- ✅ Authentication test site (JWT, sessions, OAuth ready)

**Requires adaptation:**
- 🔧 Static HTML site (remove React, add Jinja2 templates)
- 🔧 Form-heavy site (add more frontend components)
- 🔧 Pagination test site (add pagination middleware)

**Not suitable:**
- ❌ GraphQL site (needs different stack)
- ❌ WebSocket site (needs additional setup)

#### Recommendation
**PRIMARY TEMPLATE** - Use as foundation for 70% of test sites. Strip React for simple HTML sites, keep full stack for complex scenarios.

---

### 1.2 FastAPI Production Template (zhanymkanov)
**Repository:** https://github.com/zhanymkanov/fastapi_production_template
**Stars:** Not specified
**Last Updated:** Active
**License:** Not specified

#### Key Features
- Optimized Dockerfile (small size, fast builds)
- Gunicorn deployment
- Production-ready configuration
- Non-root user security

#### Fitness for EventMesh
**Good fit (70%)** - Better for production deployment learning but lacks full frontend/auth setup.

**Adaptation time:** 6-10 hours
**Use case:** When teaching deployment/optimization patterns

---

### 1.3 FastAPI + Jinja2 Boilerplates

#### Mateko/FastAPI-boilerplate
**Repository:** https://github.com/Mateko/FastAPI-boilerplate
**Tech Stack:** FastAPI, SQLAlchemy, Jinja2, TailwindCSS

**Fitness:** Excellent for static HTML test sites (90%)
**Adaptation time:** 3-5 hours
**Best for:** Form-heavy sites, pagination examples, traditional web apps

#### tmkontra/fastapi-fullstack-boilerplate
**Repository:** https://github.com/tmkontra/fastapi-fullstack-boilerplate
**Tech Stack:** Flask-Admin, Jinja2 templates

**Fitness:** Good for admin-heavy scenarios (75%)
**Adaptation time:** 4-6 hours

---

### 1.4 Cookiecutter Templates

Multiple cookiecutter-fastapi templates available:

1. **arthurhenrique/cookiecutter-fastapi** - ML focus, uv, GitHub Actions
2. **Tobi-De/cookiecutter-fastapi** - Production-ready, Django-inspired
3. **Buuntu/fastapi-react** - FastAPI + React + PostgreSQL

**Fitness:** Moderate (60%) - Great for new projects, overkill for test sites
**Adaptation time:** 8-12 hours (more customization needed)

---

## Category 2: Test Site Generators & Fixtures

### 2.1 Existing Test Sites (Reference Implementations)

#### toscrape.com Ecosystem
**Website:** https://toscrape.com
**License:** Free to scrape

##### quotes.toscrape.com
- Quotes from famous people
- Multiple variations (JavaScript rendering, infinite scroll, login)
- 100+ example scrapers on GitHub

##### books.toscrape.com
- Fictional bookstore
- 1,000 books with ratings, prices, categories
- Pagination, search, filtering
- Static HTML (perfect for learning)

**Fitness for EventMesh:** Reference implementation (100%)
**Use case:** Study pagination, filtering, data structure patterns
**Time savings:** 4-6 hours understanding best practices

#### scrapinghub/sample-projects
**Repository:** https://github.com/scrapinghub/sample-projects
**Content:** Multiple scraping examples (CSS, XPath, Selenium, AJAX)

**Fitness:** Excellent reference (90%)
**Adaptation time:** Use patterns directly, 2-3 hours

---

### 2.2 HTTP Testing Services

#### httpbin.org
**Repository:** https://github.com/postmanlabs/httpbin
**Docker:** `docker run -p 80:80 kennethreitz/httpbin`
**License:** MIT

**What it provides:**
- HTTP request/response testing
- Status codes, headers, redirects
- Auth testing (Basic, Digest, Bearer)
- Request inspection endpoints
- Data formats (JSON, XML, HTML)

**Fitness:** Excellent for API testing scenarios (95%)
**Deployment time:** 5 minutes (docker-compose)
**Customization:** Minimal needed, use as-is

#### JSONPlaceholder
**Repository:** https://github.com/typicode/jsonplaceholder
**Website:** https://jsonplaceholder.typicode.com
**Powered by:** json-server

**What it provides:**
- 6 resources (posts, comments, albums, photos, todos, users)
- Relational data
- Full REST API
- 3 billion requests/month (proven reliability)

**Fitness:** Perfect for REST API examples (100%)
**Setup time:** 30 seconds with json-server
**Customization:** 1-2 hours to add custom resources

---

## Category 3: Docker Compose Test Environments

### 3.1 General Patterns

**Common Stack Components:**
- PostgreSQL/MySQL databases
- Redis for caching
- Message queues (RabbitMQ, Kafka)
- Mockserver for API mocking
- Nginx/Traefik reverse proxy

**Best Resources:**
- Testcontainers patterns
- Skyramp for microservices testing
- Docker Compose templates in FastAPI Full Stack

**Fitness:** Excellent foundation (90%)
**Setup time:** 2-4 hours for multi-service environment
**Benefit:** Reproducible test environments

---

## Category 4: Faker & Data Generation

### 4.1 Faker.js (JavaScript/TypeScript)
**Repository:** https://github.com/faker-js/faker
**Stars:** 14,600+ ⭐
**Last Updated:** October 2025
**License:** MIT

#### Capabilities
- **70+ locales** (realistic international data)
- **Data categories:**
  - Person (names, gender, job titles)
  - Address (street, city, country, coordinates)
  - Commerce (products, prices, departments)
  - Company (name, catchphrase, BS)
  - Date/Time (past, future, recent)
  - Finance (account, credit card, crypto)
  - Internet (email, URL, username, IP)
  - Lorem (paragraphs, sentences, words)
  - Phone, Color, Image, Database, etc.

#### Integration Ease
**Very Easy** (30 minutes)
```javascript
import { faker } from '@faker-js/faker';

// Generate single user
const user = {
  id: faker.string.uuid(),
  name: faker.person.fullName(),
  email: faker.internet.email(),
  avatar: faker.image.avatar(),
  birthdate: faker.date.birthdate(),
};

// Generate 1000 products
const products = faker.helpers.multiple(createProduct, { count: 1000 });
```

**Fitness:** Perfect for all test sites (100%)
**Setup time:** 30 minutes
**Seeding time:** 1-2 hours for complete dataset

---

### 4.2 Faker (Python)
**Repository:** https://github.com/joke2k/faker
**Pytest plugin:** Built-in `faker` fixture

#### Use Cases
- Database seeding
- API fixtures
- Testing data
- Mock data for scrapers

**Fitness:** Excellent for FastAPI backends (100%)
**Integration time:** 1 hour

---

### 4.3 Specialized Generators

#### Cambalab/fake-data-generator
**Repository:** https://github.com/Cambalab/fake-data-generator
**Purpose:** JSON model-driven fake data

**Use case:** Complex relational data
**Setup time:** 45 minutes

---

## Category 5: Crawler Test Suites & Examples

### 5.1 Scrapy Fixtures

#### scrapy-autounit
**Repository:** https://github.com/scrapinghub/scrapy-autounit
**Stars:** 57
**Maintenance:** Last updated July 2021 (⚠️ not actively maintained)
**License:** BSD-3-Clause

**What it does:**
- Automatically generates test fixtures during spider execution
- Creates `.bin` cassette files (request/response pairs)
- Generates unittest test cases
- Regression testing for spiders

**Integration:**
```python
# settings.py
SPIDER_MIDDLEWARES = {
    'scrapy_autounit.AutounitMiddleware': 950,
}
AUTOUNIT_ENABLED = True
```

**Fitness:** Good for Scrapy-specific testing (75%)
**Caveat:** Unmaintained - consider alternatives
**Setup time:** 1 hour
**Alternative:** scrapy-mock (more recent)

---

#### scrapy-mock
**Repository:** https://github.com/tcurvelo/scrapy-mock
**Purpose:** Record/replay Scrapy responses as fixtures

**Fitness:** Better maintained alternative (80%)
**Setup time:** 1 hour

---

### 5.2 Playwright Test Sites

#### microsoft/playwright-examples
**Repository:** https://github.com/microsoft/playwright-examples
**Official:** Microsoft-maintained

**What it includes:**
- Browser automation examples
- Testing patterns
- CI/CD integration (GitHub Actions)
- Multiple framework examples

**Fitness:** Excellent for browser testing scenarios (90%)
**Learning time:** 2-3 hours
**Adaptation:** Use patterns for test site validation

---

#### awesome-playwright
**Repository:** https://github.com/mxschmitt/awesome-playwright
**Curator:** Max Schmitt (Playwright team)

**Content:**
- Curated tools and utils
- Community projects
- Testing frameworks
- Integration examples

**Value:** Reference architecture
**Time savings:** 3-4 hours

---

### 5.3 Crawlee Examples

#### apify/crawlee
**Repository:** https://github.com/apify/crawlee
**Stars:** 20,300+ ⭐
**Last Updated:** October 2025
**License:** Apache 2.0

**Supported Crawlers:**
- Puppeteer
- Playwright
- Cheerio (HTTP)
- JSDOM
- Raw HTTP

**Features:**
- URL queue (BFS/DFS)
- Proxy rotation
- Session management
- Auto-scaling
- Error handling/retries

**Fitness:** Excellent validation tool (85%)
**Use case:** Validate test sites work with real crawlers
**Setup time:** 1-2 hours
**Value:** Proof of concept testing

---

### 5.4 Selenium Examples

#### SeleniumBase
**Repository:** https://github.com/seleniumbase/SeleniumBase
**Content:** 200+ examples

**Features:**
- Bot detection bypass
- CAPTCHA handling
- Stealth mode

**Fitness:** Good for anti-scraping test scenarios (80%)
**Setup time:** 2 hours

---

## Comparative Analysis Matrix

| Template/Tool | Stars | Maintenance | Setup Time | Adapt Time | Fitness | License |
|--------------|-------|-------------|------------|------------|---------|---------|
| **FastAPI Full Stack** | 38.7k | ✅ Active | 1-2h | 4-8h | 95% | MIT |
| **FastAPI+Jinja2 (Mateko)** | - | ✅ Active | 1h | 3-5h | 90% | - |
| **Faker.js** | 14.6k | ✅ Active | 30m | 1-2h | 100% | MIT |
| **Faker (Python)** | - | ✅ Active | 30m | 1h | 100% | - |
| **httpbin** | - | ✅ Active | 5m | 10m | 95% | MIT |
| **JSONPlaceholder** | - | ✅ Active | 30s | 1-2h | 100% | - |
| **scrapy-autounit** | 57 | ⚠️ 2021 | 1h | 2h | 75% | BSD-3 |
| **Crawlee** | 20.3k | ✅ Active | 1-2h | 3-4h | 85% | Apache-2.0 |
| **Playwright Examples** | - | ✅ Active | 2h | 3-4h | 90% | - |
| **toscrape.com** | - | ✅ Active | 0m | 4-6h | 100% | Free |

---

## Time Estimates: Build vs Adapt

### Test Site #1: E-commerce Store
**Requirements:** Products, cart, checkout, auth, search, pagination

#### Build from Scratch
- FastAPI setup: 4 hours
- Database models: 6 hours
- Authentication: 8 hours
- Product catalog: 6 hours
- Cart/checkout: 8 hours
- Frontend templates: 12 hours
- Docker setup: 4 hours
- Test data generation: 6 hours
- Testing: 8 hours
**Total: 62 hours (~8 days)**

#### Adapt FastAPI Full Stack + Faker.js
- Strip React frontend: 2 hours
- Add Jinja2 templates: 4 hours
- Customize models: 3 hours
- Generate test data: 2 hours
- Customize routes: 3 hours
- Testing: 4 hours
**Total: 18 hours (~2.5 days)**

**Time Savings: 44 hours (5.5 days) = 71% faster**

---

### Test Site #2: Blog/CMS Platform
**Requirements:** Posts, comments, authors, tags, search, pagination

#### Build from Scratch
- FastAPI setup: 4 hours
- Database models: 4 hours
- Authentication: 8 hours
- CRUD operations: 8 hours
- Comment system: 6 hours
- Frontend: 10 hours
- Search: 6 hours
- Pagination: 4 hours
- Docker: 4 hours
- Testing: 6 hours
**Total: 60 hours (~7.5 days)**

#### Adapt FastAPI Full Stack + Faker.js
- Customize user model: 2 hours
- Add post/comment models: 3 hours
- Adapt frontend: 4 hours
- Generate content: 2 hours
- Add search: 3 hours
- Pagination: 2 hours
- Testing: 3 hours
**Total: 19 hours (~2.5 days)**

**Time Savings: 41 hours (5 days) = 68% faster**

---

### Test Site #3: REST API Test Service
**Requirements:** Multiple endpoints, auth, data formats, error scenarios

#### Build from Scratch
- FastAPI setup: 4 hours
- All CRUD endpoints: 10 hours
- Auth endpoints: 6 hours
- Error handling: 4 hours
- Data formats: 4 hours
- Documentation: 4 hours
- Testing: 6 hours
**Total: 38 hours (~5 days)**

#### Use httpbin + JSONPlaceholder + Custom FastAPI
- Deploy httpbin: 10 minutes
- Deploy JSONPlaceholder: 10 minutes
- Add custom endpoints: 4 hours
- Integrate: 2 hours
- Documentation: 2 hours
- Testing: 2 hours
**Total: 10.5 hours (~1.5 days)**

**Time Savings: 27.5 hours (3.5 days) = 72% faster**

---

### Test Site #4: Static HTML Site (Forms, Tables)
**Requirements:** Multiple pages, forms, tables, no auth

#### Build from Scratch
- FastAPI setup: 4 hours
- Jinja2 templates: 8 hours
- Form handling: 6 hours
- Table rendering: 4 hours
- Pagination: 3 hours
- CSS/styling: 6 hours
- Data generation: 4 hours
- Testing: 4 hours
**Total: 39 hours (~5 days)**

#### Adapt FastAPI+Jinja2 Template + Faker.js
- Strip unnecessary features: 1 hour
- Customize templates: 4 hours
- Add form routes: 2 hours
- Generate table data: 2 hours
- Styling: 3 hours
- Testing: 2 hours
**Total: 14 hours (~2 days)**

**Time Savings: 25 hours (3 days) = 64% faster**

---

## Recommended Template Stack by Use Case

### Use Case 1: Full-Featured E-commerce/SaaS
**Primary Template:** FastAPI Full Stack Template
**Add-ons:** Faker.js for products, stripe-mock for payments
**Estimated setup:** 2-3 days
**Coverage:** Products, auth, checkout, admin

### Use Case 2: Traditional Web App (Forms/Tables)
**Primary Template:** Mateko/FastAPI-boilerplate (Jinja2)
**Add-ons:** Faker.js for data
**Estimated setup:** 1.5-2 days
**Coverage:** Forms, tables, pagination, search

### Use Case 3: REST API Testing
**Primary Templates:** httpbin + JSONPlaceholder
**Add-ons:** FastAPI for custom endpoints
**Estimated setup:** 1 day
**Coverage:** All HTTP methods, auth, errors

### Use Case 4: Blog/CMS Platform
**Primary Template:** FastAPI Full Stack Template
**Modifications:** Remove e-commerce, add blog models
**Add-ons:** Faker.js for posts/comments
**Estimated setup:** 2 days
**Coverage:** Posts, comments, authors, tags

### Use Case 5: Authentication Testing
**Primary Template:** FastAPI Full Stack Template
**Focus:** Keep only auth features
**Add-ons:** OAuth providers, JWT variations
**Estimated setup:** 1.5 days
**Coverage:** JWT, OAuth, sessions, 2FA

### Use Case 6: GraphQL API
**Primary Template:** Build custom (no good templates)
**Framework:** Strawberry GraphQL + FastAPI
**Estimated setup:** 3-4 days
**Coverage:** Queries, mutations, subscriptions

### Use Case 7: WebSocket Testing
**Primary Template:** FastAPI base + Socket.IO
**Reference:** FastAPI WebSocket docs
**Estimated setup:** 2-3 days
**Coverage:** Real-time updates, chat

### Use Case 8: Microservices Ecosystem
**Primary Template:** Docker Compose microservices template
**Add-ons:** Multiple FastAPI services + shared DB
**Estimated setup:** 4-5 days
**Coverage:** Service discovery, API gateway

---

## Licensing Summary

All recommended templates use permissive licenses:

| Template | License | Commercial Use | Attribution Required |
|----------|---------|----------------|---------------------|
| FastAPI Full Stack | MIT | ✅ Yes | ✅ Yes |
| Faker.js | MIT | ✅ Yes | ✅ Yes |
| httpbin | MIT | ✅ Yes | ✅ Yes |
| Crawlee | Apache-2.0 | ✅ Yes | ✅ Yes |
| scrapy-autounit | BSD-3-Clause | ✅ Yes | ✅ Yes |
| JSONPlaceholder | MIT | ✅ Yes | ✅ Yes |

**All templates are safe for:**
- Commercial use
- Modification
- Distribution
- Private use

**Requirements:**
- Include original license
- State changes (for some)
- Provide attribution

---

## Implementation Recommendations

### Phase 1: Foundation (Week 1)
1. **Set up FastAPI Full Stack Template**
   - Clone and customize for EventMesh branding
   - Configure Docker Compose
   - Set up PostgreSQL with test schema
   - Deploy locally and verify

2. **Integrate Faker.js + Python Faker**
   - Create seeding scripts
   - Generate realistic test data
   - Seed database with 10k+ records

3. **Deploy httpbin + JSONPlaceholder**
   - Add to Docker Compose
   - Verify API endpoints
   - Document available resources

### Phase 2: Customization (Week 2)
4. **Create Test Site Variations**
   - E-commerce variant (keep full stack)
   - Blog variant (modify models)
   - Static HTML variant (add Jinja2)
   - Forms variant (heavy forms)

5. **Add EventMesh-Specific Features**
   - Custom spider endpoints
   - Crawl tracking
   - Rate limiting examples
   - Robot.txt variations

### Phase 3: Validation (Week 3)
6. **Test with Real Crawlers**
   - Crawlee validation
   - Playwright E2E tests
   - Selenium compatibility
   - Performance testing

7. **Documentation**
   - API documentation
   - Scraping guidelines
   - Setup instructions
   - Example scraper code

### Phase 4: Advanced Sites (Week 4)
8. **Build Complex Scenarios**
   - GraphQL API (custom build)
   - WebSocket site (FastAPI + Socket.IO)
   - Authentication variations
   - Anti-scraping challenges

---

## Critical Path Decision Tree

```
Need test site?
├─ REST API only?
│  ├─ Standard resources? → Use JSONPlaceholder (30s setup)
│  └─ Custom logic? → Use httpbin + FastAPI (1 day)
│
├─ Traditional web app?
│  ├─ With auth/database? → FastAPI Full Stack (2-3 days)
│  └─ Simple forms/tables? → FastAPI+Jinja2 template (1-2 days)
│
├─ E-commerce/SaaS?
│  └─ FastAPI Full Stack + Faker.js (2-3 days)
│
├─ Real-time/WebSocket?
│  └─ Custom FastAPI + Socket.IO (2-3 days)
│
└─ GraphQL?
   └─ Strawberry + FastAPI (3-4 days)
```

---

## Risk Assessment

### Low Risk ✅
- **FastAPI Full Stack Template:** Proven, 38k stars, active maintenance
- **Faker.js:** Industry standard, 14k stars
- **httpbin:** Widely used, Postman-maintained
- **JSONPlaceholder:** 3B requests/month, proven reliability

### Moderate Risk ⚠️
- **scrapy-autounit:** Unmaintained since 2021 (use scrapy-mock instead)
- **Cookiecutter templates:** Varying quality, check each individually
- **Custom Jinja2 templates:** Less documented than React templates

### High Risk ❌
- **Building from scratch:** Time overruns, scope creep
- **Outdated templates:** Security vulnerabilities, deprecated dependencies
- **Unmaintained tools:** Breaking changes in dependencies

---

## Final Recommendations

### DO ✅
1. **Use FastAPI Full Stack as primary foundation** (saves 2-3 days per site)
2. **Integrate Faker.js/Python Faker immediately** (eliminates manual data creation)
3. **Deploy httpbin + JSONPlaceholder** for instant API testing (5 min setup)
4. **Reference toscrape.com** for best practices (saves 4-6 hours)
5. **Use Docker Compose** for all environments (reproducibility)

### DON'T ❌
1. **Build authentication from scratch** (FastAPI template has it ready)
2. **Manually create test data** (Faker.js automates this)
3. **Use unmaintained templates** (scrapy-autounit → scrapy-mock)
4. **Skip Docker** (environment reproducibility is critical)
5. **Ignore existing test sites** (toscrape.com is perfect reference)

### MAYBE 🤔
1. **Cookiecutter templates:** Evaluate per-project
2. **Custom GraphQL:** Only if specifically needed
3. **WebSocket sites:** Build if real-time testing required
4. **Microservices:** Only for distributed system testing

---

## Conclusion

**Fastest implementation path:**

1. **Week 1:** Deploy FastAPI Full Stack + Faker.js + httpbin/JSONPlaceholder
2. **Week 2:** Create 4 site variants (e-commerce, blog, static, forms)
3. **Week 3:** Validate with Crawlee/Playwright, add documentation
4. **Week 4:** Advanced scenarios (GraphQL, WebSocket, anti-scraping)

**Total time:** 4 weeks for comprehensive test site ecosystem

**Time savings vs building from scratch:** 8-12 weeks → **66-75% faster**

**Return on investment:**
- Development: -50 hours (saved)
- Testing: -20 hours (automated)
- Maintenance: -30 hours/year (template updates)
- Documentation: -15 hours (reference implementations)

**Total ROI:** ~115 hours saved = 2.9 weeks of developer time

---

## Next Steps

1. **Immediate:** Clone FastAPI Full Stack Template and deploy locally
2. **Day 1:** Integrate Faker.js and generate seed data
3. **Day 2:** Deploy httpbin + JSONPlaceholder in Docker Compose
4. **Week 1:** Create first site variant (e-commerce)
5. **Week 2:** Validate with Crawlee and document findings

---

## Appendix: Quick Reference Links

### Primary Templates
- FastAPI Full Stack: https://github.com/fastapi/full-stack-fastapi-template
- FastAPI+Jinja2: https://github.com/Mateko/FastAPI-boilerplate
- httpbin: https://github.com/postmanlabs/httpbin
- JSONPlaceholder: https://github.com/typicode/jsonplaceholder

### Data Generation
- Faker.js: https://github.com/faker-js/faker
- Python Faker: https://github.com/joke2k/faker
- json-server: https://github.com/typicode/json-server

### Testing Tools
- Crawlee: https://github.com/apify/crawlee
- Playwright Examples: https://github.com/microsoft/playwright-examples
- scrapy-mock: https://github.com/tcurvelo/scrapy-mock
- SeleniumBase: https://github.com/seleniumbase/SeleniumBase

### Reference Sites
- toscrape.com: https://toscrape.com
- books.toscrape.com: https://books.toscrape.com
- quotes.toscrape.com: https://quotes.toscrape.com

### Documentation
- FastAPI Docs: https://fastapi.tiangolo.com
- Faker.js Docs: https://fakerjs.dev
- Crawlee Docs: https://crawlee.dev
- Playwright Docs: https://playwright.dev

---

**Report Compiled By:** Research Agent
**For:** EventMesh Test Site Development
**Confidence Level:** High (25+ sources evaluated)
**Recommendation Confidence:** 95% (templates are proven, actively maintained)


---
# Appendix: Consolidated Research

The sections above incorporate research from hosting provider comparison and template evaluation studies.
