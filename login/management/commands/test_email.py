# login/management/commands/test_email_detailed.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
import socket

class Command(BaseCommand):
    help = 'Testar envio de email com diagnóstico detalhado'

    def handle(self, *args, **options):
        self.stdout.write("=== TESTE DETALHADO DE EMAIL ===")
        
        # Teste de conexão SMTP
        try:
            self.stdout.write("1. Testando conexão SMTP...")
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.ehlo()
            if settings.EMAIL_USE_TLS:
                server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            self.stdout.write(self.style.SUCCESS("✓ Conexão SMTP bem-sucedida"))
            server.quit()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Erro na conexão SMTP: {e}"))
            return

        # Teste de envio de email via Django
        try:
            self.stdout.write("2. Enviando email via Django...")
            send_mail(
                'Teste de Email - Sistema de Agenda',
                'Este é um email de teste detalhado.',
                settings.DEFAULT_FROM_EMAIL,
                ['andernet@gmail.com'],  # Enviar para si mesmo
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("✓ Email enviado via Django"))
        except BadHeaderError:
            self.stdout.write(self.style.ERROR("✗ Cabeçalho de email inválido"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Erro ao enviar email: {e}"))

        self.stdout.write("3. Verifique a caixa de spam e lixeira do Gmail")