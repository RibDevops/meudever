from django.shortcuts import render, redirect, get_object_or_404
from..forms import MateriaForm
from..models import Materia
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Views para Materia

#@login_required
def lista_materia(request):
    materia = Materia.objects.all()
    return render(request, 'materia/lista.html', {'materias': materia})

#@login_required
def cria_materia(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Matéria cadastrada com sucesso.")
            return redirect('cal:lista_materia')
    else:
        form = MateriaForm()
    return render(request, 'materia/form.html', {'form': form})

#@login_required
def atualiza_materia(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, "Atualizado com sucesso.")

            return redirect('cal:lista_materia')
    else:
        form = MateriaForm(instance=materia)
    return render(request, 'materia/form.html', {'form': form})


#@login_required
def deleta_materia(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    try:
        materia.delete()
        messages.success(request, "Matéria deletada com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao deletar escola: {str(e)}")
    return redirect('cal:lista_materia')