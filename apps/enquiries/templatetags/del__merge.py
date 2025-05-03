from django import template
from apps.estimations.models import EstimationMainProduct, MainProductAluminium, MainProductGlass


register = template.Library()


@register.simple_tag
def merge(pk, version):
    # main_products = EstimationMainProduct.objects.filter(category=pk, building__estimation=version)
    main_products = EstimationMainProduct.objects.filter(category=pk, building__estimation=version)
    
    
    for product in main_products:
        try:
            main_product = EstimationMainProduct.objects.get(pk=product)
        except:
            main_product = None
        try:
            aluminium_obj = MainProductAluminium.objects.get(estimation_product=product)
        except:
            aluminium_obj = None
        try:
            glass_obj = MainProductGlass.objects.get(estimation_product=product, glass_primary=True)
            second_glass_obj = MainProductGlass.objects.select_related('estimation_product').filter(estimation_product=product, glass_primary=False)
        except:
            glass_obj = None
            second_glass_obj = None
        
    
        data = main_product.union(aluminium_obj)
        print("DATA==>", data)