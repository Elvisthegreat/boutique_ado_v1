"""
__init__.py : Sets the default app configuration.
apps.py: Defines the app configuration and imports signals when the app is ready.
signals.py: Contains signal handlers that update the order total whenever an OrderLineItem is saved or deleted.
"""

default_app_config = 'checkout.apps.CheckoutConfig'