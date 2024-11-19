from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.contrib.auth.models import User

# Create your models here.
class Categoria(models.Model):
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.FloatField()
    descricao = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING)
    imagem = models.ImageField(null=True, blank=True, upload_to="images/")
    def __str__(self):
        return self.nome
    
class SacolaManager(models.Manager):
    def new_or_get(self, request):
        sacola_id = request.session.get('sacola_id', None)
        qs = self.get_queryset().filter(id=sacola_id)
        if qs.count() == 1:
            new_obj = False
            sacola_obj = qs.first()
            if request.user.is_authenticated and sacola_obj.user is None:
                sacola_obj.user = request.user
                sacola_obj.save()
        else:
            sacola_obj = Sacola.objects.new(user=request.user)
            new_obj = True
            request.session['sacola_id'] = sacola_obj.id
        return sacola_obj, new_obj
    
    def new(self, user=None):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
                self.model.objects.filter(user=user_obj).delete()
        return self.model.objects.create(user=user_obj)
    

class Sacola(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, null=True, blank=True)
    produtos = models.ManyToManyField(Produto, blank=True)
    subtotal = models.DecimalField(default=0.0, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = SacolaManager()

    def __str__(self):
        return str(self.id)
    
class Endereco(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enderecos")
    rua = models.CharField(max_length=500)
    numero = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    complemento = models.CharField(max_length=500)
    cep = models.CharField(max_length=20)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rua}, {self.numero}, {self.complemento} / {self.cidade} - {self.estado}"
    
class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('enviado', 'Enviado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True)
    forma_pagamento = models.CharField(max_length=20, choices=[
        ('pix', 'Pix'),
        ('credito', 'Cartão de Crédito'),
        ('debito', 'Cartão de Débito'),
        ('dinheiro', 'Dinheiro'),
    ])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.user.username}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"    
    
def m2m_changed_sacola_receiver(sender, instance, action, *args, **kwargs):
  #print(action)
  if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
    #print(instance.produtos.all())
    #print(instance.total)
    produtos = instance.produtos.all() 
    total = 0 
    for produto in produtos: 
      total += produto.preco 
    if instance.subtotal != total:
      instance.subtotal = total
      instance.save()
    #print(total) 
    instance.subtotal = total
    instance.save()

m2m_changed.connect(m2m_changed_sacola_receiver, sender = Sacola.produtos.through)

def pre_save_sacola_receiver(sender, instance, *args, **kwargs):
    if instance.subtotal > 0:
        instance.total = instance.subtotal + 5 # considere o 5 como uma taxa de entrega
    else:
        instance.total = 0.00
pre_save.connect(pre_save_sacola_receiver, sender = Sacola)