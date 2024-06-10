from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order
# Create your views here.

def profile(request):
    """ Display the user's profile """
    profile = get_object_or_404(UserProfile, user=request.user) # Storing the user models in a variable name profile

    if request.method == 'POST': # If the request method is Post from the user
        form = UserProfileForm(request.POST, instance=profile) # Create a new instance of the user profile form using the post data.
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

    form = UserProfileForm(instance=profile)
    orders = profile.orders.all()
    
    template = 'profiles/profile.html'

    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True 
    }

    return render(request, template, context)

def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html' #  use the checkout success template since that template already has the layout for rendering a nice order confirmation.
    context = {
        'order': order,
        'from_profile': True, # So we can check in that template if the user got there via the order history view. Check button of checkout_success page
    }

    return render(request, template, context)
