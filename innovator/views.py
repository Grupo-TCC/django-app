from django.shortcuts import render, redirect
from innovator.forms import LoginForms, CustomUserCreationForm
from django.contrib import messages


from django.http import JsonResponse
from django.contrib.auth import get_user_model, authenticate, login
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

def index(request):
    
    return render (request, 'innovator/index.html')



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
                return redirect ('register')
                    
            if register_form.is_valid():       
                # Create inactive user, do NOT auto-login now
                user = register_form.save(commit=False)
                user.is_active = False  # <— important
                user.save()
                
                # Build verification link
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                verify_url = request.build_absolute_uri(
                    reverse('verify_email', args=[uidb64, token])
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
                        return redirect('register')
                        
                except Exception as e:
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': f'Falha ao enviar email: {e}'}, status=500)
                    messages.error(request, f'Falha ao enviar email: {e}')
                    return redirect('register')
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(
                    {'success': True, 'message': 'Enviamos um link de acesso ao seu email!'}
                )
                messages.success(request, 'Enviamos um link de acesso ao seu email!')
                return redirect('register')
                    
            
            # Form invalid → return all errors
            errors = [e for field in register_form.errors.values() for e in field]
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            for error in errors:
                messages.error(request, error)
            return redirect('register')
                

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
                            return redirect('register')
                    
                    login(request, user)
                    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'message': f'Bem-vindo, {user.fullname}!', 'redirect': reverse('feed:home')})
                    
                    return redirect('feed:home')                
                    
                
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': 'Email ou senha inválidos.'}, status=400)
                messages.error(request, 'Email ou senha inválidos.')
                return redirect('register')
            
            # Login form invalid
            errors = [e for field in login_form.errors.values() for e in field]
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            for error in errors:
                messages.error(request, error)
            return redirect('register')
    
    return render(request, 'innovator/register.html', {
        'register_form': register_form,
        'login_form': login_form,
        
    })
    
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # mark email verified
        user.save(update_fields=['is_active'])
        login(request, user)   # first login happens here
        messages.success(request, 'Email verificado com sucesso!')
        return redirect('feed:home')
    
    messages.error(request, 'Link de verificação inválido ou expirado')
    return redirect('register')

