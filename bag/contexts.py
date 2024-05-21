from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        total += quantity * product.price
        product_count += quantity
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product
        })

    if total < settings.FREE_DELIVERY_THRESHOLD: # free delivery. if they spend more than the amount specified in the free delivery threshold in settings.py.
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total #  let the user know how much more they need to spend to get free delivery
    else: # If the total is greater than or equal to the threshold set delivery and the free_delivery_delta to 0.
        delivery = 0
        free_delivery_delta = 0

    grand_total = delivery + total

    context = {
        """add all these items to the context.
        So they'll be available in templates across the site."""
        
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context