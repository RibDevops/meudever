# login/tests/test_password_reset.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

User = get_user_model()

class PasswordResetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='andernet@gmail.com',
            password='oldpassword123'
        )

    def test_password_reset_flow(self):
        # 1. Solicitar reset
        response = self.client.post(reverse('login:password_reset'), {
            'email': 'andernet@gmail.com'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to done page
        
        # 2. Verificar se email foi enviado
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Recuperação de Senha', mail.outbox[0].subject)
        
        # 3. Extrair link do email (simplificado)
        email_body = mail.outbox[0].body
        self.assertIn('reset', email_body)