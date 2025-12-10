# Production Deployment Guide

## Deployment Options

### Option 1: Streamlit Cloud (Recommended for Internal Use)

#### Prerequisites
- GitHub account
- Streamlit Cloud account (streamlit.io/cloud)

#### Steps

1. **Push Code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit - Top 40 Dashboard"
git remote add origin https://github.com/your-org/top40-dashboard.git
git push -u origin main
```

2. **Configure Secrets**
   - Go to Streamlit Cloud dashboard
   - Select your app
   - Click "Settings" → "Secrets"
   - Add secrets in TOML format:

```toml
[netsuite]
account_id = "YOUR_ACCOUNT_ID"
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
token_id = "YOUR_TOKEN_ID"
token_secret = "YOUR_TOKEN_SECRET"
restlet_url = "YOUR_RESTLET_URL"
```

3. **Deploy**
   - Connect your GitHub repository
   - Select branch (main)
   - Set main file: `app.py`
   - Click "Deploy"

4. **Update app.py for Secrets**

Modify the connection section in `app.py`:

```python
def initialize_connection():
    """Initialize NetSuite connection using Streamlit secrets"""
    try:
        if 'netsuite' in st.secrets:
            # Use secrets from Streamlit Cloud
            connector = NetSuiteConnector(
                account_id=st.secrets["netsuite"]["account_id"],
                consumer_key=st.secrets["netsuite"]["consumer_key"],
                consumer_secret=st.secrets["netsuite"]["consumer_secret"],
                token_id=st.secrets["netsuite"]["token_id"],
                token_secret=st.secrets["netsuite"]["token_secret"],
                restlet_url=st.secrets["netsuite"]["restlet_url"]
            )
            st.session_state.netsuite_connector = connector
            st.session_state.data_processor = DataProcessor(connector)
            return True
        else:
            # Fallback to manual entry (for local development)
            return False
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return False
```

### Option 2: Docker Deployment

#### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Build and Run

```bash
# Build image
docker build -t drew-top40-dashboard .

# Run container
docker run -p 8501:8501 \
  -e NS_ACCOUNT_ID="your_account_id" \
  -e NS_CONSUMER_KEY="your_consumer_key" \
  -e NS_CONSUMER_SECRET="your_consumer_secret" \
  -e NS_TOKEN_ID="your_token_id" \
  -e NS_TOKEN_SECRET="your_token_secret" \
  -e NS_RESTLET_URL="your_restlet_url" \
  drew-top40-dashboard
```

#### Docker Compose (Optional)

```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - NS_ACCOUNT_ID=${NS_ACCOUNT_ID}
      - NS_CONSUMER_KEY=${NS_CONSUMER_KEY}
      - NS_CONSUMER_SECRET=${NS_CONSUMER_SECRET}
      - NS_TOKEN_ID=${NS_TOKEN_ID}
      - NS_TOKEN_SECRET=${NS_TOKEN_SECRET}
      - NS_RESTLET_URL=${NS_RESTLET_URL}
    restart: unless-stopped
```

### Option 3: AWS Deployment

#### Using AWS Elastic Container Service (ECS)

1. **Push Docker Image to ECR**
```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag drew-top40-dashboard:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/drew-top40-dashboard:latest

# Push
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/drew-top40-dashboard:latest
```

2. **Create ECS Task Definition**
   - Container image: ECR image URL
   - Port mappings: 8501
   - Environment variables: NetSuite credentials (use AWS Secrets Manager)

3. **Create ECS Service**
   - Launch type: Fargate
   - Load balancer: Application Load Balancer
   - Auto-scaling: Configure as needed

4. **Configure Security**
   - Security group: Allow inbound 8501
   - IAM role: Access to Secrets Manager
   - VPC: Private subnet with NAT gateway

### Option 4: Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name drew-dashboard-rg --location eastus

# Create container instance
az container create \
  --resource-group drew-dashboard-rg \
  --name drew-top40-dashboard \
  --image your-registry.azurecr.io/drew-top40-dashboard:latest \
  --dns-name-label drew-dashboard \
  --ports 8501 \
  --environment-variables \
    NS_ACCOUNT_ID=$NS_ACCOUNT_ID \
    NS_CONSUMER_KEY=$NS_CONSUMER_KEY \
  --secure-environment-variables \
    NS_CONSUMER_SECRET=$NS_CONSUMER_SECRET \
    NS_TOKEN_ID=$NS_TOKEN_ID \
    NS_TOKEN_SECRET=$NS_TOKEN_SECRET
```

## Security Considerations

### 1. Credentials Management

**Never** commit credentials to Git. Use one of:

- **Streamlit Cloud:** Built-in secrets management
- **Environment Variables:** For Docker/cloud deployments
- **AWS Secrets Manager:** For AWS deployments
- **Azure Key Vault:** For Azure deployments
- **HashiCorp Vault:** For on-premise deployments

### 2. Network Security

- Deploy in private subnet with NAT gateway
- Use Application Load Balancer with HTTPS
- Configure security groups to allow only necessary traffic
- Enable VPC Flow Logs for monitoring

### 3. Authentication

Consider adding authentication layer:

- **Streamlit-Authenticator:** Password-based auth
- **OAuth 2.0:** SSO with corporate identity provider
- **AWS Cognito:** For AWS deployments
- **Azure AD:** For Azure deployments

Example with Streamlit-Authenticator:

```python
import streamlit_authenticator as stauth

# In app.py, before main dashboard
authenticator = stauth.Authenticate(
    credentials,
    'dashboard_cookie',
    'dashboard_key',
    30  # cookie expiry days
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Show dashboard
    main()
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
```

### 4. Rate Limiting

Add rate limiting to prevent API abuse:

```python
from functools import wraps
import time

def rate_limit(max_calls=10, time_frame=60):
    """Rate limit decorator"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls_in_time_frame = [c for c in calls if now - c < time_frame]
            
            if len(calls_in_time_frame) >= max_calls:
                st.error("Rate limit exceeded. Please wait.")
                return None
            
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Monitoring & Logging

### Application Monitoring

Add logging to track usage and errors:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# In functions
logger.info(f"User {username} accessed Top 40 Styles")
logger.error(f"NetSuite API error: {str(e)}")
```

### Performance Monitoring

Use Streamlit's built-in performance tracking:

```python
import streamlit as st

with st.spinner("Loading data..."):
    start_time = time.time()
    data = load_data()
    elapsed = time.time() - start_time
    logger.info(f"Data loaded in {elapsed:.2f} seconds")
```

### Health Checks

Add health check endpoint for load balancers:

```python
# health_check.py
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')

if __name__ == '__main__':
    server = HTTPServer(('', 8080), HealthHandler)
    server.serve_forever()
```

## Backup & Disaster Recovery

### Database Backups

Since this dashboard reads from NetSuite (no local database), ensure:

1. NetSuite has proper backup procedures
2. Document all custom fields and saved searches
3. Version control all RESTlet scripts
4. Keep copy of cost/retail master file

### Application Backup

1. **Code:** Store in version control (GitHub)
2. **Configuration:** Document all secrets and settings
3. **Documentation:** Keep CRISP and setup docs updated

## Performance Optimization

### Caching

Add caching to reduce NetSuite API calls:

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_styles_data(start_date, end_date, filters):
    processor = st.session_state.data_processor
    return processor.get_top_40_styles(start_date, end_date, **filters)
```

### Lazy Loading

Load data only when needed:

```python
if st.session_state.styles_data is None:
    if st.button("Load Top 40 Styles"):
        st.session_state.styles_data = load_styles_data(...)
```

### Pagination

For large result sets, implement pagination:

```python
# Display results in pages
page_size = 20
total_pages = len(data) // page_size + 1

page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
start_idx = (page - 1) * page_size
end_idx = start_idx + page_size

st.dataframe(data[start_idx:end_idx])
```

## Maintenance Schedule

### Daily
- Monitor application logs for errors
- Check NetSuite API rate limits

### Weekly
- Review cost/retail data sync
- Verify data accuracy with business users
- Check for NetSuite field ID changes

### Monthly
- Update dependencies (security patches)
- Review and optimize slow queries
- Clean up item master inconsistencies

### Quarterly
- Full security audit
- Performance optimization review
- User feedback session
- Documentation updates

## Rollback Procedure

If deployment fails:

1. **Streamlit Cloud:**
   - Revert to previous GitHub commit
   - Redeploy from Streamlit Cloud dashboard

2. **Docker:**
   ```bash
   docker stop drew-top40-dashboard
   docker run previous-image-tag
   ```

3. **Cloud Services:**
   - Roll back to previous task definition (ECS)
   - Restore previous container instance (ACI)

## Support & Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Slow performance | Enable caching, optimize queries |
| Connection timeouts | Increase timeout values, check NetSuite availability |
| Missing data | Verify NetSuite field IDs, check saved searches |
| Memory errors | Reduce data page size, implement pagination |

### Getting Help

1. Check application logs
2. Review NetSuite script execution logs
3. Verify all credentials are current
4. Test NetSuite API connection separately
5. Contact Megan Spencer (technical) or Troy (data rules)

---

**Last Updated:** Dec 10, 2025
**Version:** 1.0.0
