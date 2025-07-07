import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from pathlib import Path
from app.utils.config import get_settings
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.settings = get_settings()
        self.template_env = Environment(
            loader=FileSystemLoader(
                Path(__file__).parent.parent / "templates" / "email"
            ),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
    def _create_smtp_connection(self):
        """Create SMTP connection based on configuration"""
        try:
            if self.settings.email_use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port)
            
            server.login(self.settings.smtp_username, self.settings.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {e}")
            raise AppException(f"Email service connection failed: {str(e)}", 500)
    
    def send_report_email(
        self, 
        recipient_email: str,
        report_type: str,
        attachments: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Send email with report attachments
        
        Args:
            recipient_email: Email address to send to
            report_type: Type of report (e.g., 'cleaning_summary')
            attachments: List of attachment dictionaries with keys: filename, data, content_type
            metadata: Report metadata (cleaned_rows, total_value, currency, etc.)
            
        Returns:
            Dictionary with success status, message_id, and auto_response
        """
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.settings.smtp_from_email
            message["To"] = recipient_email
            message["Subject"] = f"Bibbi Cleaner Report - {report_type.replace('_', ' ').title()}"
            
            # Generate email body from template
            template = self.template_env.get_template("report_email.html")
            html_body = template.render(
                report_type=report_type,
                metadata=metadata or {},
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            message.attach(MIMEText(html_body, "html"))
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment["data"])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    message.attach(part)
            
            # Send email
            server = self._create_smtp_connection()
            text = message.as_string()
            server.sendmail(self.settings.smtp_from_email, recipient_email, text)
            server.quit()
            
            # Generate auto-response message
            auto_response = self._generate_auto_response(metadata)
            
            logger.info(f"Email sent successfully to {recipient_email}")
            
            return {
                "success": True,
                "message_id": f"email_{datetime.now().timestamp()}",
                "status": "sent",
                "timestamp": datetime.now().isoformat(),
                "auto_response": auto_response
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise AppException(f"Email sending failed: {str(e)}", 500)
    
    def _generate_auto_response(self, metadata: Dict[str, Any]) -> str:
        """Generate automatic response message based on metadata"""
        if not metadata:
            return "Report sent successfully."
        
        cleaned_rows = metadata.get("cleanedRows", 0)
        total_value = metadata.get("totalValue", 0)
        currency = metadata.get("currency", "EUR")
        
        return f"success, {cleaned_rows} rows cleaned to the value of {total_value} {currency.lower()}."
    
    def send_notification_email(
        self,
        recipient_email: str,
        subject: str,
        message: str,
        template_name: str = "notification_email.html"
    ) -> Dict[str, Any]:
        """
        Send notification email
        
        Args:
            recipient_email: Email address to send to
            subject: Email subject
            message: Email message content
            template_name: Template file name
            
        Returns:
            Dictionary with success status and message_id
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.settings.smtp_from_email
            msg["To"] = recipient_email
            msg["Subject"] = subject
            
            # Generate email body from template
            template = self.template_env.get_template(template_name)
            html_body = template.render(
                message=message,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            msg.attach(MIMEText(html_body, "html"))
            
            # Send email
            server = self._create_smtp_connection()
            text = msg.as_string()
            server.sendmail(self.settings.smtp_from_email, recipient_email, text)
            server.quit()
            
            logger.info(f"Notification email sent successfully to {recipient_email}")
            
            return {
                "success": True,
                "message_id": f"notification_{datetime.now().timestamp()}",
                "status": "sent",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification email: {e}")
            raise AppException(f"Notification email sending failed: {str(e)}", 500)