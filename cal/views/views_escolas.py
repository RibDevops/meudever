from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from..forms import EscolaForm
from..models import Escola
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

#@login_required
def lista_escolas(request):
    escolas = Escola.objects.all()
    return render(request, 'escolas/lista.html', {'escolas': escolas})

#@login_required
def cria_escolas(request):
    if request.method == 'POST':
        form = EscolaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Escola cadastrada com sucesso.")
            return redirect('cal:lista_escolas')
    else:
        form = EscolaForm()
    return render(request, 'escolas/form.html', {'form': form})

#@login_required
def atualiza_escolas(request, pk):
    print(pk)
    escola = get_object_or_404(Escola, pk=pk)
    print(escola)
    if request.method == 'POST':
        form = EscolaForm(request.POST, instance=escola)
        if form.is_valid():
            form.save()
            messages.success(request, "Atualizado com sucesso.")

            return redirect('cal:lista_escolas')
    else:
        form = EscolaForm(instance=escola)
    return render(request, 'escolas/form.html', {'form': form})

# def deleta_escolas(request, pk):
#     escola = get_object_or_404(Escola, pk=pk)
#     if request.method == 'POST':
#         escola.delete()
#         messages.success(request, "Escola deletada com sucesso.")
#         return redirect('cal:lista_escolas')
#     return render(request, 'escolas/confirma_delecao.html', {'escola': escola})


#@login_required
def deleta_escolas(request, pk):
    escola = get_object_or_404(Escola, pk=pk)
    try:
        escola.delete()
        messages.success(request, "Escola deletada com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao deletar escola: {str(e)}")
    return redirect('cal:lista_escolas')
