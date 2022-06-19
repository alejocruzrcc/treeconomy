from django import template
register = template.Library()

@register.filter(name='verbose_name')
def verbose_name(the_object, the_field):
    if the_object._meta.get_field(the_field).verbose_name == "":
        return "blankety blank"
    else:
        return the_object._meta.get_field(the_field).verbose_name