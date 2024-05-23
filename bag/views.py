from django.shortcuts import render, redirect

# Create your views here.
def view_bag(request):
    """A view that renders the bag content page"""
    
    return render(request, 'bag/bag.html')

def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    quantity = int(request.POST.get('quantity')) # get the quantity from the form. and convert it to an integer since it'll come from the template as a string.
    redirect_url = request.POST.get('redirect_url') # redirect_url found in our form

    """ if product size is in request.post we'll set it equal to that. """
    size = None
    if 'product_size' in request.POST: #  if product size is in request.post we'll set it equal to that size selected
        size = request.POST['product_size']
    bag = request.session.get('bag', {}) # first check to see if there's a bag variable in the session. And if not we'll create one.

    if size:
        """If the item is already in the bag.
        Then we need to check if another item of the same id and same size already exists.
        And if so increment the quantity for that size and otherwise just set it equal to the quantity"""
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}} # To handle maybe same item with different sizes when we add it to the bag
    else:

        if item_id in list(bag.keys()):
            bag[item_id] += quantity # Or update the quantity if it already exists.
        else:
            bag[item_id] = quantity # Add the item to the bag

    request.session['bag'] = bag # And then overwrite the variable in the session with the updated version.
    return redirect(redirect_url)
        
