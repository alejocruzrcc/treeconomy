from rolepermissions.roles import AbstractUserRole

class Admin(AbstractUserRole):
    available_permissions = {
        'is_admin': True,
        'manage_a_project': True,
        'generate_report': True,
        'view_userlist': True
    }

class Inversor(AbstractUserRole):
    available_permissions = {
        'is_admin': False,
        'view_project': True,
        'view_userlist': False
    }
    
