import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from django.conf import settings

class EmailService:
    def load_template(self, file_path, replacements):
        """Load and replace placeholders in the email template."""
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        for key, value in replacements.items():
            html_content = html_content.replace(f'{{{{{key}}}}}', str(value))
        
        return html_content
    def send_order_email(self, email, customer_name, order_number, total_price):
        msg = MIMEMultipart("alternative")
        msg['From'] = settings.sender_email
        msg['To'] = email
        msg['Subject'] = "Your Order Confirmation"

        # Load the email template
        replacements = {
            "customer_name": customer_name,
            "order_number": order_number,
            "total_price": total_price,
        }
        html_body = render_to_string("emails/order_email_template.html", replacements)

        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP_SSL(settings.PROTOCOL, settings.PORT) as server:
                server.login(settings.sender_email, settings.sender_password)
                server.sendmail(settings.sender_email, email, msg.as_string())
                print(f"Email sent successfully to {email}")
        except Exception as e:
            print(f"Error: unable to send email to {email}: {e}")

email_service = EmailService()

