from users.models import UserAccount
from .models import Product



def get_products_count(user: UserAccount) -> int:
    """Returns the number of products added by a user."""
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")
    return Product.objects.filter(store__owner=user).count()
