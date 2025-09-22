from django.http import JsonResponse
from ..models import Professor, Materia, Livro, Turma

def get_professores_by_escola(request, escola_id):
    professores = Professor.objects.filter(fk_escola_id=escola_id)  # Corrigido o filtro
    data = [{'id': prof.id, 'nome': prof.nome_professor} for prof in professores]
    return JsonResponse(data, safe=False)

def get_turmas_by_escola(request, escola_id):
    # print(escola_id)
    turmas = Turma.objects.filter(fk_escola_id=escola_id)
    # print(turmas)
    data = [{'id': turma.id, 'nome': turma.turma} for turma in turmas]
    # print(data)

    return JsonResponse(data, safe=False)

def get_materia_by_professor(request, professor_id):
    print(professor_id)
    try:
        print(professor_id)
        professor = Professor.objects.get(id=professor_id)
        materia = {'id': professor.fk_materia.id, 'nome': professor.fk_materia.nome_materia}
        return JsonResponse(materia)
    except Professor.DoesNotExist:
        return JsonResponse({'error': 'Professor não encontrado'}, status=404)

def get_livros_by_materia(request, materia_id):
    livros = Livro.objects.filter(fk_materia_id=materia_id)
    data = [{'id': livro.id, 'nome': livro.nome_livro} for livro in livros]
    return JsonResponse(data, safe=False)

def get_livros_ajax(request, materia_id, escola_id):
    print(f'materia_id: {materia_id} e escola_id: {escola_id}')
    livros = Livro.objects.filter(fk_materia_id=materia_id, fk_escola_id=escola_id)
    print(f'livros: {livros}')
    data = [{"id": livro.id, "nome": livro.nome_livro} for livro in livros]
    return JsonResponse(data, safe=False)