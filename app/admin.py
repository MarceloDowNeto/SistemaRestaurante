from django.contrib import admin
from .models import Categoria, Produto, Sacola, Endereco, Pedido, ItemPedido

# Register your models here.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    pass

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'categoria')
    list_filter = ('categoria',)
    list_editable = ('preco',)
    search_fields = ('nome', 'descricao')

@admin.register(Sacola)
class SacolaAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    list_filter = ('user',)
    list_display_links = ('user',)

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('rua', 'user')
    list_filter = ('user',)

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0  # Não exibe campos extras para adicionar mais itens
    fields = ['produto', 'quantidade', 'preco']    

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'endereco', 'total', 'forma_pagamento', 'status', 'criado_em')
    inlines = [ItemPedidoInline]
    list_filter = ('user',)
    list_editable = ('status',)
    list_display_links = ('user',)
