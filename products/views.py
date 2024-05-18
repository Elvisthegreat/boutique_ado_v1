from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q # To generate a search query
from .models import Product, Category

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:

        """For sorting products"""
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        """Handling a specific category in our main_nav.html"""
        if 'category' in request.GET:
            categories = request.GET['category'].split(',') # if that category exist split it into a list at the commas.
            products = products.filter(category__name__in=categories) # And then use that list to filter the current query set of all products down to only products whose category name is in the list.
            categories = Category.objects.filter(name__in=categories) # display for the user which categories they currently have selected.

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

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_team': query, # for search query
        'current_categories': categories, # for category
        'current_sorting': current_sorting
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """
    
    product = get_object_or_404(Product, pk=product_id) # Returning one product so we use get_object_or_404

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)