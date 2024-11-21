from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import  authenticate,login,logout
from app.models import Categoria, Produto, Sacola, Endereco, Pedido, ItemPedido
from app.pixqrcodegen import Payload

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
    data = {}
    enderecos = Endereco.objects.filter(user=request.user)
    data['enderecos'] = enderecos  
    return  render(request,'dashboard/profile.html', data)

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

def add_endereco(request):
    if request.method == "POST":
        rua = request.POST.get("rua")
        numero = request.POST.get("numero")
        cidade = request.POST.get("cidade")
        estado = request.POST.get("estado")
        complemento = request.POST.get("complemento")
        cep = request.POST.get("cep")
        Endereco.objects.create(user=request.user, rua=rua, numero=numero, cidade=cidade, estado=estado,complemento=complemento, cep=cep)
        return redirect('/profile/')  # Redireciona de volta para o perfil
    return render(request, 'dashboard/endereco_form.html')

def edit_endereco(request, endereco_id):
    endereco = get_object_or_404(Endereco, id=endereco_id, user=request.user)
    if request.method == "POST":
        endereco.rua = request.POST.get("rua")
        endereco.numero = request.POST.get("numero")
        endereco.cidade = request.POST.get("cidade")
        endereco.estado = request.POST.get("estado")
        endereco.complemento = request.POST.get("complemento")
        endereco.cep = request.POST.get("cep")
        endereco.save()
        return redirect('/profile/')  # Redireciona de volta para o perfil
    return render(request, 'dashboard/endereco_form.html', {'endereco': endereco})

def remove_endereco(request, endereco_id):
    endereco = get_object_or_404(Endereco, id=endereco_id, user=request.user)
    if request.method == "POST":
        endereco.delete()
        return redirect('/profile/')  # Redireciona de volta para o perfil
    return render(request, 'dashboard/confirm_remocao.html', {'endereco': endereco})

def concluir_pedido(request):
    sacola_obj, new = Sacola.objects.new_or_get(request)

    if sacola_obj.produtos.count() == 0:
        return redirect('/sacola/')  # Redireciona se a sacola estiver vazia

    enderecos = Endereco.objects.filter(user=request.user)
    if not enderecos.exists():  # Verifica se o usuário tem endereços salvos
        return redirect('add_endereco')

    if request.method == 'POST':
        endereco_id = request.POST.get('endereco')
        forma_pagamento = request.POST.get('forma_pagamento')
        endereco = get_object_or_404(Endereco, id=endereco_id)

        # Cria o pedido
        pedido = Pedido.objects.create(
            user=request.user,
            endereco=endereco,
            forma_pagamento=forma_pagamento,
            total=sacola_obj.total
        )

        # Adiciona os itens ao pedido
        for produto in sacola_obj.produtos.all():
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=1,
                preco=produto.preco
            )

        # Limpa a sacola
        sacola_obj.produtos.clear()
        return redirect('confirmacao', pedido_id=pedido.id)

    enderecos = Endereco.objects.filter(user=request.user)
    return render(request, 'dashboard/confirmar_pedido.html', {'sacola': sacola_obj, 'enderecos': enderecos})

def confirmar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if pedido.forma_pagamento == 'pix':
        payload = Payload('CARLOS MARCELO', 'mndowsley@gmail.com', f'{pedido.total}','Maceio','Eclipse Burger')
        payload.gerarPayload()
        codigo = payload.payload_completa
        payload.gerarQrCode(codigo, 'app\static')
        return render(request, 'dashboard/pix_qrcode.html', {'pedido': pedido, 'codigo':codigo})
    else:
        return render(request, 'dashboard/pedido_confirmado.html', {'pedido': pedido})
    
def pedidos(request):
    pedidos = Pedido.objects.filter(user=request.user).order_by('-criado_em')  # Mais recentes primeiro
    return render(request, 'dashboard/pedidos.html', {'pedidos': pedidos})
