from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import  authenticate,login,logout
from app.models import Categoria, Produto, Sacola

def home(request):
    if request.user.is_authenticated:
        return redirect('/newdashboard/')
    else:
        return  render(request,'home.html')

def create(request):
    if request.user.is_authenticated:
        return redirect('/newdashboard/')
    else:
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
    if request.user.is_authenticated:
        return redirect('/newdashboard/')
    else:
        return  render(request,'painel.html')

def dologin(request):
    data = {}
    user = authenticate(username=request.POST['user'],password=request.POST['password'])
    if user is not None:
       login(request, user)
       return redirect('/newdashboard/')
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

def newdashboard(request):
    data = {}
    data['db'] = Produto.objects.all()
    data['ct'] = Categoria.objects.all()
    return  render(request,'dashboard/dashboard.html', data)

def profile(request):    
    return  render(request,'dashboard/profile.html')

def contatos(request):    
    return  render(request,'dashboard/contatos.html')

def sacola(request):
    data = {}
    sacola_obj, new = Sacola.objects.new_or_get(request)
    print('Sacola salva: ', sacola_obj.pk is not None)
    if not sacola_obj.pk:
       sacola_obj.save()
    sacola_produtos = sacola_obj.produtos.all()
    data['pd'] = sacola_produtos
    data['st'] = sacola_obj.subtotal
    data['total'] = sacola_obj.total
    return render(request, 'dashboard/sacola.html', data)

def add_sacola(request):
    if request.method == "POST":
        produto_id = request.POST.get('produto_id')  # ID do produto enviado pelo AJAX
        sacola_obj, _ = Sacola.objects.new_or_get(request)  # Obtém ou cria uma sacola
        produto = get_object_or_404(Produto, id=produto_id)

        sacola_obj.produtos.add(produto)  # Adiciona o produto à sacola
        sacola_obj.save()

        # Retorna dados da sacola atualizada
        return JsonResponse({
            'mensagem': 'Produto adicionado com sucesso!',
            'subtotal': float(sacola_obj.subtotal),
            'total': float(sacola_obj.total),
        })

    return JsonResponse({'mensagem': 'Requisição inválida'}, status=400)

def remove_sacola(request):
    if request.method == "POST":
        produto_id = request.POST.get("produto_id")
        sacola_id = request.session.get('sacola_id')
        if sacola_id:
            try:
                sacola = Sacola.objects.get(id=sacola_id)
                produto = Produto.objects.get(id=produto_id)
                sacola.produtos.remove(produto)
                sacola.save()
                return JsonResponse({"message": "Produto removido com sucesso!"})
            except Sacola.DoesNotExist:
                return JsonResponse({"error": "Sacola não encontrada!"}, status=404)
            except Produto.DoesNotExist:
                return JsonResponse({"error": "Produto não encontrado!"}, status=404)
    return JsonResponse({"error": "Requisição inválida!"}, status=400)