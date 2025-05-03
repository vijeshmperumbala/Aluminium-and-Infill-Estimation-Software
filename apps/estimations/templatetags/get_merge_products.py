from django import template
from apps.Categories.models import Category
from apps.estimations.models import EstimationMainProduct, MainProductAluminium, Temp_EstimationMainProduct, Temp_MainProductAluminium

register = template.Library()


@register.simple_tag
def get_merge_products(request, category, products):
    """
    This function retrieves product data and category information based on a given category and list of
    product IDs.
    
    """
    category = Category.objects.get(pk=category)
    product_data = []
    product_ids = []
    alumin = []
    PATHS = [
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_print_2/'
    ]
    if any(path in request for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
        MainProductAluminiumModel = MainProductAluminium
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        MainProductAluminiumModel = Temp_MainProductAluminium
    
    summary_product = MainProductAluminiumModel.objects.filter(estimation_product__in=products).order_by('area')
    alumin.append(summary_product)
    for pro in summary_product:
        main_pro = EstimationMainProductModel.objects.filter(pk=pro.estimation_product.id)
        product_data.append(main_pro)
        
    data = {
        "category": category,
        "product_data": product_data,
        "products": products
    }
    return data