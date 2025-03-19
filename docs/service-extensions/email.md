# Email Service

The Email Service provides a unified interface for sending emails across different email providers. Currently, it implements SMTP email sending and a dummy provider for testing, but the architecture is designed to be extended with additional providers such as SendGrid, Mailchimp, or any other email service.

## Architecture

The email service follows a provider-based architecture:

1. **Abstract Base Class** (`EmailProvider`): Defines the contract that all email providers must implement.
2. **Implementations**: Provider-specific classes that implement the `EmailProvider` abstract base class.
   - `SMTPEmailProvider`: Implementation for sending emails via SMTP
   - `DummyEmailProvider`: Implementation for development/testing that logs emails instead of sending them
3. **Service** (`EmailService`): Main service class that selects and uses the appropriate provider based on configuration.

## Extending with New Providers

To add support for a new email provider (e.g., SendGrid, Mailchimp, AWS SES), follow these steps:

### 1. Create a New Provider Class

Create a new class that inherits from `EmailProvider` and implements the required `send_email` method:

```python
from typing import Optional
import logging
from app.services.email import EmailProvider

logger = logging.getLogger(__name__)

class CustomProvider(EmailProvider):
    """Custom email provider implementation"""
    
    def __init__(self, api_key: str, from_email: str):
        """Initialize with API key and sender email"""
        self.api_key = api_key
        self.from_email = from_email
        # Initialize any provider-specific client here
        # For example: self.client = SomeEmailSDK(api_key)
        
    async def send_email(
        self,
        email_to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email using the custom provider"""
        try:
            # Implement provider-specific logic here
            # Example:
            # response = await self.client.send(
            #     from_email=self.from_email,
            #     to_email=email_to,
            #     subject=subject,
            #     html_content=html_content,
            #     text_content=text_content
            # )
            
            # Log success
            logger.info(f"Email sent to {email_to} via CustomProvider")
            return True
            
        except Exception as e:
            # Log failure with detailed error
            logger.error(f"Error sending email via CustomProvider: {str(e)}")
            return False
```

### 2. Update the `_get_provider` Method

Modify the `_get_provider` method in the `EmailService` class to include your new provider:

```python
def _get_provider(self) -> EmailProvider:
    """Get the configured email provider"""
    provider_type = settings.EMAIL_PROVIDER.lower()
    
    if provider_type == "smtp":
        return SMTPEmailProvider(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            from_email=settings.EMAIL_FROM,
            use_tls=settings.SMTP_TLS
        )
    elif provider_type == "custom":
        return CustomProvider(
            api_key=settings.CUSTOM_API_KEY,
            from_email=settings.EMAIL_FROM
        )
    else:
        # Default to dummy provider if not configured or invalid provider type
        return DummyEmailProvider()
```

### 3. Update Configuration

Add the necessary configuration settings to `config.py`:

```python
# Email settings
EMAILS_ENABLED: bool = parse_bool(os.getenv("EMAILS_ENABLED", "False"))
EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "dummy")
EMAIL_FROM: str = os.getenv("EMAIL_FROM", "info@example.com")
EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Example Service")

# SMTP settings
SMTP_HOST: str = os.getenv("SMTP_HOST", "")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
SMTP_TLS: bool = parse_bool(os.getenv("SMTP_TLS", "True"))

# Custom provider settings
CUSTOM_API_KEY: str = os.getenv("CUSTOM_API_KEY", "")
```

## Requirements for Provider Implementation

When implementing a new email provider, ensure:

1. **Interface Compliance**: Implement the `send_email` method as defined in the `EmailProvider` abstract base class.
2. **Error Handling**: Implement robust error handling for all provider-specific exceptions.
3. **Async Support**: Ensure the `send_email` method is properly asynchronous, even if the underlying provider SDK is synchronous.
4. **Logging**: Provide detailed logging for successful sends and failures.
5. **Return Value**: Return `True` for successful sends and `False` for failures.

## Best Practices

1. **Lazy Loading**: Import provider-specific packages inside methods to avoid unnecessary dependencies.
2. **Detailed Logging**: Log successes and failures with appropriate detail.
3. **Fallback Strategy**: Consider implementing a fallback mechanism to another provider in case of failures.
4. **Testing**: Create comprehensive tests for your provider implementation.
5. **Documentation**: Update documentation to include the new provider and its configuration.

## Development Tips

1. **Environment Variables**: Use environment variables for sensitive information like API keys.
2. **Rate Limits**: Be aware of provider rate limits and implement appropriate backoff strategies.
3. **Content Validation**: Validate email content before sending to avoid provider rejections.
4. **Template Support**: Consider adding support for template-based emails if your provider supports it. 