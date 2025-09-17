from django.shortcuts import render, redirect, get_object_or_404
from..forms import LivrosForm
from..models import Livro
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

#@login_required
def lista_livro(request):
    livros = Livro.objects.all()
    return render(request, 'livros/lista.html', {'livros': livros})

#@login_required
def cria_livro(request):
    if request.method == 'POST':
        form = LivrosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Livro cadastrado com sucesso.")
            return redirect('cal:lista_livro')
    else:
        form = LivrosForm()
    return render(request, 'livros/form.html', {'form': form})

#@login_required
def atualiza_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == 'POST':
        form = LivrosForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, "Atualizado com sucesso.")

            return redirect('cal:lista_livro')
    else:
        form = LivrosForm(instance=livro)
    return render(request, 'livros/form.html', {'form': form})


#@login_required
def deleta_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    try:
        livro.delete()
        messages.success(request, "Livro deletado com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao deletar: {str(e)}")
    return redirect('cal:lista_livro')