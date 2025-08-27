from django.shortcuts import render, redirect
from user.forms import LoginForms, CustomUserCreationForm
from django.contrib import messages
from .models import InnovatorVerification
from .forms import InnovatorVerificationForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model, authenticate, login
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

User = get_user_model()

def index(request):
    
    return render (request, 'user/index.html')



def register(request):
    # form_submitted = False
    register_form = CustomUserCreationForm()
    login_form = LoginForms()
    
    if request.method == 'POST':
        if 'register_submit' in request.POST:           
            # form_submitted = True
            register_form = CustomUserCreationForm(request.POST)
            
            pwd1 = request.POST.get('password1')
            pwd2 = request.POST.get('password2')

            if pwd1 != pwd2:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':                   
                    return JsonResponse({'success': False, 'message': 'Senhas diferentes, tente novamente'}, status=400)
                messages.error(request, 'Senhas diferentes, tente novamente')
                return redirect ('user:register')
                    
            if register_form.is_valid():       
                # Create inactive user, do NOT auto-login now
                user = register_form.save(commit=False)
                user.is_active = False  # <— important
                user.email_verified = False
                user.save()
                
                # Build verification link
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                verify_url = request.build_absolute_uri(
                    reverse('user:verify_email', args=[uidb64, token])
                )
                
                # Send email
                subject = "Verifique seu email para acessar o Innovator"
                body = f"Clique para confirmar seu email e entrar (link expira em breve):\n{verify_url}"
                
                # Send email with error handling
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
                    return JsonResponse(
                    {'success': True, 'message': 'Enviamos um link de acesso ao seu email!'}
                )
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
                        return JsonResponse({'success': True, 'message': f'Bem-vindo, {user.fullname}!', 'redirect': reverse('feed:home')})
                    
                    return redirect('feed:home')                
                    
                
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
    
    # Mark email verified
    if not user.email_verified:
        user.email_verified = True
        user.save(update_fields=['email_verified'])

    if user.user_type == 'Re':
        user.is_active = True  # mark email verified
        user.save(update_fields=['is_active'])
        login(request, user)   # first login happens here
        
        return redirect('feed:home')
    
    # Innovators: verified email, but NOT active yet
    # Send them to identity (doc upload) step.
    # Optionally re-issue a fresh token for the next step:
    next_token = default_token_generator.make_token(user)
    return redirect(reverse('user:innovator_identity', args=[uidb64, next_token]))
    

def innovator_identity(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid, user_type='In')
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        return redirect('user:register')

    if request.method == "POST":
        form = InnovatorVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            obj, _ = InnovatorVerification.objects.get_or_create(user=user)
            obj.applicant_type = form.cleaned_data["applicant_type"]
            obj.title = form.cleaned_data["title"]
            obj.document = form.cleaned_data["document"]
            obj.status = "PENDING"
            obj.save()
            # Save M2M after obj.save()
            if "research_areas" in form.cleaned_data:
                obj.research_areas.set(form.cleaned_data["research_areas"])
            return redirect('user:innovator_identity_done')
    else:
        form = InnovatorVerificationForm()

    return render(request, 'auth/innovator_identity.html', {"form": form, "user": user})

def innovator_identity_done(request):
    return render(request, 'auth/innovator_identity_done.html')

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

    if not user:
        return redirect('user:register')

    # Must be verified and active at this point
    if not user.email_verified or not user.is_active:
        return redirect('user:register')

    # Validate token
    if default_token_generator.check_token(user, token):
        login(request, user)
        return redirect('feed:home')

    # bad/expired token
    return redirect('user:register')