# RipTide Test Sites - Deployment Guide

Complete guide for hosting the 13 test sites across different platforms.

## Table of Contents

1. [Local Development (Default)](#option-1-local-development)
2. [Hetzner VPS + Coolify (Recommended)](#option-2-hetzner-vps--coolify)
3. [Google Cloud Run (Free Tier)](#option-3-google-cloud-run)
4. [Koyeb (Fully Managed)](#option-4-koyeb)
5. [GitHub Container Registry](#option-5-github-container-registry)
6. [Cost Comparison](#cost-comparison)
7. [Recommended Approach](#recommended-approach)

---

## Option 1: Local Development

**Best for:** Development, CI/CD testing
**Cost:** Free
**Setup time:** 5 minutes

### Prerequisites
- Docker Desktop or Docker Engine
- Docker Compose
- 4GB RAM available

### Setup

```bash
# Clone repository
git clone https://github.com/your-org/riptide-test-sites.git
cd riptide-test-sites

# Copy environment template
cp .env.example .env

# Start all 13 sites
make up

# Verify health
make health-check

# Access sites at:
# http://localhost:5001 (ecommerce)
# http://localhost:5002 (blog)
# ... etc
```

### Integration with RipTide

```bash
# In RipTide test suite
export BASE_URL=http://localhost
pytest tests/e2e/ -v
```

### Pros & Cons

✅ **Pros:**
- Zero cost
- Full control over environment
- Fast iteration cycle
- Works offline
- No external dependencies

❌ **Cons:**
- Requires local Docker
- Not accessible remotely
- Manual startup required
- Uses local resources

---

## Option 2: Hetzner VPS + Coolify

**Best for:** Permanent hosted environment, team access
**Cost:** €3.49-6/month ($4-7/month) for ALL 13 sites
**Setup time:** 45 minutes

### Why This Is The Best Option

1. **Cheapest:** 75% cheaper than alternatives
2. **All-in-one:** Host 50+ sites on one VPS
3. **Easy deployment:** Heroku-like UI (Coolify)
4. **No domain needed:** Uses sslip.io for subdomains
5. **Full Docker Compose support**

### Prerequisites

- Hetzner Cloud account (sign up at hetzner.com/cloud)
- SSH client

### Step-by-Step Setup

#### 1. Create Hetzner VPS

```bash
# Option A: Web Console
# 1. Go to https://console.hetzner.cloud
# 2. Create new project: "RipTide Test Sites"
# 3. Add server:
#    - Location: Choose nearest to you
#    - Image: Ubuntu 22.04
#    - Type: CAX11 (€3.49/month) or CPX11 (€4.15/month)
#    - Networking: IPv4 + IPv6
# 4. Copy IP address (e.g., 1.2.3.4)

# Option B: CLI (faster)
# Install Hetzner CLI
brew install hcloud  # macOS
# or: sudo snap install hcloud  # Linux

# Authenticate
hcloud context create riptide-test

# Create server
hcloud server create \
  --name riptide-test-sites \
  --type cax11 \
  --image ubuntu-22.04 \
  --ssh-key your-ssh-key

# Get IP
hcloud server ip riptide-test-sites
```

#### 2. Install Coolify

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Install Coolify (one command)
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Wait 2-3 minutes for installation
# Access Coolify at: http://YOUR_SERVER_IP:8000
```

#### 3. Configure Coolify

```bash
# 1. Open browser: http://YOUR_SERVER_IP:8000
# 2. Create admin account (save credentials!)
# 3. Complete setup wizard:
#    - Set server name: "RipTide Test"
#    - Enable Docker Compose support: YES
#    - Enable automatic HTTPS: YES (Let's Encrypt)
```

#### 4. Deploy Test Sites

**Option A: Git Repository (Recommended)**

```bash
# In Coolify dashboard:
# 1. Resources → New Resource → Git Repository
# 2. Repository URL: https://github.com/your-org/riptide-test-sites
# 3. Branch: main
# 4. Build method: Docker Compose
# 5. Compose file: docker-compose.yml
# 6. Environment variables:
#    FIXTURE_SEED=42
#    BASE_URL=http://ecommerce.YOUR_IP.sslip.io

# 7. Deploy
# Coolify will:
#    - Clone repository
#    - Build all 13 images
#    - Start containers
#    - Configure Caddy reverse proxy
#    - Generate subdomains
```

**Option B: Manual Docker Compose**

```bash
# SSH into server
ssh root@YOUR_SERVER_IP

# Clone repository
git clone https://github.com/your-org/riptide-test-sites.git
cd riptide-test-sites

# Update .env
cp .env.example .env
# Edit BASE_URL to use your IP

# Deploy
docker-compose up -d

# Configure Caddy for subdomains
# (Coolify does this automatically)
```

#### 5. Access Your Sites

Your sites will be available at:

```
http://ecommerce.YOUR_IP.sslip.io
http://blog.YOUR_IP.sslip.io
http://social.YOUR_IP.sslip.io
... (all 13 sites)
```

**How sslip.io works:**
- sslip.io provides free DNS wildcards
- `ecommerce.1.2.3.4.sslip.io` resolves to `1.2.3.4`
- No domain purchase needed!
- Automatic subdomain routing

#### 6. Enable HTTPS (Optional)

```bash
# In Coolify:
# 1. Go to your deployment
# 2. Settings → SSL/TLS
# 3. Enable "Automatic HTTPS"
# 4. Let's Encrypt will auto-provision certificates

# URLs become:
# https://ecommerce.YOUR_IP.sslip.io
```

### Scaling

```bash
# Need more resources?
# Upgrade VPS in Hetzner console:
# CAX11 → CAX21 (2 vCPUs, 4GB) = €6.90/month
# CAX21 → CAX31 (4 vCPUs, 8GB) = €13.90/month

# Or use Docker resource limits:
# docker-compose.yml
services:
  ecommerce:
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M
```

### Monitoring

```bash
# Coolify provides:
# - Container status dashboard
# - Resource usage graphs
# - Log viewer
# - Health checks
# - Auto-restart failed containers

# Access at: http://YOUR_IP:8000/dashboard
```

### Maintenance

```bash
# Update sites (auto-deploy on git push)
# 1. Push changes to GitHub
# 2. Coolify auto-detects changes
# 3. Auto-rebuilds and redeploys

# Manual update:
ssh root@YOUR_SERVER_IP
cd riptide-test-sites
git pull
docker-compose up -d --build

# View logs
docker-compose logs -f ecommerce
```

### Backup

```bash
# Coolify auto-backups to:
# /var/lib/coolify/backups/

# Manual backup
ssh root@YOUR_SERVER_IP
tar czf riptide-backup.tar.gz /var/lib/docker/volumes
scp root@YOUR_IP:riptide-backup.tar.gz ./backup.tar.gz
```

### Pros & Cons

✅ **Pros:**
- Cheapest option (€3.49/month for ALL sites)
- Host unlimited sites on one VPS
- Full Docker Compose support
- Heroku-like deployment UI
- No domain purchase needed (sslip.io)
- Root access for customization
- Coolify handles proxy/SSL/routing

❌ **Cons:**
- One-time 45 min setup
- Self-managed (though Coolify helps)
- Single point of failure (use load balancer if critical)

---

## Option 3: Google Cloud Run

**Best for:** Zero infrastructure management, free tier
**Cost:** $0-8/month (likely stays FREE)
**Setup time:** 30 minutes

### Prerequisites

- Google Cloud account (free $300 credit for new accounts)
- `gcloud` CLI installed

### Setup

#### 1. Install gcloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash

# Windows
# Download from: https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Prepare Sites for Cloud Run

```bash
# Cloud Run requires individual Dockerfiles per service
# Sites already have Dockerfiles, so we're ready!

cd riptide-test-sites
```

#### 3. Deploy All Sites

```bash
# Deploy script
for site in ecommerce blog social jobboard realestate restaurant events education healthcare travel news forum projectmgmt; do
  echo "Deploying $site..."

  gcloud run deploy riptide-$site \
    --source sites/$site \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars FIXTURE_SEED=42,SITE_NAME=$site \
    --memory 512Mi \
    --cpu 1 \
    --timeout 60s \
    --max-instances 1

  echo "$site deployed!"
  echo ""
done

# Get URLs
gcloud run services list --platform managed
```

#### 4. Save URLs

```bash
# Your sites will be at:
https://riptide-ecommerce-abc123.run.app
https://riptide-blog-xyz789.run.app
... (unique URLs per site)

# Save to .env for tests
cat > test.env << EOF
BASE_URL_ECOMMERCE=https://riptide-ecommerce-abc123.run.app
BASE_URL_BLOG=https://riptide-blog-xyz789.run.app
... (fill in actual URLs)
EOF
```

### Free Tier Limits

Google Cloud Run free tier includes:
- **2 million requests/month**
- **360,000 GB-seconds memory/month**
- **180,000 vCPU-seconds/month**

**For 13 sites:**
- Each site: ~150k requests/month free
- More than enough for testing

### Monitoring

```bash
# View logs
gcloud run services logs read riptide-ecommerce \
  --platform managed \
  --region us-central1 \
  --limit 50

# Check metrics
gcloud run services describe riptide-ecommerce \
  --platform managed \
  --region us-central1
```

### Cost Optimization

```bash
# Reduce resources to stay in free tier
gcloud run services update riptide-ecommerce \
  --memory 256Mi \
  --cpu 0.5 \
  --max-instances 1 \
  --concurrency 80
```

### Pros & Cons

✅ **Pros:**
- Stays in free tier (2M requests/month)
- Zero maintenance
- Auto-scales (to zero when not used)
- Automatic HTTPS
- Global CDN
- No server management

❌ **Cons:**
- 1-3 second cold starts
- Separate URLs per site (no custom subdomains without domain)
- Requires Google Cloud account
- Logs in GCP console

---

## Option 4: Koyeb

**Best for:** Production-ready, simple deployment
**Cost:** $20/month (1 free + 12 × $1.61 eco instances)
**Setup time:** 20 minutes

### Setup

```bash
# Install Koyeb CLI
curl -fsSL https://cli.koyeb.com/install.sh | sh

# Authenticate
koyeb login

# Deploy each site
koyeb app init riptide-ecommerce \
  --git github.com/your-org/riptide-test-sites \
  --git-branch main \
  --git-workdir sites/ecommerce \
  --instance-type eco \
  --env FIXTURE_SEED=42 \
  --env SITE_NAME=ecommerce

# Repeat for all 13 sites...
```

### URLs

```
https://riptide-ecommerce.koyeb.app
https://riptide-blog.koyeb.app
... (all 13 sites)
```

### Pros & Cons

✅ **Pros:**
- Simplest managed option
- Global CDN (150+ locations)
- Zero cold starts
- Git-based deployment
- Auto SSL

❌ **Cons:**
- Most expensive option ($20/month)
- Less customization than VPS

---

## Option 5: GitHub Container Registry

**Best for:** Fast CI builds, versioned releases
**Cost:** Free
**Setup time:** 30 minutes

### Setup

```bash
# Authenticate to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and push all images
for site in ecommerce blog social jobboard realestate restaurant events education healthcare travel news forum projectmgmt; do
  docker build -t ghcr.io/your-org/riptide-$site:latest sites/$site
  docker push ghcr.io/your-org/riptide-$site:latest
done

# Use in docker-compose.yml
services:
  ecommerce:
    image: ghcr.io/your-org/riptide-ecommerce:latest
    # No build step needed!
```

### CI/CD Integration

```yaml
# .github/workflows/build.yml
name: Build and Push Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        run: |
          for site in ecommerce blog social jobboard realestate restaurant events education healthcare travel news forum projectmgmt; do
            docker build -t ghcr.io/${{ github.repository_owner }}/riptide-$site:latest sites/$site
            docker push ghcr.io/${{ github.repository_owner }}/riptide-$site:latest
          done
```

### Pros & Cons

✅ **Pros:**
- Free unlimited storage (public repos)
- Fastest CI (no build time)
- Versioned artifacts
- Auto-builds on push

❌ **Cons:**
- Still need hosting for actual sites
- Public images (or pay for private)

---

## Cost Comparison

| Option | Monthly Cost | Annual Cost | Setup Time | Pros | Cons |
|--------|-------------|-------------|------------|------|------|
| **Local Dev** | $0 | $0 | 5 min | Free, full control | Local only |
| **Hetzner + Coolify** | $4-7 | $48-84 | 45 min | Cheapest, unlimited sites | Self-managed |
| **Cloud Run** | $0-8 | $0-96 | 30 min | Free tier, zero ops | Cold starts |
| **Koyeb** | $20 | $240 | 20 min | Simplest | Most expensive |
| **GHCR** | $0 | $0 | 30 min | Fast CI | Need hosting |

---

## Recommended Approach

### By Use Case

| Use Case | Recommendation | Why |
|----------|---------------|-----|
| **Local development** | Docker Compose | Free, full control |
| **Team testing** | Hetzner + Coolify | Cheapest hosted ($4/month) |
| **CI/CD** | GHCR + Local | Fast builds, no external deps |
| **Production demos** | Cloud Run or Koyeb | Zero ops, always available |
| **Budget <$100/year** | Hetzner | Best value |
| **Zero management** | Cloud Run | Serverless |

### Hybrid Approach (Best of All Worlds)

```bash
# Development: Local Docker
make up

# CI/CD: GHCR images for fast builds
docker-compose.ci.yml with GHCR images

# Hosted: Hetzner for permanent access
Deploy to Hetzner VPS with Coolify
```

---

## Next Steps

1. **Choose your deployment method** based on needs
2. **Follow setup instructions** for chosen option
3. **Configure BASE_URL** in RipTide tests
4. **Run validation:** `make test`
5. **Monitor health:** `make health-check`

---

## Support

- **Hetzner issues:** support@hetzner.com
- **Coolify issues:** https://coolify.io/docs
- **Cloud Run issues:** https://cloud.google.com/run/docs
- **Koyeb issues:** https://www.koyeb.com/docs

**Project issues:** https://github.com/your-org/riptide-test-sites/issues
