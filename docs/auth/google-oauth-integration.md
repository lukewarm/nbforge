# Google OAuth Integration Guide for NBForge

This guide provides detailed instructions for integrating Google OAuth authentication with NBForge, allowing users to sign in with their Google accounts.

## Prerequisites

- A Google Cloud account with access to create projects
- NBForge application running locally or deployed
- Access to modify the NBForge codebase and deploy changes

## Part 1: Google Cloud Configuration

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top and select "New Project"
3. Enter a project name (e.g., "NBForge") and click "Create"
4. Wait for the project to be created, then select it

### 2. Configure OAuth Consent Screen

1. Navigate to **APIs & Services > OAuth consent screen**
2. Select the appropriate user type for your application:
   - **External** (available to any Google user)
   - **Internal** (only available to users within your organization)
3. Click "Create"
4. Fill in the required details:
   - App name: "NBForge"
   - User support email: Your email
   - Developer contact information: Your email
5. Click "Save and Continue"
6. Add the following scopes:
   - `email`
   - `profile`
   - `openid`
7. Click "Save and Continue"
8. Add test users if you selected External user type
9. Review your settings and click "Back to Dashboard"

### 3. Create OAuth Client ID

1. Navigate to **APIs & Services > Credentials**
2. Click "Create Credentials" and select "OAuth client ID"
3. Select "Web application" as the application type
4. Name: "NBForge Web Client"
5. Add authorized JavaScript origins:
   - `http://localhost:5173` (for local development)
   - `https://your-production-domain.com` (for production)
6. Add authorized redirect URIs:
   - `http://localhost:8000/api/v1/auth/google/callback` (for local development)
   - `https://your-production-domain.com/api/v1/auth/google/callback` (for production)
7. Click "Create"
8. Note down the **Client ID** and **Client Secret** (you'll need them for configuration)

## Part 2: Backend Configuration

### 1. Add Google OAuth Environment Variables

Add the following variables to your `.env` file:

```
# Google OAuth Settings
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

### 2. Install Required Packages

Install the required Python packages:

```bash
pip install authlib httpx
```

Add these to your `requirements.txt` file.

### 3. Create Google OAuth Endpoints

Edit `backend/app/api/v1/auth.py` to add Google OAuth endpoints:

```python
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
import secrets
import logging

logger = logging.getLogger(__name__)

# Initialize OAuth client
oauth = OAuth()
google = oauth.register(
    name="google",
    client_id=settings.OAUTH_PROVIDERS["google"]["client_id"],
    client_secret=settings.OAUTH_PROVIDERS["google"]["client_secret"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

@router.get("/google/login")
async def login_google(request: Request):
    """Generate Google OAuth login URL"""
    if not settings.OAUTH_PROVIDERS["google"]["client_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google login is not enabled"
        )
    
    redirect_uri = request.url_for("google_callback")
    return await google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(deps.get_db)):
    """Handle Google OAuth callback"""
    if not settings.OAUTH_PROVIDERS["google"]["client_id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google login is not enabled"
        )
    
    try:
        token = await google.authorize_access_token(request)
        userinfo = await google.parse_id_token(request, token)
        
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
                oauth_provider="google",
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
        logger.error(f"Google login failed: {str(e)}")
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=oauth_failed")
```

### 4. Ensure the Auth Config API Is Updated

Make sure the `/api/v1/auth/config` endpoint returns Google configuration:

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
            }
        },
        "demo_mode": settings.DEMO_MODE,
        "demo_user": settings.DEMO_USER if settings.DEMO_MODE else None,
        "emails_enabled": settings.EMAILS_ENABLED and settings.EMAIL_PROVIDER != "dummy"
    }
```

## Part 3: Frontend Configuration

### 1. Update Auth Store

Edit `frontend/src/stores/auth.js` to handle Google login:

```javascript
// Add Google login method
async function loginWithGoogle() {
  try {
    // Redirect to backend Google login URL
    window.location.href = `${API_URL}/api/v1/auth/google/login`;
    // The rest is handled by the backend redirect
    return true;
  } catch (error) {
    console.error('Google login error:', error);
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
  loginWithGoogle  // Add this
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

### 4. Update Login View to Display Google Option

Update `frontend/src/views/Login.vue` to add the Google login button:

```vue
<!-- Add this button with the other OAuth providers -->
<div v-if="authConfig.oauth_providers?.google?.enabled" class="mt-4">
  <button
    type="button"
    @click="loginWithGoogle"
    class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
  >
    <span class="mr-2">
      <!-- Google icon SVG -->
      <svg width="18" height="18" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path d="M12.24 10.285V14.4h6.806c-.275 1.765-2.056 5.174-6.806 5.174-4.095 0-7.439-3.389-7.439-7.574s3.345-7.574 7.439-7.574c2.33 0 3.891.989 4.785 1.849l3.254-3.138C18.189 1.186 15.479 0 12.24 0c-6.635 0-12 5.365-12 12s5.365 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.085-1.39-.189-1.989H12.24z" fill="#4285F4"/>
        <path d="M12.24 10.285V14.4h6.806c-.275 1.765-2.056 5.174-6.806 5.174-4.095 0-7.439-3.389-7.439-7.574s3.345-7.574 7.439-7.574c2.33 0 3.891.989 4.785 1.849l3.254-3.138C18.189 1.186 15.479 0 12.24 0c-6.635 0-12 5.365-12 12s5.365 12 12 12c6.926 0 11.52-4.869 11.52-11.726 0-.788-.085-1.39-.189-1.989H12.24z" fill="#4285F4"/>
      </svg>
    </span>
    Sign in with Google
  </button>
</div>
```

Add the method in the script section:

```javascript
function loginWithGoogle() {
  authStore.loginWithGoogle();
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
3. You should see the "Sign in with Google" button if properly configured
4. Click the button to start the Google authentication flow
5. After authenticating with Google, you should be redirected back to your application with a valid session

## Troubleshooting

### Common Issues

1. **Redirect URI Mismatch**: The redirect URI in your Google Cloud Console must exactly match the callback URL in your code.
2. **Missing Scopes**: Ensure you've added the required scopes (email, profile, openid) in both the OAuth consent screen and client configuration.
3. **CORS Issues**: Check your CORS settings if you're experiencing cross-origin problems.
4. **Authorization Errors**: Ensure your application is set up correctly in Google Cloud Console and has the necessary permissions.

### Debugging Steps

1. Check the backend logs for detailed error messages
2. Use browser developer tools to inspect network requests and responses
3. Verify the token flow by logging token contents (but never in production!)
4. Ensure your model has the necessary fields to store OAuth information

## Security Considerations

1. **Token Storage**: JWT tokens should be properly stored and managed securely
2. **User Creation**: Consider additional security or verification steps when creating users via OAuth
3. **Scopes**: Request only the scopes you actually need for your application
4. **Rate Limiting**: Implement rate limiting to prevent abuse of the OAuth endpoints

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT Authentication Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/) 