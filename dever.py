{% extends 'base.html' %}
{% block content %}
<div class="container py-3">
    <div class="card shadow-sm">
        <div class="card-header bg-gradient-primary text-white">
            <h4 class="mb-0">
                <i class="fas fa-plus-circle me-2"></i>Adicionar Dever
            </h4>
        </div>
        <div class="card-body">
            <form method="post" id="dever-form">
                {% csrf_token %}

                {% if user.is_superuser %}
                    <!-- Superuser vê tudo -->
                    <div class="mb-3">
                        <label for="id_fk_escola" class="form-label">Escola</label>
                        <select id="id_fk_escola" name="fk_escola" class="form-control">
                            <option value="">Selecione</option>
                            {% for escola in escolas %}
                                <option value="{{ escola.id }}">{{ escola.nome_escola }}</option>
                            {% endfor %}
                        </select>
                    </div>
                {% elif user.tipo_usuario == "coordenador" %}
                    <!-- Coordenador já tem escola, mas mantemos o select escondido -->
                    <select id="id_fk_escola" name="fk_escola" class="form-control d-none">
                        <option value="{{ user.fk_escola.id }}" selected>
                            {{ user.fk_escola.nome_escola }}
                        </option>
                    </select>
                {% elif user.tipo_usuario == "professor" %}
                    <!-- Professor já tem escola, professor e matéria fixos, mas mantemos selects -->
                    <select id="id_fk_escola" name="fk_escola" class="form-control d-none">
                        <option value="{{ user.fk_professor.fk_escola.id }}" selected>
                            {{ user.fk_professor.fk_escola.nome_escola }}
                        </option>
                    </select>

                    <select id="id_fk_professor" name="fk_professor" class="form-control d-none">
                        <option value="{{ user.fk_professor.id }}" selected>
                            {{ user.fk_professor.nome_professor }}
                        </option>
                    </select>

                    <input type="hidden" id="id_fk_materia_id" name="fk_materia" value="{{ user.fk_professor.fk_materia.id }}">
                    <input id="id_fk_materia_display" class="form-control d-none" value="{{ user.fk_professor.fk_materia.nome_materia }}" readonly>
                {% endif %}

                {% if user.tipo_usuario != "professor" %}
                <div class="mb-3">
                    <label for="id_fk_turma" class="form-label">Turma</label>
                    <select id="id_fk_turma" name="fk_turma" class="form-control"></select>
                </div>
                {% endif %}

                {% if user.is_superuser or user.tipo_usuario == "coordenador" %}
                <div class="mb-3">
                    <label for="id_fk_professor" class="form-label">Professor</label>
                    <select id="id_fk_professor" name="fk_professor" class="form-control"></select>
                </div>

                <div class="mb-3">
                    <label for="id_fk_materia_display" class="form-label">Matéria</label>
                    <input id="id_fk_materia_display" class="form-control" readonly>
                    <input type="hidden" id="id_fk_materia_id" name="fk_materia">
                </div>
                {% endif %}

                <div class="mb-3">
                    <label for="id_fk_livro" class="form-label">Livro</label>
                    <select id="id_fk_livro" name="fk_livro" class="form-control"></select>
                </div>

                <div class="mb-3">
                    <label for="id_conteudo" class="form-label">Conteúdo Ministrado</label>
                    <textarea id="id_conteudo" name="conteudo" class="form-control"></textarea>
                </div>

                <div class="mb-3">
                    <label for="id_dever" class="form-label">Dever</label>
                    <textarea id="id_dever" name="dever" class="form-control"></textarea>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="id_data_entrega" class="form-label">Data de Entrega</label>
                        <input type="date" id="id_data_entrega" name="data_entrega" class="form-control">
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="id_data_conteudo" class="form-label">Data do Conteúdo</label>
                        <input type="date" id="id_data_conteudo" name="start_time" class="form-control">
                    </div>
                </div>

                <div class="d-flex justify-content-end">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save me-1"></i>Salvar
                    </button>
                </div>
            </form>
        </div>
    </div>
</div>

<style>
.bg-gradient-primary {
    background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
}
form label {
    font-weight: 600;
}
</style>

<script>
document.addEventListener("DOMContentLoaded", function () {
    const escolaSelect = document.getElementById("id_fk_escola");
    const professorSelect = document.getElementById("id_fk_professor");

    if (escolaSelect) {
        // dispara carregamento inicial se valor já está definido (professor/coordenador)
        if (escolaSelect.value) {
            escolaSelect.dispatchEvent(new Event("change"));
        }

        escolaSelect.addEventListener("change", function () {
            var escolaId = this.value;

            // Carrega turmas da escola
            fetch(`/ajax/get-turmas/${escolaId}/`)
                .then(response => response.json())
                .then(data => {
                    var turmaSelect = document.getElementById("id_fk_turma");
                    if (turmaSelect) {
                        turmaSelect.innerHTML = '<option value="">Selecione uma Turma</option>';
                        data.forEach(turma => {
                            var option = document.createElement("option");
                            option.value = turma.id;
                            option.textContent = turma.nome;
                            turmaSelect.appendChild(option);
                        });
                    }
                });

            // Carrega professores da escola
            fetch(`/ajax/get-professores/${escolaId}/`)
                .then(response => response.json())
                .then(data => {
                    if (professorSelect) {
                        professorSelect.innerHTML = '<option value="">Selecione um Professor</option>';
                        data.forEach(professor => {
                            var option = document.createElement("option");
                            option.value = professor.id;
                            option.textContent = professor.nome;
                            professorSelect.appendChild(option);
                        });
                    }

                    // Limpa os campos de matéria e livro
                    let materiaDisplay = document.getElementById("id_fk_materia_display");
                    let materiaHidden = document.getElementById("id_fk_materia_id");
                    if (materiaDisplay) materiaDisplay.value = '';
                    if (materiaHidden) materiaHidden.value = '';
                    document.getElementById("id_fk_livro").innerHTML = '<option value="">Selecione um Livro</option>';
                });
        });
    }

    if (professorSelect) {
        professorSelect.addEventListener("change", function () {
            var professorId = this.value;

            if (professorId) {
                fetch(`/ajax/get-materia/${professorId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.error) {
                            let materiaDisplay = document.getElementById("id_fk_materia_display");
                            let materiaHidden = document.getElementById("id_fk_materia_id");

                            if (materiaDisplay) materiaDisplay.value = data.nome;
                            if (materiaHidden) materiaHidden.value = data.id;

                            var escolaId = escolaSelect ? escolaSelect.value : null;
                            if (escolaId) {
                                fetch(`/ajax/get-livros/${data.id}/${escolaId}/`)
                                    .then(response => response.json())
                                    .then(livros => {
                                        var livroSelect = document.getElementById("id_fk_livro");
                                        livroSelect.innerHTML = '<option value="">Selecione um Livro</option>';
                                        livros.forEach(livro => {
                                            var option = document.createElement("option");
                                            option.value = livro.id;
                                            option.textContent = livro.nome;
                                            livroSelect.appendChild(option);
                                        });
                                    });
                            }
                        }
                    });
            }
        });

        // dispara carregamento inicial se professor já está definido
        if (professorSelect.value) {
            professorSelect.dispatchEvent(new Event("change"));
        }
    }
});
</script>
{% endblock %}
