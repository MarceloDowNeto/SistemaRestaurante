"""
URL configuration for project project.
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from venv import create

from django.conf.urls.i18n import urlpatterns
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.views import  home,create,store,painel,dologin,dashboard,logouts,changePassword,newdashboard,profile,contatos,sacola,add_sacola,remove_sacola,add_endereco,edit_endereco,remove_endereco,concluir_pedido,confirmar_pedido,pedidos

urlpatterns =[
    path('admin/', admin.site.urls),
    path('',home),
    path('create/',create),
    path('store/',store),
    path('painel/',painel),
    path('dologin/',dologin),
    path('dashboard/',dashboard),
    path('logouts/',logouts),
    path('password/',changePassword),
    path('newdashboard/',newdashboard),
    path('profile/',profile),
    path('contatos/',contatos),
    path('sacola/',sacola),
    path('add_sacola/',add_sacola, name='add_sacola'),
    path('remove_sacola/', remove_sacola, name='remove_sacola'),
    path('add_endereco/', add_endereco, name='add_endereco'),
    path('edit_endereco/<int:endereco_id>/', edit_endereco, name='edit_endereco'),
    path('remove_endereco/<int:endereco_id>/', remove_endereco, name='remove_endereco'),
    path('concluir_pedido/', concluir_pedido, name='concluir_pedido'),
    path('confirmacao/<int:pedido_id>/', confirmar_pedido, name='confirmacao'),
    path('pedidos/', pedidos, name='pedidos'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)