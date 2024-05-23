from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_id, item_data in bag.items():
        #  execute this code if the item has no sizes.
        if isinstance(item_data, int): # This line checks if item_data is an integer. If it is, it means that the item does not have sizes associated with it. Represent the quantity instead
            product = get_object_or_404(Product, pk=item_id)
            total += item_data * product.price # This line calculates the total price by adding the product’s price multiplied by its quantity to the total
            product_count += item_data
            # After appending an item, bag_items contains a dictionary with item details
            bag_items.append({
                'item_id': item_id, # # The ID of the item
                'quantity': item_data, # The quantity of the item
                'product': product, # The product object retrieved from the database
            })
        else:
            product = get_object_or_404(Product, pk=item_id)
            for size, quantity, in item_data['items_by_size'].items():
                total += quantity * product.price
                product_count += quantity
                bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
                'size': size,
            })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    grand_total = delivery + total
    
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context