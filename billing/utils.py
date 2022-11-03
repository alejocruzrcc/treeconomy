from datetime import datetime
from projects.models import Order
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa  
#difine render_to_pdf() function
from projects.models import Order
from django.shortcuts import get_object_or_404


def render_to_pdf(template_src,cid, context_dict={}):
    template = get_template(template_src)
    order = get_object_or_404(Order, id =cid)
    context = {'order':order}
    context_dict=context
    html  = template.render(context_dict)
    result = BytesIO()

    #This part will create the pdf.
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def get_or_set_order_session(request):
    order_id= request.session.get('order_id', None)
    
    if order_id is None:
        order = Order()
        order.ordered_date = datetime.now()
        order.save()
        request.session['order_id']= order.id
    else:
        try:
            order = Order.objects.get(id=order_id, ordered=False)
        except Order.DoesNotExist:
            order = Order()
            order.save()
            request.session['order_id']= order.id
            
    if request.user.is_authenticated and order.user is None:
        
        order.user = request.user
        order.save()
    return order
            
def get_or_zero_order_session(request):
    order_id= request.session.get('order_id', None)
    
    if order_id is None:
        return False
    else:
        try:
            order = Order.objects.get(id=order_id, ordered=False)
        except Order.DoesNotExist:
            order = Order()
            order.save()
            request.session['order_id']= order.id
            
    if request.user.is_authenticated and order.user is None:
        
        order.user = request.user
        order.save()
    return order