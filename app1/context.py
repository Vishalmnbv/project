from .models import *
def cat(request):
    subtotal = 0
    deliverycharge = 0
    total = 0
    cartcount = 0
    if request.user.is_authenticated:
        cartdata = cart.objects.filter(userid=request.user)
        cartcount = cart.objects.filter(userid=request.user).count()
        for i in cartdata:
            subtotal+=i.subtotal()
            if subtotal<300 and subtotal>0:
                deliverycharge = 30
            else:
                deliverycharge = 0
        total = subtotal + deliverycharge
    return {'subtotal':subtotal,'deliverycharge':deliverycharge,'total':total,'cartcount':cartcount}
