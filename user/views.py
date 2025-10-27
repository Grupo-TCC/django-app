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


def sobre(request):
    """
    View for the About page (Sobre o InnovaSus)
    """
    return render(request, 'user/sobre.html')


def politica_privacidade(request):
    """
    View for the Privacy Policy page (Política de Privacidade)
    """
    return render(request, 'user/politica_privacidade.html')


def termos_de_uso(request):
    """
    View for the Terms of Service page (Termos de Uso)
    """
    return render(request, 'user/termos_de_uso.html')


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
                user.is_active = False  # User needs to verify email first
                user.email_verified = False
                user.save()
                
                # Create UserVerification record with Lattes link
                verification_link = register_form.cleaned_data.get('verification_link')
                verification = UserVerification.objects.create(
                    user=user,
                    link=verification_link,
                    status="PENDING"
                )
                
                # Generate email verification token and link
                token = email_verification_token.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verification_url = request.build_absolute_uri(
                    reverse('user:verify_email', kwargs={'uidb64': uid, 'token': token})
                )
                
                # Send email verification to user directly
                subject = "InnovaSus - Verifique seu email para ativar sua conta"
                message = f"""
Olá {user.fullname},

Obrigado por se cadastrar no InnovaSus! 

Para ativar sua conta, clique no link abaixo:
{verification_url}

IMPORTANTE: Suas credenciais serão verificadas através do link Lattes que você forneceu. 
Contas com informações inconsistentes podem ser removidas.

Se você não se cadastrou no InnovaSus, ignore este email.

Atenciosamente,
Equipe InnovaSus
                """
                
                try:
                    # Debug email settings
                    print(f"📧 Attempting to send email:")
                    print(f"   From: {settings.EMAIL_HOST_USER}")
                    print(f"   To: {user.email}")
                    print(f"   Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
                    print(f"   Password set: {bool(settings.EMAIL_HOST_PASSWORD)}")
                    
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email],
                        fail_silently=False
                    )
                    print("✅ Email sent successfully!")
                    
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True, 
                            'message': 'Cadastro realizado! Verifique seu email para ativar sua conta.'
                        })
                    messages.success(request, 'Cadastro realizado com sucesso! Verifique seu email para ativar sua conta.')
                    return redirect('user:register')
                    
                except Exception as e:
                    # Log detailed error information
                    print(f"❌ Email sending failed: {str(e)}")
                    print(f"   Error type: {type(e).__name__}")
                    import traceback
                    print(f"   Traceback: {traceback.format_exc()}")
                    
                    # TEMPORARY: Auto-activate user if email fails (for testing)
                    # TODO: Remove this in production and fix email issue
                    if 'test' in str(e).lower() or 'smtp' in str(e).lower():
                        print("🔧 Auto-activating user due to email failure...")
                        user.is_active = True
                        user.email_verified = True
                        user.save()
                        verification.status = "APPROVED"
                        verification.save()
                        
                        warning_msg = 'Cadastro realizado! (Email temporariamente indisponível - conta ativada automaticamente)'
                        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                            return JsonResponse({
                                'success': True, 
                                'message': warning_msg
                            })
                        messages.warning(request, warning_msg)
                        return redirect('user:register')
                    
                    # Delete the user if email sending fails
                    user.delete()
                    if verification:
                        verification.delete()
                    
                    error_msg = f'Erro ao enviar email de verificação: {str(e)}'
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False, 
                            'message': error_msg
                        }, status=500)
                    messages.error(request, error_msg)
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
                    # Add Lattes verification warning message
                    messages.info(request, 'IMPORTANTE: Suas credenciais serão verificadas através do link Lattes fornecido. Contas com informações inconsistentes podem ser removidas.')
                    
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


def verify_email(request, uidb64, token):
    """
    Handle email verification for new user registrations
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user and email_verification_token.check_token(user, token):
        # Activate the user account
        user.is_active = True
        user.email_verified = True
        user.save()
        
        # Update verification status
        verification = UserVerification.objects.filter(user=user).first()
        if verification:
            verification.status = "APPROVED"
            verification.save()
        
        messages.success(request, f"Email verificado com sucesso! Sua conta está ativa. Faça login abaixo.")
        return redirect('user:register')
    else:
        messages.error(request, "Link de verificação inválido ou expirado.")
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

