from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import  authenticate,login,logout

def home(request):
    return  render(request,'home.html')

def create(request):
    return  render(request,'create.html')

def store(request):
    data = {}
    if(request.POST['password']!=request.POST['password-conf']):
       data['msg'] = 'As senhas estão diferentes!'
       data['class'] = ' alert-danger'
    else:
        user = User.objects.create_user(request.POST['user'],request.POST['email'],request.POST['password'])
        user.first_name = request.POST['name']
        user.save()
        user.user_permissions.add( )
        data['msg'] = 'Usuário cadastrado com sucesso!'
        data['class'] = ' alert-success'

    return  render(request,'create.html',data)

def painel(request):
    return  render(request,'painel.html')

def dologin(request):
    data = {}
    user = authenticate(username=request.POST['user'],password=request.POST['password'])
    if user is not None:
       login(request, user)
       return redirect('/dashboard/')
    else:
        data['msg'] = 'Usuário ou Senha inválidos!'
        data['class'] = ' alert-danger'
        return  render(request,'painel.html',data)

def dashboard(request):
    return  render(request, 'dashboard/home.html')

def logouts(request):
    logout(request)
    return  redirect('/painel/')

def changePassword(request):
    user = User.objects.get(email=request.user.email)
    user.set_password(request.POST['password'])
    user.save()
    logout(request)
    return render(request, 'painel.html')