from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q # To generate a search query
from .models import Product

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    category = None

    if request.GET:

        """Handling a specific category in our main_nav.html"""
        if 'category' in request.GET:
            categories = request.GET['category'].split(',') # if that category exist split it into a list at the commas.
            products = products.filter(category__name__in=categories) # And then use that list to filter the current query set of all products down to only products whose category name is in the list.

        """Handling the search query"""
        if 'q' in request.GET: # remember the 'q' is the name in our input form in base.html
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            """we want to return results where the query was matched in either
               the product name or the description.
               In order to accomplish this or logic, we need to use Q. Remember this for it important!"""
               
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    context = {
        'products': products,
        'search_team': query,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """
    
    product = get_object_or_404(Product, pk=product_id) # Returning one product so we use get_object_or_404

    context = {
        'product': product,
        'product_detail': product_detail,
    }

    return render(request, 'products/product_detail.html', context)