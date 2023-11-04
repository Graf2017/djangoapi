import os


def image_upload_path(instance, filename):  # directories will have name from id of position
    position_id = str(instance.position.id)
    upload_path = os.path.join("photos", position_id, filename)
    return upload_path


def categories_image_upload_path(instance, filename):  # directories will have name from id of categories
    category_id = str(instance.id)
    upload_path = os.path.join("photos/categories", category_id, filename)
    return upload_path


def delivery_is_valid(delivery):
    required_fields = ['first_name', 'last_name', 'phone', 'city', 'address']
    return all(delivery.get(field) for field in required_fields)