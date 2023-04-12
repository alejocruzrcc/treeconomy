from rolepermissions.roles import AbstractUserRole

class Admin(AbstractUserRole):
    available_permissions = {
        'is_admin': True,
        'manage_a_project': True,
        'generate_report': True,
        'view_userlist': True,
        'view_companylist': True
    }

class Inversor(AbstractUserRole):
    available_permissions = {
        'is_admin': False,
        'view_project': True,
        'view_userlist': False
    }
    
class Company(AbstractUserRole):
    available_permissions = {
        'is_admin': False,
        'view_project': True,
        'view_userlist': False,
        'generate_qr': True        
    }