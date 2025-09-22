# accounts/views.py
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

logger = logging.getLogger(__name__)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        logger.info(f"Tentativa de reset de senha para: {email}")
        print(f"DEBUG: Processando reset para: {email}")
        
        User = get_user_model()
        active_users = User.objects.filter(email__iexact=email, is_active=True)
        
        if active_users.exists():
            print(f"DEBUG: Usuário encontrado, enviando email para: {email}")
            # Para cada usuário ativo com este email, enviar email
            for user in active_users:
                self.send_custom_reset_email(user, email)
            
            return super().form_valid(form)
        else:
            print(f"DEBUG: Usuário não encontrado ou inativo: {email}")
            # Mesmo assim, redireciona para a página de sucesso (por segurança)
            return super().form_valid(form)
    
    def send_custom_reset_email(self, user, email):
        """Envia email personalizado de recuperação de senha"""
        context = {
            'email': email,
            'domain': self.request.META['HTTP_HOST'],
            'site_name': 'Sistema de Agenda',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'https' if self.request.is_secure() else 'http',
        }
        
        # Renderizar subject
        subject = render_to_string(self.subject_template_name, context)
        subject = ''.join(subject.splitlines())  # Remove quebras de linha
        
        # Renderizar conteúdo HTML
        html_content = render_to_string(self.email_template_name, context)
        
        # Renderizar conteúdo texto (fallback)
        text_content = f"""Recuperação de Senha - Sistema de Agenda

Olá,

Você solicitou a recuperação de senha para sua conta no Sistema de Agenda.

Email associado: {email}

Para redefinir sua senha, acesse o link:
{context['protocol']}://{context['domain']}/reset/{context['uid']}/{context['token']}/

IMPORTANTE:
- Este link expira em 24 horas
- Se você não solicitou esta recuperação, ignore este email

© Sistema de Agenda. Todos os direitos reservados."""
        
        # Criar e enviar email
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=None,  # Usa DEFAULT_FROM_EMAIL das settings
            to=[email],
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()
        
        print(f"DEBUG: Email HTML enviado para: {email}")


# accounts/views.py
def send_custom_reset_email(self, user, email):
    """Envia email personalizado de recuperação de senha"""
    from django.urls import reverse
    
    context = {
        'email': email,
        'domain': self.request.META['HTTP_HOST'],
        'site_name': 'Sistema de Agenda',
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': 'https' if self.request.is_secure() else 'http',
    }
    
    # Adiciona a URL completa ao contexto
    reset_url = reverse('password_reset_confirm', kwargs={
        'uidb64': context['uid'],
        'token': context['token']
    })
    context['reset_url'] = f"{context['protocol']}://{context['domain']}{reset_url}"
    
    # Renderizar conteúdo HTML
    html_content = render_to_string(self.email_template_name, context)
    # ... resto do código


