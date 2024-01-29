from typing import Any, Dict

from users.models import UserAccount
from .models import Product
from .forms import ProductForm, ProductBrandForm, ProductGroupForm




def get_products_count(user: UserAccount) -> int:
    """Returns the number of products added by a user."""
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")
    return Product.objects.filter(store__owner=user).count()


def _fetch_existing_product_copy(product_data: Dict[str, Any]) -> Product | None:
    """
    Internal function that fetches an existing product that is very similar in attributes to the new product being added.
    (excluding the product's id, quantity, added_at and updated_at attributes)

    :param product_data: A dictionary containing the new product's data.
    """
    excluded_fields = ("id", "quantity", "added_at", "updated_at")
    fieldnames = [ field.name for field in Product._meta.get_fields() if field.name not in excluded_fields ]
    # Ensure's that only fields that exist in the product model are included in the query
    product_data = { fieldname: product_data.get(fieldname) for fieldname in fieldnames if fieldname in product_data }

    form = ProductForm(data=product_data)
    form.full_clean()
    product_data = form.cleaned_data
    # Ensure's that excluded fields are not included in the query
    for fieldname in excluded_fields:
        product_data.pop(fieldname, None)
    
    # Remove empty/null values
    product_data = dict(filter(lambda item: bool(item[1]), product_data.items()))
    return Product.objects.filter(**product_data).first()


def _update_product_data_with_new_brand_and_group(product_data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Internal function used to update product data with the new brand and group
    specified by the user.

    The new brand and group are created if they don't already exist for the product's store.

    :param product_data: A dictionary containing the new product's data.
    :return: A tuple containing the updated product data and a dictionary of errors.
    """
    errors = {}
    new_brand_name = product_data.pop("new-brand", None)
    new_group_name = product_data.pop("new-group", None)
    if new_brand_name:
        brand_form = ProductBrandForm(data={"name": new_brand_name, "store": product_data.get("store")})
        if brand_form.is_valid():
            new_brand = brand_form.save(commit=True)
            product_data["brand"] = new_brand.pk
        else:
            errors["new-brand"] = list(brand_form.errors.values())[0]

    if new_group_name:
        group_form = ProductGroupForm(data={"name": new_group_name, "store": product_data.get("store")})
        if group_form.is_valid():
            new_group = group_form.save(commit=True)
            product_data["group"] = new_group.pk
        else:
            errors["new-group"] = list(group_form.errors.values())[0]
    return product_data, errors
