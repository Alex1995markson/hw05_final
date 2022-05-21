from django.core.paginator import Paginator
from django.conf import settings


def paginator_create(request, objs):
    paginator = Paginator(objs, settings.COUNT_ITEMS_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return [page_obj, page_number]
