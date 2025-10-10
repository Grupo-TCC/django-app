from django.shortcuts import render, redirect, get_object_or_404
from user.forms import LoginForms, CustomUserCreationForm
from django.contrib import messages
from .models import User, Follow, UserVerification
from .forms import ProfilePictureForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Custom token generator for email verification that doesn't depend on is_active status
    """
    def _make_hash_value(self, user, timestamp):
        # Only use user pk, email and timestamp - not is_active or last_login
        return str(user.pk) + user.email + str(timestamp)

email_verification_token = EmailVerificationTokenGenerator()


User = get_user_model()

def index(request):
    
    return render (request, 'user/index.html')



def register(request):
    # form_submitted = False
    register_form = CustomUserCreationForm()
    login_form = LoginForms()
    
    if request.method == 'POST':
        if 'register_submit' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            pwd1 = request.POST.get('password1')
            pwd2 = request.POST.get('password2')
            if pwd1 != pwd2:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Senhas diferentes, tente novamente'}, status=400)
                messages.error(request, 'Senhas diferentes, tente novamente')
                return redirect('user:register')
            if register_form.is_valid():
                user = register_form.save(commit=False)
                user.is_active = False
                user.email_verified = False
                user.save()
                
                # Create UserVerification record directly
                verification_link = register_form.cleaned_data.get('verification_link')
                verification = UserVerification.objects.create(
                    user=user,
                    link=verification_link,
                    status="PENDING"
                )
                
                # Send admin notification email
                admin_subject = f"Nova solicitação de verificação - {user.fullname}"
                admin_body = f"""
Nova solicitação de verificação de usuário:

Nome: {user.fullname}
Email: {user.email}

Link de verificação: {verification_link}

Para aprovar ou rejeitar, acesse o painel administrativo.
                """
                
                try:
                    # Send notification to admins 
                    admin_emails = [settings.EMAIL_HOST_USER]  # Use the same email as the sender for now
                    sent = send_mail(admin_subject, admin_body, None, admin_emails, fail_silently=False)
                    
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'message': 'Cadastro realizado com sucesso! Você receberá o email de acesso caso sua solicitação seja aprovada.'})
                    messages.success(request, 'Cadastro realizado com sucesso! Você receberá o email de acesso caso sua solicitação seja aprovada.')
                    return redirect('user:register')
                    
                except Exception as e:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': f'Falha ao enviar notificação: {e}'}, status=500)
                    messages.error(request, f'Cadastro realizado, mas falha ao notificar administrador: {e}')
                    return redirect('user:register')
            # Form invalid → return all errors
            errors = [e for field in register_form.errors.values() for e in field]
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            for error in errors:
                messages.error(request, error)
            return redirect('user:register')

        elif 'login_submit' in request.POST:
            login_form = LoginForms(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data.get('email')
                password = login_form.cleaned_data.get('password')

                user = authenticate(request, email=email, password=password)
                if user is not None:
                    if not user.is_active:
                        # Still unverified
                            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                                return JsonResponse({'success': False, 'message': 'Verifique seu email antes de entrar.'}, status=400)
                            messages.error(request, 'Verifique seu email antes de entrar.')
                            return redirect('user:register')
                    
                    login(request, user)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'message': f'Bem-vindo, {user.fullname}!', 'redirect': reverse('feed:artigos')})
                    
                    return redirect('feed:artigos')                
                    
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': 'Email ou senha inválidos.'}, status=400)
                messages.error(request, 'Email ou senha inválidos.')
                return redirect('user:register')
            
            # Login form invalid
            errors = [e for field in login_form.errors.values() for e in field]
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            for error in errors:
                messages.error(request, error)
            return redirect('user:register')
    
    return render(request, 'user/register.html', {
        'register_form': register_form,
        'login_form': login_form,
    })

def custom_logout(request):
    logout(request)
    return redirect('user:register') 
    



def auto_login(request, uidb64, token):
    """
    One-time login link. Works only if:
    - token is valid
    - user is active
    - email_verified is True
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if not user or not user.email_verified or not user.is_active:
        messages.error(request, "Link inválido ou conta não aprovada.")
        return redirect('user:register')

    # Validate token using our custom token generator
    if email_verification_token.check_token(user, token):
        login(request, user)
        messages.success(request, f"Bem-vindo, {user.fullname}!")
        return redirect('feed:artigos')  # Updated redirect to match LOGIN_REDIRECT_URL

    # bad/expired token
    messages.error(request, "Link de acesso expirado ou inválido.")
    return redirect('user:register')


@login_required
def change_profile_picture(request):
    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("feed:settings")  # redirect to your homepage or profile
    else:
        form = ProfilePictureForm(instance=request.user)

    return redirect("feed:settings")

