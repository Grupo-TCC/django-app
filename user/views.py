from django.shortcuts import render, redirect, get_object_or_404
from user.forms import LoginForms, CustomUserCreationForm, UserVerificationForm
from django.contrib import messages
from .models import User, Follow, UserVerification
from .forms import ProfilePictureForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
                # Build verification link
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                verify_url = request.build_absolute_uri(
                    reverse('user:verify_email', args=[uidb64, token])
                )
                subject = "Verifique seu email para acessar o Innovator"
                body = f"Clique para confirmar seu email e entrar (link expira em breve):\n{verify_url}"
                try:
                    sent = send_mail(subject, body, None, [user.email])
                    if sent != 1:
                        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                            return JsonResponse({'success': False, 'message': 'Não foi possível enviar o email de verificação.'}, status=500)
                        messages.error(request, 'Não foi possível enviar o email de verificação.')
                        return redirect('user:register')
                except Exception as e:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': f'Falha ao enviar email: {e}'}, status=500)
                    messages.error(request, f'Falha ao enviar email: {e}')
                    return redirect('user:register')
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Enviamos um link de acesso ao seu email!'})
                messages.success(request, 'Enviamos um link de acesso ao seu email!')
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
    
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None
        
    if user is None or not default_token_generator.check_token(user, token):
        # invalid or expired link
        messages.error(request, 'Link de verificação inválido ou expirado')
        return redirect('user:register')
    
    # ensure UserVerification exists
    verification, _ = UserVerification.objects.get_or_create(user=user)

    if request.method == "POST":
        form = UserVerificationForm(request.POST, instance=verification)
        if form.is_valid():
            form.save()
            messages.success(request, "Seu link foi enviado para verificação pelo administrador.")
            return redirect("user:register")
    else:
        form = UserVerificationForm(instance=verification)

    return render(request, "user/verification_form.html", {"form": form})
    
    


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
        messages.error(request, "Usuário inválido.")
        return redirect('user:register')

    # Validate token
    if default_token_generator.check_token(user, token):
        login(request, user)
        return redirect('feed:home')

    # bad/expired token
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

