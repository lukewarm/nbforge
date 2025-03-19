# Okta Integration Guide for NBForge

This guide provides step-by-step instructions for integrating Okta Single Sign-On (SSO) with NBForge's authentication system.

## Prerequisites

- Admin access to an Okta account
- NBForge application running locally or deployed
- Access to modify the NBForge codebase and deploy changes

## Part 1: Okta Configuration

### 1. Create an OAuth/OIDC Application in Okta

1. Log in to your Okta Admin Dashboard
2. Navigate to **Applications > Applications**
3. Click **Create App Integration**
4. Select **OIDC - OpenID Connect** as the Sign-in method
5. Choose **Web Application** as the Application type
6. Click **Next**

### 2. Configure the Okta Application

1. Name your application (e.g., "NBForge")
2. Add the following URLs:
   - **Sign-in redirect URIs**: `http://localhost:8000/api/v1/auth/okta/callback` (for local development)
     - Add your production URL if applicable: `https://your-domain.com/api/v1/auth/okta/callback`
   - **Sign-out redirect URIs**: `http://localhost:5173` (or your frontend URL)
3. Under **Assignments**, select either:
   - **Allow everyone in your organization to access** (for organization-wide access), or
   - **Limit access to selected groups** (for restricted access)
4. Click **Save**

### 3. Retrieve Okta Application Credentials

After creating the application, note down the following credentials (you'll need them for the backend configuration):
- **Client ID**
- **Client Secret**
- **Okta Domain** (e.g., `dev-12345.okta.com`)

## Part 2: Backend Configuration

### 1. Add Okta Environment Variables

Add the following variables to your `.env` file:

```
# Okta Settings
OKTA_CLIENT_ID=your_client_id_here
OKTA_CLIENT_SECRET=your_client_secret_here
OKTA_DOMAIN=your_okta_domain.okta.com
OKTA_ENABLED=true
```

### 2. Update Configuration Module

Edit `backend/app/core/config.py` to include Okta provider settings:

```python
# Add Okta to the OAUTH_PROVIDERS dictionary
OAUTH_PROVIDERS: dict = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
    },
    "okta": {
        "client_id": os.getenv("OKTA_CLIENT_ID", ""),
        "client_secret": os.getenv("OKTA_CLIENT_SECRET", ""),
        "domain": os.getenv("OKTA_DOMAIN", ""),
        "enabled": os.getenv("OKTA_ENABLED", "false").lower() == "true",
    }
}
```

### 3. Create Okta OAuth Endpoints

Edit `backend/app/api/v1/auth.py` to add Okta OAuth endpoints:

```python
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
import secrets
import logging

logger = logging.getLogger(__name__)

# Initialize OAuth client
oauth = OAuth()
okta = oauth.register(
    name="okta",
    client_id=settings.OAUTH_PROVIDERS["okta"]["client_id"],
    client_secret=settings.OAUTH_PROVIDERS["okta"]["client_secret"],
    server_metadata_url=f'https://{settings.OAUTH_PROVIDERS["okta"]["domain"]}/oauth2/default/.well-known/oauth-authorization-server',
    client_kwargs={
        "scope": "openid email profile"
    }
)

@router.get("/okta/login")
async def login_okta(request: Request):
    """Generate Okta OAuth login URL"""
    if not settings.OAUTH_PROVIDERS["okta"]["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Okta login is not enabled"
        )
    
    redirect_uri = request.url_for("okta_callback")
    return await okta.authorize_redirect(request, redirect_uri)

@router.get("/okta/callback", name="okta_callback")
async def okta_callback(request: Request, db: Session = Depends(deps.get_db)):
    """Handle Okta OAuth callback"""
    if not settings.OAUTH_PROVIDERS["okta"]["enabled"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Okta login is not enabled"
        )
    
    try:
        token = await okta.authorize_access_token(request)
        userinfo = await okta.parse_id_token(request, token)
        
        # Get email from userinfo
        email = userinfo["email"]
        
        # Check if user exists
        user = crud.user.get_by_email(db, email=email)
        
        # Create user if not exists
        if not user:
            user_in = schemas.UserCreate(
                email=email,
                password=secrets.token_urlsafe(16),  # Random password
                full_name=userinfo.get("name", email.split("@")[0]),
                is_active=True,
            )
            user = crud.user.create(db, obj_in=user_in)
        
        # Update OAuth info
        if not user.oauth_provider or not user.oauth_id:
            user_update = schemas.UserUpdate(
                oauth_provider="okta",
                oauth_id=userinfo["sub"]
            )
            user = crud.user.update(db, db_obj=user, obj_in=user_update)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token
        frontend_url = settings.FRONTEND_URL
        return RedirectResponse(f"{frontend_url}/auth/callback?token={access_token}")
    
    except Exception as e:
        # Log the error and redirect to login page with error
        logger.error(f"Okta login failed: {str(e)}")
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=oauth_failed")
```

### 4. Update Auth Config Endpoint

Update the `/config` endpoint in `backend/app/api/v1/auth.py` to include Okta:

```python
@router.get("/config", response_model=Dict[str, Any])
def get_auth_config():
    """Get authentication configuration for the frontend"""
    return {
        "oauth_providers": {
            "google": {
                "client_id": bool(settings.OAUTH_PROVIDERS.get("google", {}).get("client_id")),
                "enabled": bool(settings.OAUTH_PROVIDERS.get("google", {}).get("client_id"))
            },
            "github": {
                "client_id": bool(settings.OAUTH_PROVIDERS.get("github", {}).get("client_id")),
                "enabled": bool(settings.OAUTH_PROVIDERS.get("github", {}).get("client_id"))
            },
            "okta": {
                "enabled": settings.OAUTH_PROVIDERS.get("okta", {}).get("enabled", False)
            }
        },
        "demo_mode": settings.DEMO_MODE,
        "demo_user": settings.DEMO_USER if settings.DEMO_MODE else None,
        "emails_enabled": settings.EMAILS_ENABLED and settings.EMAIL_PROVIDER != "dummy"
    }
```

### 5. Add Dependencies

Install required packages:

```bash
pip install authlib httpx itsdangerous
```

Add these to your `requirements.txt` file.

## Part 3: Frontend Configuration

### 1. Update Auth Store

Edit `frontend/src/stores/auth.js` to handle Okta login:

```javascript
// Add Okta login method
async function loginWithOkta() {
  try {
    // Redirect to backend Okta login URL
    window.location.href = `${API_URL}/api/v1/auth/okta/login`;
    // The rest is handled by the backend redirect
    return true;
  } catch (error) {
    console.error('Okta login error:', error);
    throw error;
  }
}

// Add to the returned object
return {
  user,
  token,
  loading,
  error,
  demoMode,
  isAuthenticated,
  login,
  register,
  logout,
  initAuth,
  fetchCurrentUser,
  loginWithOkta  // Add this
}
```

### 2. Create OAuth Callback Component

Create a new file `frontend/src/views/AuthCallback.vue`:

```vue
<template>
  <div class="flex justify-center items-center h-screen">
    <div v-if="error" class="text-red-500">
      {{ error }}
    </div>
    <div v-else>
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      <p class="mt-4 text-gray-600">Completing login...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const error = ref(null);

onMounted(async () => {
  try {
    // Get token from URL
    const token = route.query.token;
    
    if (!token) {
      throw new Error('No token provided');
    }
    
    // Set token in auth store
    authStore.token = token;
    localStorage.setItem('token', token);
    
    // Fetch current user with the token
    await authStore.fetchCurrentUser();
    
    // Redirect to home
    router.push('/');
  } catch (err) {
    error.value = 'Authentication failed. Please try again.';
    console.error('Auth callback error:', err);
    
    // Redirect to login after short delay
    setTimeout(() => {
      router.push('/login');
    }, 3000);
  }
});
</script>
```

### 3. Add the Auth Callback Route

Update `frontend/src/router/index.js` to include the callback route:

```javascript
import AuthCallback from '@/views/AuthCallback.vue'

// Add to routes array
{
  path: '/auth/callback',
  name: 'auth-callback',
  component: AuthCallback,
  meta: { requiresAuth: false }
}
```

### 4. Update Login View to Display Okta Option

Update `frontend/src/views/Login.vue` to add an Okta login button:

```vue
<!-- Add this button with the other OAuth providers -->
<div v-if="authConfig.oauth_providers?.okta?.enabled" class="mt-4">
  <button
    type="button"
    @click="loginWithOkta"
    class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
  >
    <span class="mr-2">
      <!-- Okta icon SVG -->
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 0C5.389 0 0 5.389 0 12C0 18.611 5.389 24 12 24C18.611 24 24 18.611 24 12C24 5.389 18.611 0 12 0ZM12 17.25C9.093 17.25 6.75 14.907 6.75 12C6.75 9.093 9.093 6.75 12 6.75C14.907 6.75 17.25 9.093 17.25 12C17.25 14.907 14.907 17.25 12 17.25Z" fill="#007DC1"/>
      </svg>
    </span>
    Sign in with Okta
  </button>
</div>
```

Add the method in the script section:

```javascript
function loginWithOkta() {
  authStore.loginWithOkta();
}
```

## Frontend Considerations

1. **Error Handling**:
   - The frontend should handle OAuth errors gracefully
   - Display appropriate error messages to users
   - Provide a way to retry failed authentication

2. **Loading States**:
   - Show loading indicators during OAuth redirects
   - Handle network timeouts appropriately

3. **Token Management**:
   - Store tokens securely (preferably in memory)
   - Implement token refresh logic
   - Clear tokens on logout

4. **User Experience**:
   - Provide clear feedback during the OAuth flow
   - Maintain user context after authentication
   - Handle browser back/forward navigation

5. **Security**:
   - Use HTTPS in production
   - Implement CSRF protection
   - Validate tokens on the frontend

## Testing the Integration

1. Start your backend and frontend applications
2. Navigate to the login page
3. You should see the "Sign in with Okta" button if properly configured
4. Click the button to start the Okta authentication flow
5. After successful authentication, you should be redirected back to your application

## Troubleshooting

### Common Issues

1. **Redirect URI Mismatch**: Ensure the redirect URI in your Okta application configuration exactly matches the callback URL in your code.
2. **CORS Issues**: Verify your CORS settings in both Okta and your backend.
3. **Network Errors**: Check if your application can reach the Okta domain.
4. **Token Handling**: Ensure the JWT token is being properly created and handled.

### Debugging

1. Check backend logs for detailed error messages
2. Use browser developer tools to inspect network requests and responses
3. Verify environment variables are correctly set
4. Confirm Okta application settings are correctly configured

## Additional Resources

- [Okta Developer Documentation](https://developer.okta.com/docs/guides/)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/) 