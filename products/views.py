from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q # To generate a search query
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    # making sure the variables are defined for it to  work properly
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:

        """For sorting products and the direction"""
        if 'sort' in request.GET: # checking if 'sort' is there
            sortkey = request.GET['sort']
            sort = sortkey # setting sort defined to None to sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
                # sort category by name instead of category id
            if sortkey == 'category':
                sortkey = 'category__name'

            if 'direction' in request.GET: # checking if 'direction' is there
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}' # check whether it's descending. And if so we'll add a minus in front of the sort key using string formatting, which will reverse the order.
            products = products.order_by(sortkey) # Finally in order to actually sort the products all we need to do is use the order by model method.

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

    """for sorting asc & desc"""
    current_sorting = f'{sort}_{direction}' # return the current sorting methodology to the template.

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


def add_product(request):
    """Add Product to the store"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) # instance of the product form from request.post and include request .files also In order to make sure to capture in the image of the product if one was submitted.
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm

    templates = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, templates, context)

def edit_product(request, product_id):
    """Edit a product in a store"""
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    templates = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, templates, context)
