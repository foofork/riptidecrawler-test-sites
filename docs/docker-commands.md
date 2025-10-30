# Docker Management Commands

## Start Services
```bash
docker-compose up -d --build
```

## Stop Services
```bash
docker-compose down
```

## View Running Containers
```bash
docker-compose ps
```

## View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f happy-path

# Last 50 lines
docker-compose logs --tail=50
```

## Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart happy-path
```

## Rebuild Specific Service
```bash
docker-compose up -d --build happy-path
```

## Check Container Health
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## Execute Command in Container
```bash
docker exec -it riptide-happy-path /bin/bash
```

## View Resource Usage
```bash
docker stats
```

## Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes as well
docker-compose down -v

# Remove all unused images
docker image prune -a
```

## Test All Endpoints
```bash
for port in {5001..5013}; do
  echo "Port $port:"
  curl -s http://localhost:$port/health || curl -s http://localhost:$port/ | head -5
  echo ""
done
```

## Quick Health Check
```bash
# Check all running containers
docker ps | grep riptide | wc -l

# Should return: 13
```
