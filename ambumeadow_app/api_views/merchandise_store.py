from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from django.utils import timezone

from ambumeadow_app.models import Product


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_product(request):
    product_name = request.data.get("product_name")
    description = request.data.get("description", "")
    category = request.data.get("category")
    price = request.data.get("price")
    quantity = request.data.get("quantity")
    requires_prescription = request.data.get("requires_prescription", False)
    image = request.FILES.get('image')

    # basic validation
    if not product_name or not category or price is None or quantity is None:
        return JsonResponse(
            {"message": "product_name, category, price and quantity are required"},
            status=400
        )

    # validate category
    valid_categories = dict(Product.CATEGORY_CHOICES).keys()
    if category not in valid_categories:
        return JsonResponse(
            {"message": "Invalid product category"},
            status=400
        )

    try:
        product = Product.objects.create(
            product_name=product_name,
            description=description,
            category=category,
            price=price,
            quantity=quantity,
            image=image,
            requires_prescription=requires_prescription,
        )

        return JsonResponse({
            "message": "Medicine added successfully",
            "product": {
                "id": product.id,
                "product_name": product.product_name,
                "description": product.description,
                "category": product.category,
                "price": str(product.price),
                "quantity": product.quantity,
                "image_url": product.image.url if product.image else None,
                "requires_prescription": product.requires_prescription,
                "date_added": product.date_added.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }, status=200)

    except Exception as e:
        return JsonResponse(
            {"message": "Failed to add medicine", "error": str(e)},
            status=500
        )
# end of add product api

# api to get all products
@api_view(['GET'])
def get_all_products(request):
    try:
        products = Product.objects.filter(is_active=True).order_by('-date_added')

        product_list = []

        # map category key → label
        category_map = dict(Product.CATEGORY_CHOICES)

        for product in products:
            product_list.append({
                "id": product.id,
                "product_name": product.product_name,
                "description": product.description,
                "category": product.category,
                "price": str(product.price),
                "quantity": product.quantity,
                "image_url": product.image.url if product.image else None,
                "requires_prescription": product.requires_prescription,
                "is_active": product.is_active,
                "date_added": product.date_added.strftime("%Y-%m-%d %H:%M:%S"),
            })

        return JsonResponse({
            "count": len(product_list),
            "products": product_list
        }, status=200)

    except Exception as e:
        return JsonResponse(
            {"message": "Failed to fetch medicines", "error": str(e)},
            status=500
        )

# end of get all products api

# api to update the product quantity and price
@api_view(['PUT'])
def update_product_stock(request):
    product_id = request.data.get("product_id")
    price = request.data.get("price")
    quantity = request.data.get("quantity")

    # must provide at least one field
    if price is None and quantity is None:
        return JsonResponse(
            {"message": "Provide price or quantity to update"},
            status=400
        )

    try:
        product = Product.objects.filter(id=product_id, is_active=True).first()

        if not product:
            return JsonResponse(
                {"message": "Product not found"},
                status=404
            )

        # update fields if provided
        if price is not None:
            try:
                product.price = float(price)
            except ValueError:
                return JsonResponse(
                    {"message": "Invalid price value"},
                    status=400
                )

        if quantity is not None:
            try:
                product.quantity = int(quantity)
            except ValueError:
                return JsonResponse(
                    {"message": "Invalid quantity value"},
                    status=400
                )

        product.save()

        return JsonResponse({
            "message": "Product updated successfully",
            "product": {
                "id": product.id,
                "product_name": product.product_name,
                "price": str(product.price),
                "quantity": product.quantity,
                "date_updated": product.date_added.strftime("%Y-%m-%d %H:%M:%S"),
            }
        }, status=200)

    except Exception as e:
        return JsonResponse(
            {"message": "Failed to update product", "error": str(e)},
            status=500
        )

# end of update product stock api