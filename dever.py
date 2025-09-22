<nav class="navbar navbar-expand-md navbar-dark bg-dark fixed-top">
    <div class="container-fluid">
        <!-- Logo/Brand -->
        <a class="navbar-brand" href="{% url 'cal:home' %}">Home</a>
        
        <!-- Botão Toggler para Offcanvas -->
        <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <!-- Menu Principal (visível em telas maiores) -->
        <div class="collapse navbar-collapse">
            <div class="navbar-nav">
                {% if user.is_authenticated %}
                    <!-- Superusuário - pode ver tudo -->
                    {% if user.is_superuser %}
                        <a class="nav-link" href="{% url 'cal:calendar' %}">Calendário</a>
                        <a class="nav-link" href="{% url 'cal:semana_alunos' %}">Semana</a>
                        <a class="nav-link" href="{% url 'cal:dever_create' %}">Novo</a>
                        <a class="nav-link" href="{% url 'cal:listar_eventos' %}">Lista</a>
                        <a class="nav-link" href="{% url 'cal:lista_escolas' %}">Escolas</a>
                        <a class="nav-link" href="{% url 'cal:lista_turma' %}">Turmas</a>
                        <a class="nav-link" href="{% url 'cal:lista_materia' %}">Matérias</a>
                        <a class="nav-link" href="{% url 'cal:lista_livro' %}">Livros</a>
                        <a class="nav-link" href="{% url 'cal:lista_professor' %}">Professores</a>
                        <a class="nav-link" href="{% url 'cal:lista_alunos' %}">Alunos</a>
                        <a class="nav-link" href="{% url 'cal:listar_horarios' %}">Horários</a>
                        <a class="nav-link" href="{% url 'login:lista_usuarios' %}">Usuários</a>
                    
                    <!-- Coordenador - pode ver tudo -->
                    {% elif user.groups.all.0.name == 'coordenador' %}
                        <a class="nav-link" href="{% url 'cal:calendar' %}">Calendário</a>
                        <a class="nav-link" href="{% url 'cal:semana_alunos' %}">Semana</a>
                        <a class="nav-link" href="{% url 'cal:dever_create' %}">Novo</a>
                        <a class="nav-link" href="{% url 'cal:listar_eventos' %}">Lista</a>
                        <a class="nav-link" href="{% url 'cal:lista_escolas' %}">Escolas</a>
                        <a class="nav-link" href="{% url 'cal:lista_turma' %}">Turmas</a>
                        <a class="nav-link" href="{% url 'cal:lista_materia' %}">Matérias</a>
                        <a class="nav-link" href="{% url 'cal:lista_livro' %}">Livros</a>
                        <a class="nav-link" href="{% url 'cal:lista_professor' %}">Professores</a>
                        <a class="nav-link" href="{% url 'cal:lista_alunos' %}">Alunos</a>
                        <a class="nav-link" href="{% url 'cal:listar_horarios' %}">Horários</a>
                        <a class="nav-link" href="{% url 'login:lista_usuarios' %}">Usuários</a>
                    
                    <!-- Professor - pode ver Novo, Lista, Turmas -->
                    {% elif user.groups.all.0.name == 'professor' %}
                        <a class="nav-link" href="{% url 'cal:dever_create' %}">Novo</a>
                        <a class="nav-link" href="{% url 'cal:listar_eventos' %}">Lista</a>
                        <a class="nav-link" href="{% url 'cal:lista_turma' %}">Turmas</a>
                    
                    <!-- Pai - pode ver Semana e Lista -->
                    {% elif user.groups.all.0.name == 'pai' %}
                        <a class="nav-link" href="{% url 'cal:semana_alunos' %}">Semana</a>
                        <a class="nav-link" href="{% url 'cal:listar_eventos' %}">Lista</a>
                    
                    <!-- Caso o usuário não se encaixe em nenhum grupo específico -->
                    {% else %}
                        <a class="nav-link" href="{% url 'cal:calendar' %}">Calendário</a>
                        <a class="nav-link" href="{% url 'cal:semana_alunos' %}">Semana</a>
                        <a class="nav-link" href="{% url 'cal:listar_eventos' %}">Lista</a>
                    {% endif %}
                {% endif %}
            </div>
            
            <!-- Menu do usuário (lado direito) -->
            <ul class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                        <i class="fas fa-user me-1"></i>{{ user.username }}
                    </a>
                    <ul class="dropdown-menu dropdown-menu-end">
                        <li><a class="dropdown-item" href="{% url 'login:perfil' %}">
                            <i class="fas fa-user me-2"></i>Meu Perfil
                        </a></li>
                        <li><a class="dropdown-item" href="{% url 'login:editar_perfil' %}">
                            <i class="fas fa-edit me-2"></i>Editar Perfil
                        </a></li>
                        <li><a class="dropdown-item" href="{% url 'login:alterar_senha' %}">
                            <i class="fas fa-key me-2"></i>Alterar Senha
                        </a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li>
                            <form method="post" action="{% url 'login:logout' %}" class="d-inline">
                                {% csrf_token %}
                                <button type="submit" class="dropdown-item">
                                    <i class="fas fa-sign-out-alt me-2"></i>Sair
                                </button>
                            </form>
                        </li>
                    </ul>
                </li>
                {% else %}
                <li class="nav-item">
                    <a href="{% url 'login:login' %}" class="btn btn-outline-success">Login</a>
                </li>
                {% endif %}
            </ul>
        </div>
        
        <!-- Offcanvas Menu (para mobile) -->
        <div class="offcanvas offcanvas-end bg-dark text-white" tabindex="-1" id="offcanvasNavbar">
            <div class="offcanvas-header">
                <h5 class="offcanvas-title">Menu</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>
            <div class="offcanvas-body">
                <!-- O conteúdo do offcanvas será preenchido automaticamente pelo Bootstrap -->
                <!-- Não é necessário duplicar o conteúdo aqui -->
            </div>
        </div>
    </div>
</nav>