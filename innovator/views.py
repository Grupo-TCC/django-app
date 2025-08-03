from django.shortcuts import render, redirect
from innovator.forms import LoginForms, CustomUserCreationForm
from django.contrib import messages
from django.contrib import auth



def index(request):
    
    return render (request, 'innovator/index.html')



def register(request):
    form_submitted = False
    register_form = CustomUserCreationForm()
    login_form = LoginForms()
    
    if request.method == 'POST':
        if 'register_submit' in request.POST:        
        
            form_submitted = True
            register_form = CustomUserCreationForm(request.POST)

            if register_form.is_valid():
                password1 = register_form.cleaned_data.get('password1')
                password2 = register_form.cleaned_data.get('password2')

                if password1 != password2:
                    messages.warning(request, 'Senhas diferentes')
                    return redirect('register')

                register_form.save()
                messages.success(request, 'Conta criada com sucesso!')
                return redirect('register')
            else:
                print(register_form.errors)
                messages.error(request, 'Erro ao criar conta. Verifique os campos.')
                return redirect('register')

        elif 'login_submit' in request.POST:
            login_form = LoginForms(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data.get('email')
                password = login_form.cleaned_data.get('password')

                user = auth.authenticate(request, email=email, password=password)
                if user is not None:
                    auth.login(request, user)
                    messages.success(request, f'Bem-vindo, {user.fullname}!')
                    return redirect('feed:home')  # Replace with your actual feed page URL name
                else:
                    messages.error(request, 'Email ou senha inválidos.')
    
    return render(request, 'innovator/register.html', {
        'register_form': register_form,
        'login_form': login_form,
        'form_submitted': form_submitted
    })
