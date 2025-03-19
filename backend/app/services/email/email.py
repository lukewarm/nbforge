from typing import List, Dict, Any, Optional
import logging
from abc import ABC, abstractmethod
from pydantic import EmailStr
from datetime import datetime

from app.core.config import get_settings

settings = get_settings()

logger = logging.getLogger(__name__)

class EmailProvider(ABC):
    """Base class for email providers"""
    
    @abstractmethod
    async def send_email(
        self,
        email_to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email"""
        pass

class SMTPEmailProvider(EmailProvider):
    """SMTP email provider implementation"""
    
    def __init__(
        self, 
        host: str, 
        port: int, 
        username: str, 
        password: str,
        from_email: str,
        use_tls: bool = True
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls
        
    async def send_email(
        self,
        email_to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email using SMTP"""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = email_to
            
            # Add content
            if text_content:
                message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            # Connect to server and send
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.username and self.password:
                    server.login(self.username, self.password)
                    
                server.sendmail(self.from_email, email_to, message.as_string())
                
            logger.info(f"Email sent to {email_to} via SMTP")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email via SMTP: {str(e)}")
            return False

class DummyEmailProvider(EmailProvider):
    """Dummy email provider for development/testing"""
    
    async def send_email(
        self,
        email_to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Log the email instead of sending it"""
        logger.info(f"[DUMMY EMAIL] To: {email_to}, Subject: {subject}")
        logger.info(f"[DUMMY EMAIL] HTML Content: {html_content}")
        if text_content:
            logger.info(f"[DUMMY EMAIL] Text Content: {text_content}")
        return True

class EmailService:
    """Email service that uses the configured provider"""
    
    def __init__(self):
        self.provider = self._get_provider()
        
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
        else:
            # Default to dummy provider if not configured or invalid provider type
            return DummyEmailProvider()
    
    async def send_email(
        self,
        email_to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email using the configured provider"""
        if not settings.EMAILS_ENABLED:
            logger.info(f"Emails disabled, would have sent to {email_to}")
            return True
            
        if settings.DEMO_MODE:
            logger.info(f"Demo mode enabled, not sending email to {email_to}")
            return True
            
        return await self.provider.send_email(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_password_reset_email(self, email_to: str, token: str) -> bool:
        """Send password reset email"""
        reset_link = f"{settings.FRONTEND_URL}/#/reset-password?token={token}"
        
        subject = f"{settings.PROJECT_NAME} - Password Recovery"
        html_content = f"""
        <p>Hi,</p>
        <p>We received a request to reset the password for your account.</p>
        <p>Please click the link below to reset your password:</p>
        <p><a href="{reset_link}">{reset_link}</a></p>
        <p>This link will expire in 24 hours.</p>
        <p>If you didn't request this password reset, you can safely ignore this email. Your account is secure.</p>
        <p>Thanks,</p>
        <p>The {settings.PROJECT_NAME} Team</p>
        """
        
        text_content = f"""
        Hi,
        
        We received a request to reset the password for your account.
        
        Please click the link below to reset your password:
        {reset_link}
        
        This link will expire in 24 hours.
        
        If you didn't request this password reset, you can safely ignore this email. Your account is secure.
        
        Thanks,
        The {settings.PROJECT_NAME} Team
        """
        
        return await self.send_email(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_execution_notification(
        self, 
        email_to: str, 
        execution_id: str,
        notebook_path: str,
        status: str,
        error: Optional[str] = None,
        output_html: Optional[str] = None,
        output_notebook: Optional[str] = None
    ) -> bool:
        """Send execution notification email"""
        # Base URL for accessing the UI
        frontend_url = settings.FRONTEND_URL
        
        # Generate execution detail page URL
        execution_url = f"{frontend_url}/#/executions/{execution_id}"
        
        # Generate results viewer URL if output_html is available
        results_url = None
        if output_html and status == "completed":
            results_url = f"{frontend_url}/#/results?path={output_html}&notebookPath={output_notebook if output_notebook else ''}"
        
        # Format notebook name for display (remove path and extension)
        notebook_name = notebook_path.split("/")[-1].replace(".ipynb", "")
        
        # Determine emoji, status display, and custom messages based on status
        if status == "completed":
            emoji = "✅"
            status_display = "COMPLETED SUCCESSFULLY"
            subject = f"{emoji} Notebook '{notebook_name}' execution completed"
            heading = "Your notebook execution has completed successfully!"
            message = "Great news! Your notebook was executed without any errors."
            button_text = "View Results"
            button_url = results_url if results_url else execution_url
            button_color = "#4CAF50"  # green
        elif status == "failed":
            emoji = "❌"
            status_display = "FAILED"
            subject = f"{emoji} Notebook '{notebook_name}' execution failed"
            heading = "Your notebook execution has failed."
            message = "We encountered an error while executing your notebook."
            button_text = "View Error Details"
            button_url = execution_url
            button_color = "#F44336"  # red
        else:
            emoji = "ℹ️"
            status_display = status.upper()
            subject = f"{emoji} Notebook '{notebook_name}' execution {status}"
            heading = f"Your notebook execution is {status}."
            message = f"The current status of your notebook execution is: {status}"
            button_text = "View Execution"
            button_url = execution_url
            button_color = "#2196F3"  # blue
        
        # Create HTML email content with better styling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.5; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ margin-bottom: 30px; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #4a5568; }}
                .content {{ background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
                .title {{ font-size: 20px; font-weight: bold; margin-bottom: 15px; color: #2d3748; }}
                .status {{ display: inline-block; padding: 5px 12px; border-radius: 15px; font-weight: bold; margin-bottom: 15px; }}
                .status.completed {{ background-color: #e3fcef; color: #0c6e47; }}
                .status.failed {{ background-color: #fee2e2; color: #b91c1c; }}
                .status.other {{ background-color: #e1effe; color: #1e429f; }}
                .details {{ margin-bottom: 20px; }}
                .details p {{ margin: 5px 0; }}
                .label {{ font-weight: 600; color: #4a5568; }}
                .button {{ display: inline-block; background-color: {button_color}; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; margin-top: 15px; }}
                .button:hover {{ opacity: 0.9; }}
                .error-box {{ background-color: #fee2e2; border-left: 4px solid #b91c1c; padding: 10px; margin-top: 15px; border-radius: 4px; overflow-x: auto; }}
                .error-text {{ font-family: monospace; white-space: pre-wrap; font-size: 12px; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #718096; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{settings.PROJECT_NAME}</div>
                </div>
                
                <div class="content">
                    <h1 class="title">{heading}</h1>
                    <div class="status {status if status in ['completed', 'failed'] else 'other'}">{status_display}</div>
                    
                    <p>{message}</p>
                    
                    <div class="details">
                        <p><span class="label">Notebook:</span> {notebook_name}</p>
                        <p><span class="label">Path:</span> {notebook_path}</p>
                        <p><span class="label">Execution ID:</span> {execution_id}</p>
                    </div>
                    
                    {f'''
                    <div class="error-box">
                        <p class="label">Error:</p>
                        <p class="error-text">{error}</p>
                    </div>
                    ''' if error else ''}
                    
                    <a href="{button_url}" class="button">{button_text}</a>
                    
                    <p style="margin-top: 20px;">You can also access the execution details directly at: <a href="{execution_url}">{execution_url}</a></p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message from {settings.PROJECT_NAME}.</p>
                    <p>&copy; {datetime.now().year} {settings.PROJECT_NAME}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text content as fallback
        error_block = f"Error:\n{error}" if error else ""

        text_content = f"""
        {heading}
        
        Status: {status_display}
        
        {message}
        
        ---- Execution Details ----
        Notebook: {notebook_name}
        Path: {notebook_path}
        Execution ID: {execution_id}
        
        {error_block}
        
        {f"View Results: {results_url}" if results_url else ""}
        
        View Execution Details: {execution_url}
        
        -------------------------
        
        This is an automated message from {settings.PROJECT_NAME}.
        """
        
        return await self.send_email(
            email_to=email_to,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

# Create a singleton instance
email_service = EmailService() 