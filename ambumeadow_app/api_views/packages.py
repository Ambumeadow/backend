from .common_imports import *


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_packages(request):
    packages = Package.objects.all().order_by('-date_added')

    package_data = []

    for package in packages:
        package_data.append({
            "id": package.id,
            "name": package.name,
            "category": package.category,
            "maximum_members": package.maximum_members,
            "no_of_consultations": package.no_of_consultations,
            "access_telemedicine": package.access_telemedicine,
            "book_ambulance": package.book_ambulance,
            "book_care_appointment": package.book_care_appointment,
            "price": float(package.price),
            "date_added": package.date_added,
        })

    return JsonResponse({
        "total_packages": packages.count(),
        "packages": package_data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_package(request):
    try:
        package = Package.objects.create(
            name=request.data.get("name"),
            category=request.data.get("category"),
            maximum_members=request.data.get("maximum_members"),
            no_of_consultations=request.data.get("no_of_consultations"),
            access_telemedicine=request.data.get("access_telemedicine"),
            book_ambulance=request.data.get("book_ambulance"),
            book_care_appointment=request.data.get("book_care_appointment"),
            price=request.data.get("price"),
        )

        return JsonResponse({
            "success": True,
            "message": "Package created successfully",
            "package_id": package.id
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_package(request, package_id):
    try:
        package = Package.objects.get(id=package_id)

        package.name = request.data.get(
            "name",
            package.name
        )

        package.category = request.data.get(
            "category",
            package.category
        )

        package.maximum_members = request.data.get(
            "maximum_members",
            package.maximum_members
        )

        package.no_of_consultations = request.data.get(
            "no_of_consultations",
            package.no_of_consultations
        )

        package.access_telemedicine = request.data.get(
            "access_telemedicine",
            package.access_telemedicine
        )

        package.book_ambulance = request.data.get(
            "book_ambulance",
            package.book_ambulance
        )

        package.book_care_appointment = request.data.get(
            "book_care_appointment",
            package.book_care_appointment
        )

        package.price = request.data.get(
            "price",
            package.price
        )

        package.save()

        return JsonResponse({
            "success": True,
            "message": "Package updated successfully"
        })

    except Package.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Package not found"
        }, status=404) 



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_package(request, package_id):
    try:
        package = Package.objects.get(id=package_id)

        package.delete()

        return JsonResponse({
            "success": True,
            "message": "Package deleted successfully"
        })

    except Package.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Package not found"
        }, status=404)
