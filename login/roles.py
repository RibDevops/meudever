from rolepermissions.roles import AbstractUserRole

class Coordenador(AbstractUserRole):
    available_permissions = {
        'dever_list': True,
        'dever_detail': True,
        'dever_create': True,
        'dever_update': True,
        'dever_delete': True,
        'registro_view': True,
    }

class Professor(AbstractUserRole):
    available_permissions = {
        'dever_list': True,
        'dever_detail': True,
        'dever_create': True,
        'dever_update': True,
        'dever_delete': True,
        
    }

class Pai(AbstractUserRole):
    available_permissions = {
        'dever_list': True,
        'dever_detail': True,

    }

# from rolepermissions.roles import AbstractUserRole

# class Coordenador(AbstractUserRole):
#     available_permissions = {
#         'access_all_data': True,
#         'manage_teachers_and_parents': True,
#     }

# class Professor(AbstractUserRole):
#     available_permissions = {
#         'look_all_situations': True,
#         'manage_class_assignments': True,
#     }

# class Pai(AbstractUserRole):
#     available_permissions = {
#         'view_child_performance': True,
#     }

# class Aluno(AbstractUserRole):
#     available_permissions = {
#         'look_situation': True,
#     }
