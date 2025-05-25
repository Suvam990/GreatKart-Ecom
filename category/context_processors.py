from .models import Category

def menu_links(requesst):
    links = Category.objects.all()

    return dict(links = links)

