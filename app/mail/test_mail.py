import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template


def load_email_template():
    with open("email_verification_template.html", "r") as file:
        return Template(file.read())

def send_test_email(receiver_email: str, verification_code: str):
    sender_email = "code-verification@frist-it.online"  # Укажи свой email
    sender_password = "pUavfGqaUQYpt5cBL7PU"  # Укажи пароль от почтового ящика
    smtp_server = "smtp.mail.ru"  # SMTP сервер Mail.ru
    smtp_port = 465  # Порт для SSL

    msg = MIMEMultipart()
    msg["Subject"] = "Test Email Verification"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    template = load_email_template()
    html_content = template.render(code=verification_code)
    msg.attach(MIMEText(html_content, "html"))


    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", str(e))



# Тестовый запуск
if __name__ == "__main__":
    test_receiver = "fristivan@mail.ru"  # Укажи тестовую почту
    test_code = "123456"
    send_test_email(test_receiver, test_code)