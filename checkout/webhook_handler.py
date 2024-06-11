from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile

import stripe
import json
import time

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""

        cust_email = order.email # Get the customers email from the order and store it in a variable
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        
        # Now to finally send the email all we've got to do is use the send mail function.
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        ) 

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """

        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # Get the Charge object
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )

        billing_details = stripe_charge.billing_details # updated
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2) # updated

        # Clean data in the shipping details clean up the data by ensuring that fields without values are explicitly set to None instead of an empty string.
        # It loops through each key-value pair in the shipping_details.address dictionary.
        # For each pair, it checks if the value is an empty string ("")
        # If an empty string is found, it replaces the empty string with None.
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        profile = None # Set to None Just so we know we can still allow anonymous users to checkout.
        username = intent.metadata.username
        if username != 'AnonymousUser': # if the username isn't anonymous user. We know they were authenticated.
            profile = UserProfile.objects.get(user__username=username)
            if save_info: # Save the user details only if checkbox was checked
                profile.default_phone_number__ = shipping_details.phone
                profile.default_country__ = shipping_details.address.country
                profile.default_postcode__ = shipping_details.address.postal_code
                profile.default_town_or_city__ = shipping_details.address.city
                profile.default_street_address1__ = shipping_details.address.line1
                profile.default_street_address2__ = shipping_details.address.line2
                profile.default_county__ = shipping_details.address.state
                profile.save()

        order_exists = False # Let's start by assuming the order by user doesn't exist in our database. We can do that with a simple variable set to false.
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    # iexact lookup field to make it an exact match
                    # For example, if shipping_details.name is “John Doe”, this query iexact will match records with full_name as “john doe”, “JOHN DOE”, “John Doe”, etc.
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                """If the order is found we'll set order exists to true,
                    and return a 200 HTTP response to stripe, with the message that we verified the order already exists."""
                order_exists = True
                break # Break out of the loop if order is found
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order) # Calling the send confirmation email method. The payment has definitely been completed at this point. So we'll want to send an email no matter what. send it just before returning that response to stripe
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                # And otherwise will create the order.
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile, # In this way, the webhook handler can create orders for both authenticated users by attaching their profile. And for anonymous users by setting that field to none.
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                if order:
                    # And if anything goes wrong just delete the order if it was created. And return a 500 server error response to stripe.
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        self._send_confirmation_email(order) # If the order was created by the webhook handler I'll send the email at the bottom here
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)