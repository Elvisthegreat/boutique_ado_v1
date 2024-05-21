from django.shortcuts import render, redirect

# Create your views here.
def view_bag(request):
    """A view that renders the bag content page"""
    
    return render(request, 'bag/bag.html')

def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    quantity = int(request.POST.get('quantity')) # get the quantity from the form. and convert it to an integer since it'll come from the template as a string.
    redirect_url = request.POST.get('redirect_url') # redirect_url found in our form
    bag = request.session.get('bag', {}) # first check to see if there's a bag variable in the session. And if not we'll create one.

    if item_id in list(bag.keys()):
        bag[item_id] += quantity # Or update the quantity if it already exists.
    else:
        bag[item_id] = quantity # Add the item to the bag

    request.session['bag'] = bag # And then overwrite the variable in the session with the updated version.
    return redirect(redirect_url)
        
