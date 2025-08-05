# Personal AI Assistant - Docker Infrastructure

## 🐳 Docker Infrastructure Setup Complete!

This document explains the complete Docker infrastructure setup for the Personal AI Assistant project.

## 📋 What's Included

### Core Services
- **PostgreSQL 15** - Main database with extensions and custom types
- **Redis 7** - Caching and session management
- **Qdrant** - Vector database for AI embeddings
- **Ollama** - Local LLM inference server
- **Nginx** - Reverse proxy and load balancer
- **Backend** - FastAPI application (to be built)

### Development Tools
- **Adminer** - Database administration UI
- **Redis Commander** - Redis administration UI
- **MailHog** - Email testing tool

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Clone the repository (or create the structure)
# Copy environment configuration
cp .env.example .env

# Edit .env with your settings
nano .env

# Start development environment
make dev
```

### 2. Complete Setup (First Time)
```bash
# Run complete setup (includes model downloads)
make setup-complete
```

### 3. Daily Development
```bash
# Start services
make dev

# View logs
make logs

# Run tests (when backend is built)
make test

# Stop services
make dev-down
```

## 🌐 Service URLs (Development)

| Service           | URL                             | Description         |
|-------------------|---------------------------------|---------------------|
| Backend API       | http://localhost:8000           | FastAPI application |
| API Documentation | http://localhost:8000/docs      | Swagger UI          |
| Database Admin    | http://localhost:8080           | Adminer interface   |
| Redis Admin       | http://localhost:8081           | Redis Commander     |
| Mail Testing      | http://localhost:8025           | MailHog interface   |
| Qdrant Dashboard  | http://localhost:6333/dashboard | Vector DB admin     |

## 📁 File Structure

```
personal-ai-assistant/
├── docker-compose.yml           # Production configuration
├── docker-compose.dev.yml       # Development overrides
├── .env.example                 # Environment template
├── Makefile                     # Development commands
├── .gitignore                   # Git ignore rules
└── docker/
    ├── postgres/
    │   ├── init.sql            # Database initialization
    │   └── dev-seed.sql        # Development seed data
    ├── redis/
    │   ├── redis.conf          # Production Redis config
    │   └── redis-dev.conf      # Development Redis config
    ├── nginx/
    │   └── nginx.conf          # Nginx configuration
    ├── ollama/
    │   └── entrypoint-dev.sh   # Ollama setup script
    └── scripts/
        ├── entrypoint.sh       # Backend container entrypoint
        └── healthcheck.sh      # Health monitoring script
```

## ⚙️ Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Core Settings
ENVIRONMENT=development
SECRET_KEY=your-secret-key
DEBUG=true

# Database
POSTGRES_PASSWORD=dev_password
DATABASE_URL=postgresql+asyncpg://assistant:dev_password@localhost:5432/assistant

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Models
OLLAMA_MODELS=llama3.2:3b,phi3:mini,codellama:7b

# Google OAuth (for future weeks)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Service Configuration

#### PostgreSQL
- **Database**: `assistant`
- **User**: `assistant`
- **Extensions**: `uuid-ossp`, `pgcrypto`, `pg_trgm`, `btree_gin`
- **Custom Types**: `user_role`, `account_provider`, `conversation_status`, etc.
- **Functions**: `health_check()`, `update_updated_at_column()`, `generate_short_id()`

#### Redis
- **Production**: Persistent with security restrictions
- **Development**: No persistence, verbose logging
- **Memory Limit**: 256MB (production), 128MB (development)
- **Eviction Policy**: allkeys-lru (production), noeviction (development)

#### Qdrant
- **Port**: 6333 (HTTP), 6334 (gRPC)
- **Storage**: Persistent volumes
- **Web UI**: Available at port 6333

#### Ollama
- **Models**: Automatically downloads specified models
- **API**: http://localhost:11434
- **GPU Support**: Available (uncomment in docker-compose.yml)

## 🛠️ Development Commands

### Basic Operations
```bash
make dev            # Start development environment
make dev-build      # Build and start (fresh build)
make dev-down       # Stop development environment
make dev-clean      # Stop and remove volumes
```

### Database Operations
```bash
make migrate        # Run database migrations
make migrate-create MESSAGE="description"  # Create new migration
make migrate-rollback  # Rollback last migration
make seed          # Seed with development data
make db-reset      # Reset database (WARNING: destroys data)
```

### Testing
```bash
make test          # Run all tests
make test-unit     # Unit tests only
make test-integration  # Integration tests only
make test-e2e      # End-to-end tests
make test-watch    # Tests in watch mode
```

### Code Quality
```bash
make lint          # Run linting checks
make format        # Format code
make security      # Security checks
```

### AI Models
```bash
make models-download    # Download Ollama models
make models-list       # List available models
make models-remove MODEL=model-name  # Remove specific model
```

### Monitoring
```bash
make status        # Service status
make health        # Health checks
make stats         # Resource usage
make logs          # All service logs
make logs-backend  # Backend logs only
make logs-db       # Database logs only
```

### Utilities
```bash
make shell         # Backend container shell
make shell-db      # Database shell
make shell-redis   # Redis shell
make backup        # Create database backup
make backup-restore FILE=backup.sql  # Restore from backup
```

## 🔒 Security Features

### Production Security
- **PostgreSQL**: Custom user permissions, dangerous command restrictions
- **Redis**: Command renaming, memory limits, authentication ready
- **Nginx**: Rate limiting, security headers, request size limits
- **Network**: Isolated Docker network, port restrictions

### Development Security
- **Relaxed Settings**: Easier debugging and development
- **No Authentication**: Services accessible without passwords
- **Verbose Logging**: Detailed logs for troubleshooting

## 📊 Health Monitoring

### Automatic Health Checks
All services include health checks:
- **Backend**: HTTP endpoint `/health`
- **Database**: Connection and query tests
- **Redis**: Ping command
- **Qdrant**: HTTP health endpoint
- **Ollama**: Version API check

### Manual Health Check
```bash
# Comprehensive health check
make health

# Individual service checks
./docker/scripts/healthcheck.sh http
./docker/scripts/healthcheck.sh database
./docker/scripts/healthcheck.sh redis
```

## 🚀 Production Deployment

### Build for Production
```bash
# Build production images
make build

# Deploy to production
make deploy

# Update production deployment
make deploy-update
```

### Production Considerations
- Set strong passwords in production `.env`
- Enable SSL/TLS certificates
- Configure external monitoring
- Set up automated backups
- Review security settings

## 🐛 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check if ports are in use
netstat -tulpn | grep :5432
netstat -tulpn | grep :6379
netstat -tulpn | grep :8000

# Check Docker status
docker system info
docker-compose ps

# View service logs
make logs
```

#### Database Connection Issues
```bash
# Test database connection
make shell-db

# Check database status
docker exec ai-assistant-postgres pg_isready -U assistant

# Reset database
make db-reset
```

#### Ollama Model Issues
```bash
# Check available models
make models-list

# Re-download models
make models-download

# Check Ollama logs
docker logs ai-assistant-ollama
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x docker/scripts/*.sh
```

#### Out of Disk Space
```bash
# Clean Docker resources
make clean

# Remove unused volumes
docker volume prune

# Check disk usage
df -h
docker system df
```

### Debug Mode

#### Enable Verbose Logging
```bash
# Edit .env file
LOG_LEVEL=DEBUG
OLLAMA_DEBUG=1

# Restart services
make dev-down && make dev
```

#### Container Debugging
```bash
# Access running containers
make shell          # Backend container
make shell-db       # Database container
make shell-redis    # Redis container

# View container processes
docker exec ai-assistant-backend ps aux
```

### Performance Issues

#### Monitor Resource Usage
```bash
# Container stats
make stats

# Detailed monitoring
docker stats --no-stream
```

#### Optimize for Development
```bash
# Reduce memory usage
# Edit docker-compose.dev.yml
# Reduce Redis maxmemory
# Limit Ollama models
```

## 📈 Monitoring & Observability

### Built-in Monitoring

#### Health Endpoints
- Backend: `GET /health`
- Database: Custom health_check() function
- Redis: PING command
- Qdrant: `GET /health`

#### Log Aggregation
```bash
# Real-time logs
make logs

# Service-specific logs
make logs-backend
make logs-db

# Save logs to file
docker-compose logs > logs/full-$(date +%Y%m%d).log
```

### Metrics Collection

#### Resource Monitoring
```bash
# Container resource usage
make stats

# System resource usage
docker system df
```

#### Application Metrics
- Request/response times via Nginx logs
- Database query performance via slow query log
- Redis command statistics
- Ollama model inference times

## 🔄 Backup & Recovery

### Automated Backups
```bash
# Create backup
make backup

# Backup with timestamp
./scripts/backup.sh

# Schedule backups (add to crontab)
0 2 * * * cd /path/to/project && make backup
```

### Restore Procedures
```bash
# List available backups
ls -la backups/

# Restore from backup
make backup-restore FILE=backup_20240101_020000.sql

# Test restore (to different database)
docker exec -i ai-assistant-postgres psql -U assistant -d test_db < backups/backup.sql
```

### Disaster Recovery
```bash
# Complete environment rebuild
make clean-all
make setup-complete

# Restore data
make backup-restore FILE=latest_backup.sql
```

## 🔧 Customization

### Adding New Services

#### 1. Update docker-compose.yml
```yaml
  new-service:
    image: service:latest
    ports:
      - "9000:9000"
    networks:
      - ai-assistant-network
    depends_on:
      - postgres
```

#### 2. Update Makefile
```makefile
logs-newservice: ## Show new service logs
	$(DOCKER_COMPOSE_DEV) logs -f new-service
```

#### 3. Update Health Checks
```bash
# Add to healthcheck.sh
check_new_service() {
    curl -f http://localhost:9000/health
}
```

### Environment Customization

#### Local Overrides
```bash
# Create local override file
cp docker-compose.dev.yml docker-compose.local.yml

# Edit for your specific needs
# Git will ignore this file
```

#### Custom Environment Files
```bash
# Create environment-specific files
.env.local        # Local development
.env.team         # Team shared settings
.env.staging      # Staging environment
```

### Development Workflow

1. **Start Development**: `make dev`
2. **Develop Backend**: Hot reload enabled
3. **Test Changes**: `make test`
4. **Check Quality**: `make lint && make format`
5. **Monitor**: Use admin interfaces and logs
6. **Deploy**: `make build && make deploy`

The Docker infrastructure is production-ready and provides a solid foundation for building the AI assistant backend in the upcoming phases.

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Run `make setup-complete`
3. Make your changes
4. Run `make test && make lint`
5. Submit a pull request

### Adding Features
- Follow the existing structure
- Update documentation
- Add appropriate tests
- Update health checks if needed
