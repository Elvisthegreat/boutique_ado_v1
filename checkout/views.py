from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm

# Create your views here.

def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        mesages.error(request, 'There is nothing in your bag at the moment')
        return redirect(reverse('products'))

    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51PLq3HHmLk04H1kswWAlnzLrkgHTnhp0pnMt7I64U6TbgrM2O0NUQg9ZN9ahRXtuN7Tx03alhjpIdaoFnYYwkxa4000M7ijR7j',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)
