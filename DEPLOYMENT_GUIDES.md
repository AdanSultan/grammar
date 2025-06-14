# Deployment Guides

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account
- GitHub repository with your frontend code
- Environment variables configured

### Step-by-Step Deployment

1. **Prepare Your Repository**
   ```bash
   cd frontend
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Select the `frontend` directory

3. **Configure Environment Variables**
   In Vercel dashboard, go to Settings → Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-domain.com
   ```

4. **Deploy**
   - Vercel will automatically detect Next.js
   - Click "Deploy"
   - Your app will be available at `https://your-project.vercel.app`

5. **Custom Domain (Optional)**
   - Go to Settings → Domains
   - Add your custom domain
   - Configure DNS records as instructed

### Vercel Configuration
The `vercel.json` file is already configured with:
- Security headers
- Function timeout settings
- Environment variable mapping

## Backend Deployment (AWS EC2)

### Prerequisites
- AWS account
- EC2 instance (recommended: t3.large or larger)
- Domain name (optional)
- SSL certificate

### Step-by-Step Deployment

1. **Launch EC2 Instance**
   ```bash
   # Recommended specifications
   Instance Type: t3.large (2 vCPU, 8 GB RAM)
   OS: Ubuntu 20.04 LTS
   Storage: 50 GB GP3
   Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
   ```

2. **Connect to Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Dependencies**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Install Nginx
   sudo apt install nginx -y
   ```

4. **Deploy Application**
   ```bash
   # Clone your repository
   git clone https://github.com/your-username/ai-to-human-converter.git
   cd ai-to-human-converter/backend
   
   # Create environment file
   cp .env.example .env
   nano .env  # Add your API keys
   
   # Build and run with Docker Compose
   sudo docker-compose up -d --build
   ```

5. **Configure Nginx**
   ```bash
   # Copy Nginx configuration
   sudo cp nginx.conf /etc/nginx/sites-available/ai-to-human
   sudo ln -s /etc/nginx/sites-available/ai-to-human /etc/nginx/sites-enabled/
   
   # Update domain in config
   sudo nano /etc/nginx/sites-available/ai-to-human
   # Replace 'your-domain.com' with your actual domain
   
   # Test and reload Nginx
   sudo nginx -t
   sudo systemctl reload nginx
   ```

6. **SSL Certificate (Let's Encrypt)**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx -y
   
   # Get SSL certificate
   sudo certbot --nginx -d your-domain.com
   
   # Auto-renewal
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

7. **Setup Redis (Optional)**
   ```bash
   # Redis is already included in docker-compose.yml
   # For production, consider using AWS ElastiCache
   ```

### Docker Configuration
The `Dockerfile` is optimized for:
- Multi-stage builds
- Security (non-root user)
- Health checks
- Performance optimization

### Monitoring and Logs
```bash
# View application logs
sudo docker-compose logs -f app

# Monitor system resources
htop

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

### Backend (.env)
```env
# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
COHERE_API_KEY=your-cohere-key
GPTZERO_API_KEY=your-gptzero-key
TURNITIN_API_KEY=your-turnitin-key
COPYLEAKS_API_KEY=your-copyleaks-key
ORIGINALITY_API_KEY=your-originality-key

# Redis
REDIS_URL=redis://localhost:6379

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

## Scaling and Performance

### Horizontal Scaling
```bash
# Scale backend services
sudo docker-compose up -d --scale app=3

# Update Nginx upstream
# Add more backend servers in nginx.conf
```

### Load Balancing
The Nginx configuration includes:
- Round-robin load balancing
- Health checks
- Rate limiting
- Gzip compression

### Caching Strategy
- Redis for API response caching
- Browser caching for static assets
- CDN for global distribution

## Security Best Practices

1. **Network Security**
   - Use security groups to restrict access
   - Enable VPC for network isolation
   - Use private subnets for backend

2. **Application Security**
   - Regular security updates
   - Input validation and sanitization
   - Rate limiting and DDoS protection

3. **Data Protection**
   - Encrypt data in transit (HTTPS)
   - Encrypt data at rest
   - Regular backups

## Monitoring and Alerts

### CloudWatch Setup
```bash
# Install CloudWatch agent
sudo apt install amazon-cloudwatch-agent -y

# Configure monitoring
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Health Checks
- Application health endpoint: `/health`
- Docker health checks
- Nginx upstream health checks

## Backup Strategy

### Database Backups
```bash
# Redis backup
sudo docker exec redis redis-cli BGSAVE

# Application data backup
sudo docker-compose exec app tar -czf /backup/app-$(date +%Y%m%d).tar.gz /app/data
```

### Configuration Backups
```bash
# Backup configuration files
sudo tar -czf /backup/config-$(date +%Y%m%d).tar.gz /etc/nginx /etc/ssl
```

## Troubleshooting

### Common Issues

1. **Application Not Starting**
   ```bash
   # Check logs
   sudo docker-compose logs app
   
   # Check environment variables
   sudo docker-compose exec app env
   ```

2. **Nginx Issues**
   ```bash
   # Test configuration
   sudo nginx -t
   
   # Check status
   sudo systemctl status nginx
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew manually
   sudo certbot renew
   ```

### Performance Optimization

1. **Database Optimization**
   - Redis connection pooling
   - Query optimization
   - Index optimization

2. **Application Optimization**
   - Async processing
   - Caching strategies
   - Resource monitoring

## Cost Optimization

### AWS Cost Management
- Use reserved instances for predictable workloads
- Enable auto-scaling based on demand
- Monitor and optimize resource usage

### Resource Recommendations
- **Development**: t3.micro (1 vCPU, 1 GB RAM)
- **Production**: t3.large (2 vCPU, 8 GB RAM)
- **High Traffic**: t3.xlarge (4 vCPU, 16 GB RAM)

## Maintenance

### Regular Tasks
- Security updates
- SSL certificate renewal
- Log rotation
- Performance monitoring
- Backup verification

### Update Process
```bash
# Update application
git pull origin main
sudo docker-compose down
sudo docker-compose up -d --build

# Update system
sudo apt update && sudo apt upgrade -y
```

## Support and Documentation

### Useful Commands
```bash
# View all containers
sudo docker ps

# Restart services
sudo docker-compose restart

# View resource usage
sudo docker stats

# Access application shell
sudo docker-compose exec app bash
```

### Monitoring URLs
- Application: `https://your-domain.com`
- Health Check: `https://your-domain.com/health`
- API Documentation: `https://your-domain.com/docs`

This deployment guide ensures a production-ready setup with security, performance, and scalability in mind. 