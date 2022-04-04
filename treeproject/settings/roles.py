from rolepermissions.roles import AbstractUserRole

class Admin(AbstractUserRole):
    available_permissions = {
        'manage_a_project': True,
    }

class Inversor(AbstractUserRole):
    available_permissions = {
        'view_project': True,
    }
    
