from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ambumeadow_app.models import Product, User, ProductOrder, Notification, Payment
from ambumeadow_app.utils.verify_paystack import verify_paystack_payment
import json

from . auth import verify_firebase_token


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@verify_firebase_token
def add_product(request):
    product_name = request.data.get("product_name")
    description = request.data.get("description", "")
    category = request.data.get("category")
    price = request.data.get("price")
    quantity = request.data.get("quantity")
    expiry_date = request.data.get("expiry_date")
    requires_prescription = request.data.get("requires_prescription", False)
    image = request.FILES.get('image')

    # basic validation
    if not product_name or not category or price is None or quantity is None:
        print("product_name, category, price and quantity are required")
        return JsonResponse(
            {"message": "product_name, category, price and quantity are required"},
            status=400
        )


    try:
        product = Product.objects.create(
            product_name=product_name,
            description=description,
            category=category,
            price=price,
            quantity=quantity,
            expiry_date=expiry_date,
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
@verify_firebase_token
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
@verify_firebase_token
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
                product.quantity += int(quantity)
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


# create  order api
@csrf_exempt
@api_view(['POST'])
@verify_firebase_token
def create_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            latitude = data.get("latitude", 0.0)
            longitude = data.get("longitude", 0.0)
            reference = request.data.get("payment_reference")
            amount = request.data.get("amount")
            products = data.get("products", [])  # List of items

            if not user_id or not products:
                return JsonResponse({"message": "User ID and product list are required"}, status=400)

            user = User.objects.filter(id=user_id).first()
            if not user:
                return JsonResponse({"message": "User not found"}, status=404)
            
            # ================= VERIFY PAYMENT =================
            paystack_response = verify_paystack_payment(reference)

            if not paystack_response.get("status"):
                return Response({"error": "Payment verification failed"}, status=400)

            data = paystack_response.get("data")

            if data["status"] != "success":
                return Response({"error": "Payment not successful"}, status=400)

            paid_amount = data["amount"] / 100  # convert from kobo/cents

            if float(paid_amount) != float(amount):
                return Response({"error": "Amount mismatch"}, status=400)

            order_ids = []
            for item in products:
                product_id = item.get("product_id")
                quantity = item.get("quantity")
                price = item.get("price")

                # Check required fields
                if not all([product_id, quantity, price]):
                    return JsonResponse({"message": "Missing product details in one of the items"}, status=400)

                product = Product.objects.filter(id=product_id).first()
                if not product:
                    return JsonResponse({"message": f"Product with ID {product_id} not found"}, status=404)

                if quantity > product.quantity:
                    return JsonResponse({"message": f"Not enough stock for {product.product_name}"}, status=400)
                
                # ================= SAVE PAYMENT =================
                payment = Payment.objects.create(
                    user=user,
                    hospital=product.hospital,
                    service_type="merchandise",
                    amount=amount,
                    method="paystack",
                    transaction_reference=reference,
                    receipt_number=data.get("reference"),
                    status="paid",
                    paid_at=timezone.now(),
                )

                # Create order
                order = ProductOrder.objects.create(
                    product_id=product,
                    user_id=user,
                    quantity=quantity,
                    price=price,
                    delivered=False,
                    latitude=latitude,
                    longitude=longitude
                )
                product.quantity -= quantity
                product.save()
                order_ids.append(order.id)


                # Notification for each item
                Notification.objects.create(
                    user=user,
                    message=f"Order for {product.product_name} placed successfully. We’ll deliver soon.",
                    is_read=False
                )

            return JsonResponse({"message": "All orders created successfully", "order_ids": order_ids}, status=200)

        except Exception as e:
            print("Error:", str(e))
            # logger.info(f"Error creating orders: {str(e)}")
            return JsonResponse({"message": "An error occurred", "error": str(e)}, status=500)

# endof create order api