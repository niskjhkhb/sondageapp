from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm
from django.shortcuts import redirect
# Create your views here.


def profile(request):
    if request.user.is_authenticated:
        return render(request, 'users/profile.html')
    else:
        messages.error(request, 'You need to be logged in to view this page.')
        return redirect('login')

#inscription
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username= form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
            form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')



def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')





        
