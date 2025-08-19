from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests
import json
from .models import User
from .forms import SignUpForm, ProfileForm

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

def github_oauth_login(request):
    """Initiate GitHub OAuth login"""
    github_client_id = settings.GITHUB_CLIENT_ID
    if not github_client_id:
        messages.error(request, 'GitHub OAuth is not configured.')
        return redirect('login')
    
    redirect_uri = request.build_absolute_uri('/accounts/github/callback/')
    github_auth_url = f"https://github.com/login/oauth/authorize?client_id={github_client_id}&redirect_uri={redirect_uri}&scope=user:email"
    
    return redirect(github_auth_url)

def github_oauth_callback(request):
    """Handle GitHub OAuth callback"""
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'GitHub authentication failed.')
        return redirect('login')
    
    # Exchange code for access token
    token_url = 'https://github.com/login/oauth/access_token'
    token_data = {
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET,
        'code': code,
    }
    
    headers = {'Accept': 'application/json'}
    token_response = requests.post(token_url, data=token_data, headers=headers)
    
    if token_response.status_code != 200:
        messages.error(request, 'Failed to get access token from GitHub.')
        return redirect('login')
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    if not access_token:
        messages.error(request, 'No access token received from GitHub.')
        return redirect('login')
    
    # Get user info from GitHub
    user_url = 'https://api.github.com/user'
    user_headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    user_response = requests.get(user_url, headers=user_headers)
    if user_response.status_code != 200:
        messages.error(request, 'Failed to get user info from GitHub.')
        return redirect('login')
    
    github_user = user_response.json()
    
    # Get user email (might be private)
    email_url = 'https://api.github.com/user/emails'
    email_response = requests.get(email_url, headers=user_headers)
    emails = email_response.json() if email_response.status_code == 200 else []
    primary_email = next((email['email'] for email in emails if email['primary']), github_user.get('email'))
    
    # Create or get user
    try:
        user = User.objects.get(github_id=str(github_user['id']))
        # Update existing user info
        user.github_username = github_user['login']
        user.avatar_url = github_user['avatar_url']
        if primary_email and not user.email:
            user.email = primary_email
        user.save()
    except User.DoesNotExist:
        # Create new user
        username = github_user['login']
        # Ensure unique username
        counter = 1
        original_username = username
        while User.objects.filter(username=username).exists():
            username = f"{original_username}_{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=primary_email or '',
            github_id=str(github_user['id']),
            github_username=github_user['login'],
            first_name=github_user.get('name', '').split(' ')[0] if github_user.get('name') else '',
            last_name=' '.join(github_user.get('name', '').split(' ')[1:]) if github_user.get('name') else '',
            bio=github_user.get('bio', ''),
            avatar_url=github_user['avatar_url']
        )
    
    login(request, user)
    messages.success(request, f'Successfully logged in with GitHub as {user.username}!')
    return redirect('home')
