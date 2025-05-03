from django import forms

from apps.Categories.models import Category
from apps.accessories_kit.models import AccessoriesKit
from apps.addon_master.models import Addons
from apps.brands.models import CategoryBrands

from apps.enquiries.models import (
    EnquirySpecifications, 
    Enquiries, 
    Temp_EnquirySpecifications,
)
from apps.estimations.models import (   
    Deduction_Items, 
    EstimationBuildings, 
    EstimationMainProduct, 
    EstimationProduct_Associated_Data, 
    EstimationProductComplaints, 
    EstimationProjectSpecifications, 
    MainProductAluminium, 
    MainProductGlass, 
    MainProductAddonCost, 
    MainProductSilicon,
    PricingOption, 
    ProductComments, 
    Quotation_Notes, 
    Quotation_Notes_Comments, 
    Quotation_Provisions, 
    Quotations, 
    ProductCategoryRemarks, 
    Quote_Send_Detail, 
    Temp_Deduction_Items, 
    Temp_EstimationMainProduct, 
    Temp_EstimationProductComplaints, 
    Temp_MainProductAddonCost, 
    Temp_MainProductAluminium, 
    Temp_MainProductGlass, 
    Temp_MainProductSecondtaryGlass, 
    Temp_MainProductSilicon, 
    Temp_PricingOption, 
    Temp_ProductComments, 
    Temp_Quotation_Notes, 
    Temp_Quotation_Notes_Comments, 
    Temp_Quotation_Provisions, 
    Temp_Quotations,
)
from apps.UoM.models import UoM
from apps.panels_and_others.models import (
    PanelMasterSpecifications, 
    PanelMasterBrands, 
    PanelMasterSeries, 
    PanelMasterBase,
)
from apps.pricing_master.models import Sealant_kit, Surface_finish_kit
from apps.product_master.models import Product
from apps.product_parts.models import Profile_Kit
from apps.profiles.models import ProfileMasterType

from apps.provisions.models import Provisions
from apps.signatures.models import Signatures
from apps.suppliers.models import BillofQuantity, Suppliers
from apps.surface_finish.models import Surface_finish
# from apps.tags.models import Tags


class CreateEnquirySpecificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kit_id = kwargs.pop('kit_id')
        super(CreateEnquirySpecificationForm, self).__init__(*args, **kwargs)
        self.fields['surface_finish'].queryset = Surface_finish_kit.objects.filter(master=kit_id).order_by('surface_finish__surface_finish')
        self.fields['surface_finish'].widget.attrs.update({
                'class': 'form-select form-select-solid',
                'data-placeholder': 'Select an option'
            })
        self.fields['surface_finish'].empty_label = 'Select a Surface Finish'
        
    SPEC_TYPE = [
        (1, "predefined"),
        (2, "Custom"),
    ]
    categories = forms.ModelChoiceField(queryset=Category.objects.select_related().order_by('category'), empty_label="Select a Category")
    categories.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
        'style': 'padding-left: 10px;'
    })

    aluminium_products = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1).order_by('product_name'), required=False, empty_label="select a Product")
    aluminium_products.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    aluminium_system = forms.ModelChoiceField(queryset=CategoryBrands.objects.all().order_by('brands'), required=False,
                                              empty_label="Select a Brand")
    aluminium_system.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    
    aluminium_specification = forms.ModelChoiceField(queryset=ProfileMasterType.objects.all().distinct('profile_master_type'), required=False,
                                              empty_label="Select a Type")
    aluminium_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    aluminium_series = forms.ModelChoiceField(queryset=Profile_Kit.objects.all().order_by('profile_series__profile_master_series'), required=False,
                                            empty_label="select a series")
    aluminium_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_category = forms.ModelChoiceField(queryset=PanelMasterBase.objects.all().order_by('panel_category__category'), required=False,
                                         empty_label="select a category")
    panel_category.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all().order_by('panel_brands__brands'), required=False,
                                         empty_label="select a brand")
    panel_brand.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    panel_product = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1).order_by('product_name'), required=False,
                                         empty_label="select a Panel Product")
    panel_product.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select a Panel Product'
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all().order_by('series'), required=False,
                                          empty_label="select a series")
    panel_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_specification = forms.ModelChoiceField(queryset=PanelMasterSpecifications.objects.all().order_by('specifications'), required=False,
                                                 empty_label="select a specifictaion")
    panel_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option',
        
    })
    
    specification_type = forms.ChoiceField(choices=SPEC_TYPE, initial=1, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input',
        'data-placeholder': 'Select an option'
    }))

    class Meta:
        model = EnquirySpecifications
        exclude = ['created_date', 'created_by']
        widgets = {
            'identifier': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Product Identifier',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'required': True
                }
            ),
            'is_description': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'specification_description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Description',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'cols': '4',
                    'rows': '3',
                }
            ),
            
                
        }


class TempCreateEnquirySpecificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kit_id = kwargs.pop('kit_id')
        super(TempCreateEnquirySpecificationForm, self).__init__(*args, **kwargs)
        self.fields['surface_finish'].queryset = Surface_finish_kit.objects.filter(master=kit_id).order_by('surface_finish__surface_finish')
        self.fields['surface_finish'].widget.attrs.update({
                'class': 'form-select form-select-solid',
                'data-placeholder': 'Select an option'
            })
        self.fields['surface_finish'].empty_label = 'Select a Surface Finish'
        
    SPEC_TYPE = [
        (1, "predefined"),
        (2, "Custom"),
    ]
    
    categories = forms.ModelChoiceField(queryset=Category.objects.select_related().order_by('category'), empty_label="Select a Category")
    categories.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
        'style': 'padding-left: 10px;'
        
    })
    
    specification_type = forms.ChoiceField(choices=SPEC_TYPE, initial=1, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input',
        'data-placeholder': 'Select an option'
    }))

    aluminium_products = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1).order_by('product_name'), required=False, empty_label="select a Product")
    aluminium_products.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    aluminium_system = forms.ModelChoiceField(queryset=CategoryBrands.objects.all().order_by('brands'), required=False,
                                              empty_label="Select a Brand")
    aluminium_system.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    aluminium_specification = forms.ModelChoiceField(queryset=ProfileMasterType.objects.all().distinct('profile_master_type'), required=False,
                                              empty_label="Select a Type")
    aluminium_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    aluminium_series = forms.ModelChoiceField(queryset=Profile_Kit.objects.all().order_by('profile_series__profile_master_series'), required=False,
                                            empty_label="select a series")
    aluminium_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_category = forms.ModelChoiceField(queryset=PanelMasterBase.objects.all().order_by('panel_category__category'), required=False,
                                         empty_label="select a category")
    panel_category.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all().order_by('panel_brands__brands'), required=False,
                                         empty_label="select a brand")
    panel_brand.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all().order_by('series'), required=False,
                                          empty_label="select a series")
    panel_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    panel_product = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1).order_by('product_name'), required=False,
                                         empty_label="select a Panel Product")
    panel_product.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select a Panel Product'
    })

    panel_specification = forms.ModelChoiceField(queryset=PanelMasterSpecifications.objects.all().order_by('specifications'), required=False,
                                                 empty_label="select a specifictaion")
    panel_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    
    class Meta:
        model = Temp_EnquirySpecifications
        exclude = ['created_date', 'created_by']
        widgets = {
            'identifier': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Product Identifier',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'required': True
                }, 
            ),
            'is_description': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'specification_description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Description',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'cols': '4',
                    'rows': '3',
                }
            ),
            'specification_custom': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            # 'internal_sealant': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input me-3 h-20px w-20px',
            #     }
            # ),
            # 'external_sealant': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input me-3 h-20px w-20px',
            #     }
            # ),
        }


class EditEnquirySpecificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kit_id = kwargs.pop('kit_id')
        super(EditEnquirySpecificationForm, self).__init__(*args, **kwargs)
        self.fields['surface_finish'].queryset = Surface_finish_kit.objects.filter(master=kit_id)
        self.fields['surface_finish'].widget.attrs.update({
                'class': 'form-select form-select-solid',
                'data-placeholder': 'Select an option'
            })
        self.fields['surface_finish'].empty_label = 'Select a Surface Finish'
        
    SPEC_TYPE = [
        (1, "predefined"),
        (2, "Custom"),
    ]
    categories = forms.ModelChoiceField(queryset=Category.objects.select_related(), empty_label="Select a Category")
    categories.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
        'style': 'padding-left: 10px;'
        
    })

    specification_type = forms.ChoiceField(choices=SPEC_TYPE, initial=1, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input',
        'data-placeholder': 'Select an option'
    }))
    
    aluminium_products = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1), required=False, empty_label="select a Product")
    aluminium_products.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    aluminium_system = forms.ModelChoiceField(queryset=CategoryBrands.objects.all(), required=False,
                                              empty_label="Select a Brand")
    aluminium_system.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    aluminium_specification = forms.ModelChoiceField(queryset=ProfileMasterType.objects.all().distinct('profile_master_type'), required=False,
                                              empty_label="Select a Type")
    aluminium_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    aluminium_series = forms.ModelChoiceField(queryset=Profile_Kit.objects.all(), required=False,
                                            empty_label="select a series")
    aluminium_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_category = forms.ModelChoiceField(queryset=PanelMasterBase.objects.all(), required=False,
                                         empty_label="select a category")
    panel_category.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    panel_product = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1), required=False,
                                         empty_label="select a Panel Product")
    panel_product.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select a Panel Product'
    })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all(), required=False,
                                         empty_label="select a brand")
    panel_brand.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all(), required=False,
                                          empty_label="select a series")
    panel_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_specification = forms.ModelChoiceField(queryset=PanelMasterSpecifications.objects.all(), required=False,
                                                 empty_label="select a specifictaion")
    panel_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    
    surface_finish = forms.ModelChoiceField(queryset=Surface_finish.objects.all(), required=False, empty_label='Select an Option')
    surface_finish.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option',
        'required': True,
    })

    class Meta:
        model = EnquirySpecifications
        exclude = ['created_date', 'created_by', 'last_modified_by', 'last_modified_date', 'estimation']
        widgets = {
            'identifier': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    # 'style': 'border-radius:0px; padding-top: 20px;',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'required': True
                }
            ),
            'internal_sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'external_sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_description': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'specification_description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Description',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'cols': '4',
                    'rows': '3',
                }
            ),
        }
        
        
class TempEditEnquirySpecificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kit_id = kwargs.pop('kit_id')
        super(TempEditEnquirySpecificationForm, self).__init__(*args, **kwargs)
        self.fields['surface_finish'].queryset = Surface_finish_kit.objects.filter(master=kit_id)
        self.fields['surface_finish'].widget.attrs.update({
                'class': 'form-select form-select-solid',
                'data-placeholder': 'Select an option'
            })
        self.fields['surface_finish'].empty_label = 'Select a Surface Finish'
    ALUMINIUM_SPECIFICATION = [
        (1, 'Thermal Break'),
        (2, 'Non Thermal Break'),
    ]
    SPEC_TYPE = [
        (1, "predefined"),
        (2, "Custom"),
    ]
    categories = forms.ModelChoiceField(queryset=Category.objects.select_related(), empty_label="Select a Category")
    categories.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
        'style': 'padding-left: 10px;'
        
    })

    # aluminium_category = forms.ModelChoiceField(queryset=ConfigurationMasterBase.objects.all(), required=False, empty_label="select a Category")
    # aluminium_category.widget.attrs.update({
    #     'class': 'form-select form-select-solid',
    #     'data-placeholder': 'Select an option'
    # })
    specification_type = forms.ChoiceField(choices=SPEC_TYPE, initial=1, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input',
        'data-placeholder': 'Select an option'
    }))

    aluminium_products = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1), required=False, empty_label="select a Product")
    aluminium_products.widget.attrs.update({
        'class': 'form-select form-select-solid',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })

    aluminium_system = forms.ModelChoiceField(queryset=CategoryBrands.objects.all(), required=False,
                                              empty_label="Select a Brand")
    aluminium_system.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    aluminium_specification = forms.ModelChoiceField(queryset=ProfileMasterType.objects.all().distinct('profile_master_type'), required=False,
                                              empty_label="Select a Type")
    aluminium_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    aluminium_series = forms.ModelChoiceField(queryset=Profile_Kit.objects.all(), required=False,
                                            empty_label="select a series")
    aluminium_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_category = forms.ModelChoiceField(queryset=PanelMasterBase.objects.all(), required=False,
                                         empty_label="select a category")
    panel_category.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    panel_product = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1), required=False,
                                         empty_label="select a Panel Product")
    panel_product.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select a Panel Product'
    })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all(), required=False,
                                         empty_label="select a brand")
    panel_brand.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all(), required=False,
                                          empty_label="select a series")
    panel_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })

    panel_specification = forms.ModelChoiceField(queryset=PanelMasterSpecifications.objects.all(), required=False,
                                                 empty_label="select a specifictaion")
    panel_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    
    surface_finish = forms.ModelChoiceField(queryset=Surface_finish.objects.all(), required=False, empty_label='Select an Option')
    surface_finish.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option',
        'required': True,
    })

    class Meta:
        model = Temp_EnquirySpecifications
        exclude = ['created_date', 'created_by', 'last_modified_by', 'last_modified_date', 'estimation']
        widgets = {
            'identifier': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    # 'style': 'border-radius:0px; padding-top: 20px;',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'required': True
                }
            ),
            'internal_sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'external_sealant': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_description': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'specification_description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Description',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'cols': '4',
                    'rows': '3',
                }
            ),
        }


class CreateEstimationProductForm(forms.ModelForm):
    def __init__(self, enquiry_id, *args, **kwargs):
        super(CreateEstimationProductForm, self).__init__(*args, **kwargs)
        myChoices = [(c.categories.id, c.categories.category) for c in EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id).order_by('categories')]
        myChoices = [('', 'Select a Category')] + myChoices
        try:
            # myChoices2 = [(c.panel_specification.id, c.panel_specification) for c in EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            myChoices2 = [(c.panel_product.id, c.panel_product) for c in EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            myChoices2.insert(0, ('', 'Select a Product'))
            self.fields['panel_product'].choices = set(myChoices2)
            self.fields['panel_product'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        except Exception as e:
            self.fields['panel_product'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        

        self.fields['category'].choices = set(myChoices)
        self.fields['category'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an option'
            })
        self.fields['category'].empty_label = 'Select a Category'

        
        self.fields['boq_number'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                           queryset=BillofQuantity.objects.filter(enquiry=enquiry_id).distinct('boq_number'), 
                                                           empty_label="Select BoQ Number",
                                                           required=False)
        self.fields['specification_Identifier'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                                         queryset=EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id).order_by('id'), 
                                                                         empty_label="Select a Identifier", required=True)

    TOLERANCE = [
        ('', 'Select a tolerance unit'),
        (1, 'Percentage'),
        (2, 'Fixed Value'),
    ]

    category = forms.ModelChoiceField(
            queryset=Category.objects.all().order_by('id'),
            empty_label="Select a Category"
        )
    category.widget.attrs.update({
                            'class': 'form-control floating-control',
                            'data-placeholder': 'Select an option'
                        })

    product = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1), required=False, empty_label="Select a Product")
    product.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                    })

    panel_product = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1), required=False, empty_label="Select a Product")
    panel_product.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                        
                    })

    brand = forms.ModelChoiceField(queryset=CategoryBrands.objects.all(), required=False, empty_label="Select a Brand")
    brand.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                        
                    })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all(), required=False,
                                   empty_label="Select a Brand")
    panel_brand.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                        
                    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all(), required=False, empty_label="Select a Series")
    panel_series.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                        
                    })

    # series = forms.ModelChoiceField(queryset=ConfigurationMasterSeries.objects.all(), required=False,
    #                                 empty_label="Select a Series")
    series = forms.ModelChoiceField(queryset=Profile_Kit.objects.all(), required=False,
                                    empty_label="Select a Series")
    series.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
        
    })

    uom = forms.ModelChoiceField(queryset=UoM.objects.all(), empty_label="Select a Unit")
    uom.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })
    accessories = forms.ModelChoiceField(queryset=AccessoriesKit.objects.all(), required=False, empty_label="Select a Accessory")
    accessories.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })
    tolerance_type = forms.ChoiceField(choices=TOLERANCE, required=False, widget=forms.Select(attrs={
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                    }))
    
    supplier = forms.ModelChoiceField(queryset=Suppliers.objects.all(), required=False, empty_label="Select a Supplier")
    supplier.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })
    
    class Meta:
        model = EstimationMainProduct
        fields = [
                    'category',
                    'product',
                    'brand',
                    'panel_brand',
                    'series',
                    'panel_series',
                    'uom',
                    'accessories',
                    'is_accessory',
                    'tolerance_type',
                    'tolerance',
                    'panel_product',
                    'accessory_quantity',
                    'is_tolerance',
                    'is_sourced',
                    'supplier',
                    'boq_number',
                    'specification_Identifier',
                    'enable_addons',
                    
                    'is_display_data',
                    'display_product_name',
                    'display_width',
                    'display_height',  
                    'display_area',
                    'display_quantity',
                    'display_total_area',
                    'hide_dimension',
                    
                    
                 ]
        widgets = {
            'is_display_data': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                }
            ),
            'display_product_name': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'display_width': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'display_height': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'display_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'readonly': True,
                }
            ),
            'display_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'display_total_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'readonly': True,
                }
            ),
            
            
            'tolerance': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'accessory_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'is_tolerance': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_sourced': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'enable_addons': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_accessory': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'hide_dimension': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
        }


class CreateEstimationProductAluminiumForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kit_id = kwargs.pop('kit_id')
        super(CreateEstimationProductAluminiumForm, self).__init__(*args, **kwargs)
        self.fields['surface_finish'].queryset = Surface_finish_kit.objects.filter(master=kit_id)
        self.fields['surface_finish'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an option'
            })
        self.fields['surface_finish'].empty_label = 'Select a Surface Finish'

    UNIT = [
        (1, 'Pricing for SqM'),
        (2, 'Pricing for Unit'),
        (3, 'Pricing for KG'),
        
    ]
    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
        (4, 'Formula Based'),
    ]

    pricing_unit = forms.ChoiceField(choices=UNIT, required=False, widget=forms.Select(attrs={
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
    }))
    aluminium_pricing = forms.ChoiceField(choices=PRICING_TYPE, initial=3, required=False, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input',
        'data-placeholder': 'Select an option',
        'style': "border: 1px solid #009ef7;",
    }))

    # surface_finish = forms.ModelChoiceField(queryset=Surface_finish.objects.all(), required=False, empty_label='Select a Surface Finish')
    # surface_finish.widget.attrs.update({
    #     'class': 'form-control floating-control',
    #     'data-placeholder': 'Select an option'
    # })
    
    class Meta:
        model = MainProductAluminium
        fields = [
                    'aluminium_pricing',
                    'pricing_unit',
                    'custom_price',
                    'width',
                    'height',
                    'area',
                    'quantity',
                    'total_quantity',
                    'total_area',
                    'total_weight',
                    'product_type',
                    'product_description',
                    'price_per_kg',
                    'weight_per_unit',
                    'al_markup',
                    'al_quoted_price',
                    'enable_divisions',
                    'horizontal',
                    'vertical',
                    'total_linear_meter',
                    'weight_per_lm',
                    'surface_finish',
                    'curtainwall_type',
                    'in_area_input',
                    
                 ]
        widgets = {
            'al_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'al_quoted_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'price_per_kg': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'weight_per_unit': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'custom_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                    # 'placeholder': 'Price',
                }
            ),
            'width': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px; ',
                    'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$'
                    
                }
            ),
            'height': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                    'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+\s*$',
                }
            ),
            'area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'total_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                    'readonly': True,
                }
            ),
            'total_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'total_weight': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'product_type': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 10px;',
                    'required': True
                }
            ),
            'product_description': forms.Textarea(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'cols': '5',
                    'rows': '4',
                    'placeholder': 'Product Description',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'horizontal': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'vertical': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'enable_divisions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'curtainwall_type': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'in_area_input': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'total_linear_meter': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
            'weight_per_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                }
            ),
        }


class CreateEstimationProductGlassForm(forms.ModelForm):
    def __init__(self, enquiry_id, *args, **kwargs):
        super(CreateEstimationProductGlassForm, self).__init__(*args, **kwargs)
        try:
            myChoices = [(c.panel_specification.id, c.panel_specification.specifications) for c in
                        EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            self.fields['glass_specif'].choices = set(myChoices)
            self.fields['glass_specif'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        except Exception as e:
            self.fields['glass_specif'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })

    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
    ]

    glass_pricing_type = forms.ChoiceField(choices=PRICING_TYPE, initial=3, required=False,
                                          widget=forms.RadioSelect(attrs={
                                              'class': 'form-check-input glcosting',
                                              'data-placeholder': 'Select an option'
                                          }))
    

    class Meta:
        model = MainProductGlass
        fields = [
                    'glass_specif',
                    'is_glass_cost',
                    'total_area_glass',
                    'glass_base_rate',
                    'glass_markup_percentage',
                    'glass_quoted_price',
                    'glass_width',
                    'glass_height',
                    'glass_area',
                    'glass_quantity',
                    'glass_pricing_type',
        ]
        widgets = {
            'is_glass_cost': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            # 'glass_primary': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input',
            #     }
            # ),
            'total_area_glass': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                    'required': False,
                }
            ),
            'glass_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                }
            ),
            'glass_markup_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                }
            ),
            'glass_quoted_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                    'required': False,
                }
            ),
            # 'glass_price_per_sqm': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
            #     }
            # ),
            'glass_width': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_height': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            # 'total_area_glass': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
        }
        

class CreateEstimationProductTemp_SecondaryGlassForm(forms.ModelForm):
    def __init__(self, enquiry_id, *args, **kwargs):
        super(CreateEstimationProductTemp_SecondaryGlassForm, self).__init__(*args, **kwargs)
        try:
            myChoices = [(c.panel_specification.id, c.panel_specification.specifications) for c in
                        EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            self.fields['sec_glass_specif'].choices = set(myChoices)
            self.fields['sec_glass_specif'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        except Exception as e:
            self.fields['sec_glass_specif'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        

    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
    ]

    sec_glass_pricing_type = forms.ChoiceField(choices=PRICING_TYPE, initial=3, required=False,
                                          widget=forms.RadioSelect(attrs={
                                              'class': 'form-check-input glcosting',
                                              'data-placeholder': 'Select an option'
                                          }))

    class Meta:
        model = Temp_MainProductSecondtaryGlass
        fields = [
                    'sec_glass_specif',
                    'sec_is_glass_cost',
                    # 'sec_total_area_glass',
                    'sec_base_rate',
                    'sec_markup_percentage',
                    'sec_quoted_price',
                    
                    'sec_price_per_sqm',
                    # 'sec_glass_primary',
                    'sec_width',
                    'sec_height',
                    'sec_area',
                    'sec_quantity',
                    'sec_total_area',
                    'sec_glass_pricing_type',
        ]
        widgets = {
            'sec_is_glass_cost': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            # 'sec_glass_primary': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input',
            #         'style': 'display: none',
            #         'checked': 'checked',
            #     }
            # ),
            
            'sec_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                }
            ),
            'sec_markup_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                }
            ),
            'sec_quoted_price': forms.TextInput(
                attrs={
                    'class': 'form-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                }
            ),
            'sec_price_per_sqm': forms.TextInput(
                attrs={
                    'class': 'form-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                }
            ),
            'sec_width': forms.TextInput(
                attrs={
                    'class': 'form-control  measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'sec_height': forms.TextInput(
                attrs={
                    'class': 'form-control  measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'sec_area': forms.TextInput(
                attrs={
                    'class': 'form-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'sec_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'sec_total_area': forms.TextInput(
                attrs={
                    'class': 'form-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
        }
        
class TempCreateEstimationProductTemp_SecondaryGlassForm(forms.ModelForm):
    def __init__(self, enquiry_id, *args, **kwargs):
        super(TempCreateEstimationProductTemp_SecondaryGlassForm, self).__init__(*args, **kwargs)
        try:
            myChoices = [(c.panel_specification.id, c.panel_specification.specifications) for c in
                        Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            self.fields['glass_specif'].choices = set(myChoices)
            self.fields['glass_specif'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        except Exception as e:
            self.fields['glass_specif'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })

    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
    ]

    glass_pricing_type = forms.ChoiceField(choices=PRICING_TYPE, initial=3, required=False,
                                          widget=forms.RadioSelect(attrs={
                                              'class': 'form-check-input glcosting',
                                              'data-placeholder': 'Select an option'
                                          }))
    

    class Meta:
        model = Temp_MainProductGlass
        fields = [
                    'glass_specif',
                    'is_glass_cost',
                    'total_area_glass',
                    'glass_base_rate',
                    'glass_markup_percentage',
                    'glass_quoted_price',
                    'glass_width',
                    'glass_height',
                    'glass_area',
                    'glass_quantity',
                    'glass_pricing_type',
        ]
        widgets = {
            'is_glass_cost': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            # 'glass_primary': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input',
            #     }
            # ),
            'total_area_glass': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                    'required': False,
                }
            ),
            'glass_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                }
            ),
            'glass_markup_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                }
            ),
            'glass_quoted_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
                    'required': False,
                }
            ),
            # 'glass_price_per_sqm': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
            #     }
            # ),
            'glass_width': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_height': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            # 'total_area_glass': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
        }
        

class CreateMainProductSilicon(forms.ModelForm):
    # def __init__(self, sealant_pricing_id, *args, **kwargs):
    #     super(CreateMainProductSilicon, self).__init__(*args, **kwargs)
        # if sealant_pricing_id:
        # self.fields['external_sealant_type'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
        # self.fields['external_sealant_type'].widget.attrs.update({
        #             'class': 'form-control floating-control',
        #             'data-placeholder': 'Select an option'
        #         })
        # self.fields['external_sealant_type'].empty_label = 'Select an option'

        # self.fields['internal_sealant_type'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
        # self.fields['internal_sealant_type'].widget.attrs.update({
        #             'class': 'form-control floating-control',
        #             'data-placeholder': 'Select an option'
        #         })
        # self.fields['internal_sealant_type'].empty_label = 'Select an option'

        # self.fields['polyamide_gasket'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
        # self.fields['polyamide_gasket'].widget.attrs.update({
        #             'class': 'form-control floating-control',
        #             'data-placeholder': 'Select an option'
        #         })
        # self.fields['polyamide_gasket'].empty_label = 'Select an option'

        # self.fields['transom_gasket'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
        # self.fields['transom_gasket'].widget.attrs.update({
        #             'class': 'form-control floating-control',
        #             'data-placeholder': 'Select an option'
        #         })
        # self.fields['transom_gasket'].empty_label = 'Select an option'

        # self.fields['mullion_gasket'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
        # self.fields['mullion_gasket'].widget.attrs.update({
        #             'class': 'form-control floating-control',
        #             'data-placeholder': 'Select an option'
        #         })
        # self.fields['mullion_gasket'].empty_label = 'Select an option'

        # self.fields['epdm_gasket'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
        # self.fields['epdm_gasket'].widget.attrs.update({
        #             'class': 'form-control floating-control',
        #             'data-placeholder': 'Select an option'
        #         })
        # self.fields['epdm_gasket'].empty_label = 'Select an option'
        
    
    
    
    class Meta:
        model = MainProductSilicon
        fields = [
            'is_silicon',
            
            # 'is_external',
            'external_lm',
            # 'is_internal',
            'internal_lm',
            'silicon_quoted_price',
            'external_markup',
            'internal_markup',
            'internal_base_rate',
            'external_base_rate',
            'external_sealant_type',
            'internal_sealant_type',
            'polyamide_gasket',
            'polyamide_markup',
            'transom_gasket',
            'transom_markup',
            'mullion_gasket',
            'mullion_markup',
            # 'epdm_gasket',
            # 'epdm_markup',
            'polyamide_lm',
            'transom_lm',
            'mullion_lm',
            # 'epdm_lm',
            'polyamide_base_rate',
            'transom_base_rate',
            'mullion_base_rate',
            # 'epdm_base_rate',
        ]
        widgets = {
            # 'external_sealant_type': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px;',
                    
            #     }
            # ),
            # 'epdm_base_rate': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
            'mullion_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'polyamide_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'transom_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'polyamide_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            # 'epdm_lm': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
            'mullion_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'transom_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'polyamide_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'epdm_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'mullion_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'transom_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'polyamide_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            
            'is_silicon': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            # 'is_external': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-30px',
            #         'style': 'border: 1px solid #009ef7;',
            #     }
            # ),
            # 'is_internal': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-30px',
            #         'style': 'border: 1px solid #009ef7;',
            #     }
            # ),
            'external_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'internal_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'external_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'internal_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'external_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'internal_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'silicon_quoted_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'type': 'hidden'
                }
            ),
            'external_sealant_type': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            'internal_sealant_type': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            'polyamide_gasket': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            'transom_gasket': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            'mullion_gasket': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            # 'epdm_gasket': forms.TextInput(
            #     attrs={
            #         'type': 'hidden'
            #     }
            # ),
        }
        

class CreateMainProductAddons(forms.ModelForm):
    PRICING_TYPE = [
        ('', "Select Price Type"),
        (1, 'Price per Linear Meter'),
        (2, 'Price per Square Meter'),
        (3, 'Price per Unit')
    ]
    pricing_type = forms.ChoiceField(choices=PRICING_TYPE, required=False, widget=forms.Select(attrs={
                        'class': 'form-select mb-2 form-control floating-control addon_type',
                        'data-placeholder': 'Select an option'
                    }))
    
    addons = forms.ModelChoiceField(queryset=Addons.objects.all().exclude(linear_meter=0.000, sqm=0.000, unit=0.000), required=False, empty_label="Select a Addon")
    addons.widget.attrs.update({
        'class': 'form-control floating-control selection_addon',
        'data-placeholder': 'Select an option'
    })

    class Meta:
        model = MainProductAddonCost
        fields = [
                'addons',
                'base_rate',
                'pricing_type', 
                'addon_quantity',
            ]

        widgets = {
            'base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control addon_rate fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'addon_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control addon_quantity fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
        }


class CreatePricingRuleForm(forms.ModelForm):

    class Meta:
        model = PricingOption
        exclude = ['estimation_product', 'created_date']
        widgets = {
            'is_pricing_control': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'adjust_by_sqm': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'overhead_perce': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'labour_perce': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
        }


class CreateQuotationsForm(forms.ModelForm):
    signature = forms.ModelChoiceField(queryset=Signatures.objects.all(), initial=1)
    signature.widget.attrs.update({
        'class': 'form-select mb-2',
        
    })
    DISCOUNT_TYPE = [
        (0, 'None'),
        (1, 'Percentage'),
        (2, 'Fixed Value'),
    ]
    
    discount_type = forms.ChoiceField(choices=DISCOUNT_TYPE, required=False, widget=forms.Select(attrs={
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    }))
    

    class Meta:
        model = Quotations
        exclude = [     
                        'created_by', 
                        'created_date', 
                        'prepared_for', 
                        'represented_by', 
                        'estimations_version', 
                        'estimations', 
                        'products_specifications',
                        
                ]
        # fields = '__all__'
        widgets = {
            'quotation_id': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-flush fw-bolder text-dark fs-5 w-125px px-1',
                    'placeholder': 'Q-ID'
                }
            ),
            'quotation_date': forms.DateInput(
                attrs={
                    'class': 'form-control text-dark fs-5 q_date px-1 py-0',
                    'placeholder': 'Select date',
                    'type': 'date'
                }
            ),
            'valid_till': forms.DateInput(
                attrs={
                    'class': 'form-control  text-dark fs-5 q_valid px-1 py-0',
                    'placeholder': 'Select date',
                    'type': 'date'
                }
            ),
            'remarks': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '10'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '3'
                }
            ),
            'other_notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '3'
                }
            ),
            'terms_of_payment': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '10'
                }
            ),
            'exclusions': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '6'
                }
            ),
            'terms_and_conditions': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '30'
                }
            ),
            'signature': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                }
            ),
            'quote_price': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'hidden',
                }
            ),
            
            'custom_specifictaion': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'apply_total': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'apply_line_items': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'display_discount_perc': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_provisions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'building_total_enable': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'discount': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Discount',
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '6',
                    'rows': '3',
                    'placeholder': 'Quotation Discount Notes... (Optional)',
                }
            ),
            
            'is_dimensions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
            'is_quantity': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
            'is_rpu': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
            'is_rpsqm': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
            'is_area': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
        }
        
class CreateQuotations_Provisions(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateQuotations_Provisions, self).__init__(*args, **kwargs)
        self.fields['provision'].queryset = Provisions.objects.all()
        self.fields['provision'].label_from_instance = lambda obj: "%s | %s" % (obj.provisions, obj.provisions_price)
        
    provision = forms.ModelChoiceField(queryset=Provisions.objects.all(), empty_label="Select a Provision")
    provision.widget.attrs.update({
        'class': 'form-select mb-2 provision_select',
    })
    
    class Meta:
        modal = Quotation_Provisions
        fields = ['provision', 'provision_cost']
        widgets = {
            'provision_cost': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid fw-bolder text-muted fs-3 provisioncost',
                }
            ),
        }

class TempCreateQuotations_Provisions(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TempCreateQuotations_Provisions, self).__init__(*args, **kwargs)
        self.fields['provision'].queryset = Provisions.objects.all()
        self.fields['provision'].label_from_instance = lambda obj: "%s | %s" % (obj.provisions, obj.provisions_price)
        
    provision = forms.ModelChoiceField(queryset=Provisions.objects.all(), empty_label="Select a Provision")
    provision.widget.attrs.update({
        'class': 'form-select mb-2 provision_select',
    })
    
    class Meta:
        modal = Temp_Quotation_Provisions
        fields = ['provision', 'provision_cost']
        widgets = {
            'provision_cost': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid fw-bolder text-muted fs-3 ',
                }
            ),
        }
        
        
# class CreateShortQuotationsForm(forms.ModelForm):
#     signature = forms.ModelChoiceField(queryset=Signatures.objects.all(), initial=1)
#     signature.widget.attrs.update({
#         'class': 'form-select mb-2',
#     })
    
#     DISCOUNT_TYPE = [
#         (0, 'None'),
#         (1, 'Percentage'),
#         (2, 'Fixed Value'),
#     ]
    
#     discount_type = forms.ChoiceField(choices=DISCOUNT_TYPE, required=False, widget=forms.Select(attrs={
#         'class': 'form-select mb-2',
#         # 'data-control': 'select2',
#         # 'data-hide-search': 'true',
#         'data-placeholder': 'Select an option'
#     }))

#     class Meta:
#         model = Quotations
#         exclude = [
#                         'created_by', 'created_date', 'prepared_for', 
#                         'represented_by', 'estimations_version', 'estimations', 
#                         'terms_of_payment', 'products_specifications', 'exclusions', 
#                   ]
#         widgets = {
#             'quotation_id': forms.TextInput(
#                 attrs={
#                     'class': 'form-control form-control-flush fw-bolder text-muted fs-3 w-125px',
#                 }
#             ),
#             'quotation_date': forms.DateInput(
#                 attrs={
#                     'class': 'form-control form-control-transparent fw-bolder pe-5',
#                     'placeholder': 'Select date',
#                     'type': 'date'
#                 }
#             ),
#             'valid_till': forms.DateInput(
#                 attrs={
#                     'class': 'form-control form-control-transparent fw-bolder pe-5',
#                     'placeholder': 'Select date',
#                     'type': 'date'

#                 }
#             ),
#             'description': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '40',
#                     'rows': '3'
#                 }
#             ),
#             'other_notes': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '40',
#                     'rows': '3'
#                 }
#             ),
#             'remarks': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '40',
#                     'rows': '10'
#                 }
#             ),
#             'terms_and_conditions': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '40',
#                     'rows': '15'
#                 }
#             ),
#             'signature': forms.TextInput(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                 }
#             ),
#             'quote_price': forms.TextInput(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'type': 'hidden',
#                 }
#             ),
#             'custom_specifictaion': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input me-3 h-20px w-30px',
#                 }
#             ),
#             'apply_total': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input',
#                 }
#             ),
#             'apply_line_items': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input',
#                 }
#             ),
#             'discount': forms.TextInput(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'placeholder': 'Discount',
#                 }
#             ),
#             'is_provisions': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input',
#                 }
#             ),
#             'building_total_enable': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input',
#                 }
#             ),
#             'notes': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '6',
#                     'rows': '3',
#                     'placeholder': 'Quotation Discount Notes... (Optional)',
#                 }
#             ),
#         }


class UpdateLabourAndOverhead(forms.ModelForm):
    class Meta:
        model = PricingOption
        fields = ['overhead_perce', 'labour_perce']
        widgets = {
            'overhead_perce': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                }
            ),
            'labour_perce': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                    
                }
            ),
        }


class UpdateAluminiumPercentage(forms.ModelForm):
    class Meta:
        model = MainProductAluminium
        fields = ['al_markup']
        widgets = {
            'al_markup': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                    
                }
            ),
        }


class UpdateGlassPercentage(forms.ModelForm):
    class Meta:
        model = MainProductGlass
        fields = ['glass_markup_percentage']
        widgets = {
            'glass_markup_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                }
            ),
        }
        
class UpdateTolerance(forms.ModelForm):
    class Meta:
        model = EstimationMainProduct
        fields = ['tolerance']
        widgets = {
            'tolerance': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                }
            ),
        }


class CreateNoteForm(forms.ModelForm):
    class Meta:
        model = ProductCategoryRemarks
        fields = ['remark']
        widgets = {
            'remark': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': "Note's",
                    'cols': '10',
                    'rows': '3'
                }
            )
        }


class TempCreateEstimationProductForm(forms.ModelForm):
    # def __init__(self, enquiry_id, *args, **kwargs):
    #     super(TempCreateEstimationProductForm, self).__init__(*args, **kwargs)
    #     myChoices = [(c.categories.id, c.categories.category) for c in Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
    #     myChoices = [('', 'Select a Category')] + myChoices
        
    #     try:
    #         myChoices2 = [(c.panel_product.id, c.panel_product) for c in Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
    #         myChoices2.insert(0, ('', 'Select a Product'))
    #         print("myChoices2===>", myChoices2)
    #         # myChoices2 = [(c.panel_product.id, c.panel_product) for c in Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            
    #         self.fields['panel_product'].choices = set(myChoices2)
    #         self.fields['panel_product'].widget.attrs.update({
    #                 'class': 'form-control floating-control',
    #                 'data-placeholder': 'Select an option'
    #             })
    #     except Exception as e:
    #         print("Exce==>", e)
    #         pass
    #     # self.fields['category'].choices = [(c.categories.id, c.categories) for c in EnquirySpecifications.objects.filter(enquiry=enquiry_id)]
    #     self.fields['category'].choices = set(myChoices)
    #     self.fields['category'].widget.attrs.update({
    #             'class': 'form-control floating-control',
    #             'data-placeholder': 'Select an option'
    #         })

        
    #     self.fields['boq_number'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
    #                                                        queryset=BillofQuantity.objects.filter(enquiry=enquiry_id).distinct('boq_number'), 
    #                                                        empty_label="Select BoQ Number",
    #                                                        required=False)
    #     self.fields['specification_Identifier'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                                        #  queryset=Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id).order_by('id'), 
                                                                        #  empty_label="Select a Identifier",  required=True)
    
    
    def __init__(self, enquiry_id, *args, **kwargs):
        super(TempCreateEstimationProductForm, self).__init__(*args, **kwargs)
        myChoices = [(c.categories.id, c.categories.category) for c in Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id).order_by('categories')]
        myChoices = [('', 'Select a Category')] + myChoices
        try:
            # myChoices2 = [(c.panel_specification.id, c.panel_specification) for c in EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            myChoices2 = [(c.panel_product.id, c.panel_product) for c in Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            myChoices2.insert(0, ('', 'Select a Product'))
            self.fields['panel_product'].choices = set(myChoices2)
            self.fields['panel_product'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        except Exception as e:
            self.fields['panel_product'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        

        self.fields['category'].choices = set(myChoices)
        self.fields['category'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an option'
            })
        self.fields['category'].empty_label = 'Select a Category'

        
        self.fields['boq_number'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                           queryset=BillofQuantity.objects.filter(enquiry=enquiry_id).distinct('boq_number'), 
                                                           empty_label="Select BoQ Number",
                                                           required=False)
        self.fields['specification_Identifier'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                                         queryset=Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id).order_by('id'), 
                                                                         empty_label="Select a Identifier", required=True)

    
    
    TOLERANCE = [
        ('', 'Select a tolerance unit'),
        (1, 'Percentage'),
        (2, 'Fixed Value'),
    ]

    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label="Select a Category")
    category.widget.attrs.update({
                            'class': 'form-control floating-control',
                            'data-placeholder': 'Select an option',
                            
                        })

    product = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1), required=False, empty_label="Select a Product")
    product.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                        
                    })

    panel_product = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1), required=False, empty_label="Select a Product")
    panel_product.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })

    brand = forms.ModelChoiceField(queryset=CategoryBrands.objects.all(), required=False, empty_label="Select a Brand")
    brand.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                        
                    })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all(), required=False,
                                   empty_label="Select a Brand")
    panel_brand.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
        
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all(), required=False, empty_label="Select a Series")
    panel_series.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option',
                        # 'disabled': True
                        
                    })

    series = forms.ModelChoiceField(queryset=Profile_Kit.objects.all(), required=False,
                                    empty_label="Select a Series")
    series.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
        # 'disabled': True
        
    })

    uom = forms.ModelChoiceField(queryset=UoM.objects.all(), empty_label="Select a Unit")
    uom.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })
    accessories = forms.ModelChoiceField(queryset=AccessoriesKit.objects.all(), required=False, empty_label="Select a Accessory")
    accessories.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })
    tolerance_type = forms.ChoiceField(choices=TOLERANCE,  required=False, widget=forms.Select(attrs={
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    }))
    
    supplier = forms.ModelChoiceField(queryset=Suppliers.objects.all(), required=False, empty_label="Select a Supplier")
    supplier.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })
    specification_Identifier = forms.ModelChoiceField(queryset=EnquirySpecifications.objects.all(), required=False, empty_label="Select a Identifier")
    specification_Identifier.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })

    class Meta:
        model = Temp_EstimationMainProduct
        fields = [
                    'category',
                    'product',
                    'brand',
                    'panel_brand',
                    'series',
                    'panel_series',
                    'uom',
                    'accessories',
                    'is_accessory',
                    'tolerance_type',
                    'tolerance',
                    'panel_product',
                    'accessory_quantity',
                    'is_tolerance',
                    'is_sourced',
                    'supplier',
                    'boq_number',
                    'specification_Identifier',
                    'enable_addons',
                    
                    'is_display_data',
                    'display_width',
                    'display_product_name',
                    'display_height',  
                    'display_area',
                    'display_quantity',
                    'display_total_area',
                    'hide_dimension',
                    
                 ]
        widgets = {
            'is_display_data': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                }
            ),
            'display_product_name': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'display_width': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'display_height': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'display_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'readonly': True,
                }
            ),
            'display_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'display_total_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'readonly': True,
                }
            ),
            
            'tolerance': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'accessory_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-5',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'is_tolerance': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_sourced': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'enable_addons': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_accessory': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'hide_dimension': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
        }


class TempCreateEstimationProductAluminiumForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kit_id = kwargs.pop('kit_id')
        super(TempCreateEstimationProductAluminiumForm, self).__init__(*args, **kwargs)
        self.fields['surface_finish'].queryset = Surface_finish_kit.objects.filter(master=kit_id)
        self.fields['surface_finish'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an option'
            })
        self.fields['surface_finish'].empty_label = 'Select a Surface Finish'
        
    UNIT = [
        (1, 'Pricing for SqM'),
        (2, 'Pricing for Unit'),
        (3, 'Pricing for KG'),
        # (4, "Formula Based"),
        
    ]
    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
        (4, 'Formula Based'),
    ]

    pricing_unit = forms.ChoiceField(choices=UNIT, required=False, widget=forms.Select(attrs={
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
    }))
    aluminium_pricing = forms.ChoiceField(choices=PRICING_TYPE, initial=3, required=False, widget=forms.RadioSelect(attrs={
        'class': 'form-check-input',
        'data-placeholder': 'Select an option',
        'style': "border: 1px solid #009ef7;",
    }))
    
    surface_finish = forms.ModelChoiceField(queryset=Surface_finish.objects.all(), required=False, empty_label='Select an Option')
    surface_finish.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option'
    })

    class Meta:
        model = Temp_MainProductAluminium
        fields = [
                    'aluminium_pricing',
                    'pricing_unit',
                    'custom_price',
                    'width',
                    'height',
                    'area',
                    'quantity',
                    'total_area',
                    'total_weight',
                    'product_type',
                    'product_description',
                    'price_per_kg',
                    'weight_per_unit',
                    'al_markup',
                    'al_quoted_price',
                    'enable_divisions',
                    'horizontal',
                    'vertical',
                    'total_linear_meter',
                    'weight_per_lm',
                    'surface_finish',
                    'in_area_input',
                    'curtainwall_type',
                    'total_quantity',

                 ]
        widgets = {
            'al_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'al_quoted_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'price_per_kg': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'weight_per_unit': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'custom_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    # 'placeholder': 'Price',
                }
            ),
            'width': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$'
                    
                }
            ),
            'height': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+\s*$'
                    
                }
            ),
            'curtainwall_type': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'total_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                    'readonly': True,
                }
            ),
            'area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'total_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'total_weight': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'product_type': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'required': True
                }
            ),
            'product_description': forms.Textarea(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'cols': '5',
                    'rows': '4',
                    'placeholder': 'Product Description',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'horizontal': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'vertical': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'enable_divisions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'total_linear_meter': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'weight_per_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'in_area_input': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
        }
        

class TempCreateEstimationProductGlassForm(forms.ModelForm):
    def __init__(self, enquiry_id, *args, **kwargs):
        super(TempCreateEstimationProductGlassForm, self).__init__(*args, **kwargs)
        try:
            myChoices = [(c.panel_specification.id, c.panel_specification.specifications) for c in
                        Temp_EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
            myChoices.insert(0, ('', 'Select a Glass'))
            self.fields['glass_specif'].choices = set(myChoices)
            self.fields['glass_specif'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        except Exception as e:
            self.fields['glass_specif'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })

    PRICING_TYPE = [
        (1, 'Predefined Prices'),
        (2, 'Custom Pricing'),
        (3, 'None'),
    ]

    glass_pricing_type = forms.ChoiceField(choices=PRICING_TYPE, initial=3, required=False,
                                          widget=forms.RadioSelect(attrs={
                                              'class': 'form-check-input glcosting',
                                              'data-placeholder': 'Select an option'
                                          }))

    class Meta:
        model = Temp_MainProductGlass
        fields = [
                    'glass_specif',
                    'is_glass_cost',
                    'total_area_glass',
                    'glass_base_rate',
                    'glass_markup_percentage',
                    'glass_quoted_price',
                    # 'glass_price_per_sqm',
                    # 'glass_primary',
                    
                    'glass_width',
                    'glass_height',
                    'glass_area',
                    'glass_quantity',
                    # 'glass_total_area',
                    'glass_pricing_type',
        ]
        widgets = {
            'is_glass_cost': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            # 'glass_primary': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input',
            #     }
            # ),
            'total_area_glass': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; text-align: right; padding-right: 20px;',
                    'required': False,
                }
            ),
            'glass_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; text-align: right; padding-right: 20px;',
                }
            ),
            'glass_markup_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; text-align: right; padding-right: 20px;',
                }
            ),
            'glass_quoted_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px; text-align: right; padding-right: 20px;',
                    # 'disabled': True,
                }
            ),
            # 'glass_price_per_sqm': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px; padding-right: 20px;',
            #     }
            # ),
            'glass_width': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_height': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control measurement fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_area': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'glass_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            # 'glass_total_area': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),

        }
    

class TempCreatePricingRuleForm(forms.ModelForm):

    class Meta:
        model = Temp_PricingOption
        exclude = ['estimation_product', 'created_date']
        widgets = {
            'is_pricing_control': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'adjust_by_sqm': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'overhead_perce': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'labour_perce': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
        }


class TempCreateMainProductAddons(forms.ModelForm):
    PRICING_TYPE = [
        ('', "Select Price Type"),
        (1, 'Price per Linear Meter'),
        (2, 'Price per Square Meter'),
        (3, 'Price per Unit')
    ]
    pricing_type = forms.ChoiceField(choices=PRICING_TYPE, required=False, widget=forms.Select(attrs={
                        'class': 'form-select mb-2 form-control floating-control addon_type',
                        'data-placeholder': 'Select an option'
                    }))
    addons = forms.ModelChoiceField(queryset=Addons.objects.all().exclude(linear_meter=0.000, sqm=0.000, unit=0.000), required=False, empty_label="Select a Addon")
    addons.widget.attrs.update({
        'class': 'form-control floating-control selection_addon',
        'data-placeholder': 'Select an option'
    })

    class Meta:
        model = Temp_MainProductAddonCost
        fields = [
                'addons',
                'base_rate',
                'pricing_type', 
                'addon_quantity',
            ]

        widgets = {
            'base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control addon_rate fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'addon_quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control addon_quantity fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
        }

class TempUpdateLabourAndOverhead(forms.ModelForm):
    class Meta:
        model = Temp_PricingOption
        fields = ['overhead_perce', 'labour_perce']
        widgets = {
            'overhead_perce': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                    
                }
            ),
            'labour_perce': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                    
                }
            ),
        }

class TempUpdateAluminiumPercentage(forms.ModelForm):
    class Meta:
        model = Temp_MainProductAluminium
        fields = ['al_markup']
        widgets = {
            'al_markup': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                    
                }
            ),
        }

class TempUpdateGlassPercentage(forms.ModelForm):
    class Meta:
        model = Temp_MainProductGlass
        fields = ['glass_markup_percentage']
        # fields = ['markup_percentage', 'sec_markup_percentage']
        widgets = {
            'glass_markup_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                    
                }
            ),
        }

class TempUpdateTolerance(forms.ModelForm):
    class Meta:
        model = EstimationMainProduct
        fields = ['tolerance']
        widgets = {
            'tolerance': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'style': 'min-height: 0px;border-bottom: none;background-color:#fff0;'
                }
            ),
        }

# temporories

class TempCreateQuotationsForm(forms.ModelForm):
    signature = forms.ModelChoiceField(queryset=Signatures.objects.all(), initial=1)
    signature.widget.attrs.update({
        'class': 'form-select mb-2',
    })
    DISCOUNT_TYPE = [
        (0, 'None'),
        (1, 'Percentage'),
        (2, 'Fixed Value'),
    ]
    
    discount_type = forms.ChoiceField(choices=DISCOUNT_TYPE, required=False, widget=forms.Select(attrs={
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    }))

    class Meta:
        model = Temp_Quotations
        exclude = [
                        'created_by', 'created_date', 'prepared_for', 
                        'represented_by', 'estimations_version', 
                        'estimations', 'products_specifications'
                  ]
        # fields = '__all__'
        widgets = {
            'quotation_id': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-flush fw-bolder text-muted fs-3 w-125px',
                    'readonly':'readonly',
                    'placeholder': 'Q-ID'
                }
            ),
            'quotation_date': forms.DateInput(
                attrs={
                    'class': 'form-control fw-bolder  q_date px-1 py-0',
                    'placeholder': 'Select date',
                    'type': 'date'
                }
            ),
            'valid_till': forms.DateInput(
                attrs={
                    'class': 'form-control  fw-bolder px-1 py-0 q_valid',
                    'placeholder': 'Select date',
                    'type': 'date'

                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '3'
                }
            ),
            'other_notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '3'
                }
            ),
            'display_discount_perc': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'remarks': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '10'
                }
            ),
            'terms_of_payment': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '10'
                }
            ),
            'quote_price': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'hidden',
                }
            ),
            'exclusions': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '6'
                }
            ),
            'terms_and_conditions': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '40',
                    'rows': '30'
                }
            ),
            'signature': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                }
            ),
            'is_provisions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'custom_specifictaion': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input me-3 h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'apply_total': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'apply_line_items': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'discount': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Discount',
                }
            ),
            'building_total_enable': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'cols': '6',
                    'rows': '3',
                    'placeholder': 'Quotation Discount Notes... (Optional)',
                }
            ),
            'is_dimensions': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
            'is_quantity': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
            'is_rpu': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
            'is_rpsqm': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
            'is_area': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input column_control',
                }
            ),
        }


# class TempCreateShortQuotationsForm(forms.ModelForm):
#     signature = forms.ModelChoiceField(queryset=Signatures.objects.all(), initial=1)
#     signature.widget.attrs.update({
#         'class': 'form-select mb-2',
#         # 'data-control': 'select2',
#         # 'data-hide-search': 'true',
#         # 'data-placeholder': 'Select an option'
#     })
    
#     DISCOUNT_TYPE = [
#         (0, 'None'),
#         (1, 'Percentage'),
#         (2, 'Fixed Value'),
#     ]
    
#     discount_type = forms.ChoiceField(choices=DISCOUNT_TYPE, required=False, widget=forms.Select(attrs={
#         'class': 'form-select mb-2',
#         # 'data-control': 'select2',
#         # 'data-hide-search': 'true',
#         'data-placeholder': 'Select an option'
#     }))

#     class Meta:
#         model = Temp_Quotations
#         exclude = ['created_by', 'created_date', 'prepared_for', 'represented_by', 'estimations_version', 'estimations', 'terms_of_payment', 'products_specifications', 'exclusions']
#         # fields = '__all__'
#         widgets = {
#             'quotation_id': forms.TextInput(
#                 attrs={
#                     'class': 'form-control form-control-flush fw-bolder text-muted fs-3 w-125px',
#                 }
#             ),
#             'quotation_date': forms.DateInput(
#                 attrs={
#                     'class': 'form-control form-control-transparent fw-bolder pe-5',
#                     'placeholder': 'Select date',
#                     'type': 'date'
#                 }
#             ),
#             'valid_till': forms.DateInput(
#                 attrs={
#                     'class': 'form-control form-control-transparent fw-bolder pe-5',
#                     'placeholder': 'Select date',
#                     'type': 'date'

#                 }
#             ),
#             'description': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '40',
#                     'rows': '3'
#                 }
#             ),
#             'other_notes': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '40',
#                     'rows': '3'
#                 }
#             ),
#             'remarks': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '40',
#                     'rows': '10'
#                 }
#             ),
#             'terms_and_conditions': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '40',
#                     'rows': '15'
#                 }
#             ),
#             'signature': forms.TextInput(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                 }
#             ),
            
#             'apply_total': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input',
#                 }
#             ),
#             'custom_specifictaion': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input me-3 h-20px w-30px',
#                     'style': 'border: 1px solid #009ef7;',
#                 }
#             ),
#             'apply_line_items': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input',
#                 }
#             ),
#             'discount': forms.TextInput(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'placeholder': 'Discount',
#                 }
#             ),
#             'building_total_enable': forms.CheckboxInput(
#                 attrs={
#                     'class': 'form-check-input',
#                 }
#             ),
#             'notes': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid',
#                     'cols': '6',
#                     'rows': '3',
#                     'placeholder': 'Quotation Discount Notes... (Optional)',
#                 }
#             ),
#         }


class TempCreateMainProductSilicon(forms.ModelForm):
    # def __init__(self, sealant_pricing_id=None, *args, **kwargs):
    #     super(TempCreateMainProductSilicon, self).__init__(*args, **kwargs)
        # if sealant_pricing_id:
          
            # self.fields['external_sealant_type'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
            # self.fields['external_sealant_type'].widget.attrs.update({
            #             'class': 'form-control floating-control',
            #             'data-placeholder': 'Select an option'
            #         })
            # self.fields['external_sealant_type'].empty_label = 'Select an option'
            # self.fields['internal_sealant_type'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
            # self.fields['internal_sealant_type'].widget.attrs.update({
            #             'class': 'form-control floating-control',
            #             'data-placeholder': 'Select an option'
            #         })
            # self.fields['internal_sealant_type'].empty_label = 'Select an option'
            
            # self.fields['polyamide_gasket'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
            # self.fields['polyamide_gasket'].widget.attrs.update({
            #             'class': 'form-control floating-control',
            #             'data-placeholder': 'Select an option'
            #         })
            # self.fields['polyamide_gasket'].empty_label = 'Select an option'
            
            # self.fields['transom_gasket'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
            # self.fields['transom_gasket'].widget.attrs.update({
            #             'class': 'form-control floating-control',
            #             'data-placeholder': 'Select an option'
            #         })
            # self.fields['transom_gasket'].empty_label = 'Select an option'
            
            # self.fields['mullion_gasket'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
            # self.fields['mullion_gasket'].widget.attrs.update({
            #             'class': 'form-control floating-control',
            #             'data-placeholder': 'Select an option'
            #         })
            # self.fields['mullion_gasket'].empty_label = 'Select an option'
            
            # self.fields['epdm_gasket'].queryset = Sealant_kit.objects.filter(pricing_master=sealant_pricing_id)
            # self.fields['epdm_gasket'].widget.attrs.update({
            #             'class': 'form-control floating-control',
            #             'data-placeholder': 'Select an option'
            #         })
            # self.fields['epdm_gasket'].empty_label = 'Select an option'
            
            
            
    
    class Meta:
        model = Temp_MainProductSilicon
        fields = [
            'is_silicon',
            
            # 'is_external',
            'external_lm',
            # 'is_internal',
            'internal_lm',
            'silicon_quoted_price',
            'external_markup',
            'internal_markup',
            'internal_base_rate',
            'external_base_rate',
            'external_sealant_type',
            'internal_sealant_type',
            'polyamide_gasket',
            'polyamide_markup',
            'transom_gasket',
            'transom_markup',
            'mullion_gasket',
            'mullion_markup',
            # 'epdm_gasket',
            # 'epdm_markup',
            'polyamide_lm',
            'transom_lm',
            'mullion_lm',
            # 'epdm_lm',
            'polyamide_base_rate',
            'transom_base_rate',
            'mullion_base_rate',
            # 'epdm_base_rate',
        ]
        widgets = {
            # 'epdm_base_rate': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
            'mullion_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'polyamide_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'transom_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'polyamide_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            # 'epdm_lm': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
            'mullion_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'transom_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'polyamide_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'mullion_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'transom_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'polyamide_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            # 'epdm_markup': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control fs-4',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
            'is_silicon': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            # 'is_external': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-30px',
                    #   'style': 'border: 1px solid #009ef7;',
            #     }
            # ),
            # 'is_internal': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-30px',
                    #   'style': 'border: 1px solid #009ef7;',
            #     }
            # ),
            # 'silicon_base_rate': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
            # 'silicon_markup_percentage': forms.TextInput(
            #     attrs={
            #         'class': 'form-control floating-control ',
            #         'style': 'border-radius:0px; padding-top: 20px;',
            #     }
            # ),
            'external_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'internal_lm': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'silicon_quoted_price': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                    'type': 'hidden'
                    
                }
            ),
            'external_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'internal_base_rate': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'external_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'internal_markup': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control fs-4',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'external_sealant_type': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            'internal_sealant_type': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            'polyamide_gasket': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            'transom_gasket': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            'mullion_gasket': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            ),
            # 'epdm_gasket': forms.TextInput(
            #     attrs={
            #         'type': 'hidden'
            #     }
            # ),
        }
        
class ProductComplaintsForm(forms.ModelForm):
    class Meta:
        model = EstimationProductComplaints
        fields = [
            'is_aluminium_complaint',
            'aluminium_complaint',
            'is_panel_complaint',
            'panel_complaint',
            'is_surface_finish_complaint',
            'surface_finish_complaint'
        ]
        
        widgets = {
            'is_aluminium_complaint': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_panel_complaint': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_surface_finish_complaint': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'aluminium_complaint': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'style': 'min-height: 40px; padding-left: 5px;'
                }
            ),
            'panel_complaint': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'style': 'min-height: 40px; padding-left: 5px;'
                }
            ),
            'surface_finish_complaint': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'style': 'min-height: 40px; padding-left: 5px;'
                }
            ),
        }
        
class TempProductComplaintsForm(forms.ModelForm):
    class Meta:
        model = Temp_EstimationProductComplaints
        fields = [
            'is_aluminium_complaint',
            'aluminium_complaint',
            'is_panel_complaint',
            'panel_complaint',
            'is_surface_finish_complaint',
            'surface_finish_complaint'
        ]
        
        widgets = {
            'is_aluminium_complaint': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_panel_complaint': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'is_surface_finish_complaint': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                    'style': 'border: 1px solid #009ef7;',
                }
            ),
            'aluminium_complaint': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'style': 'min-height: 40px; padding-left: 5px;'
                }
            ),
            'panel_complaint': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'style': 'min-height: 40px; padding-left: 5px;'
                }
            ),
            'surface_finish_complaint': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'style': 'min-height: 40px; padding-left: 5px;'
                }
            ),
        }
        

class CreateQuoteSendDetailForm(forms.ModelForm):
    STATUS = [
        ('', 'Send by'),
        (1, 'By Hand'),
        (2, 'Email'),
        (3, 'Fax'),
    ]
    
    status = forms.ChoiceField(choices=STATUS, required=False, widget=forms.Select(attrs={
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    }))
    
    class Meta:
        model = Quote_Send_Detail
        fields = [
            'status',
            'notes',
            'send_date',
            ]
        widgets = {
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid p-2',
                    'cols': '10',
                    'rows': '3',
                    'required': True,
                }
            ),
            
            'send_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'date',
                    'style': 'padding: 5px;'
                    
                }
            ),
        }
        

class ProductCommentsForm(forms.ModelForm):
    class Meta:
        model = ProductComments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid p-2 mb-3',
                    'cols': '10',
                    'rows': '3',
                    
                }
            ),
        }
        

class TempProductCommentsForm(forms.ModelForm):
    class Meta:
        model = Temp_ProductComments
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid p-2 mb-3',
                    'cols': '10',
                    'rows': '3',
                    
                }
            ),
        }


# class CreateVersionHistory(forms.ModelForm):
#     class Meta:
#         model = VersionHistory
#         fields = ['history_notes']
#         widgets = {
#             'history_notes': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid p-2 mb-3',
#                     'rows': '3',
#                     'placeholder': 'Revision Note..'
#                 }
#             )
#         }
        

# class Temp_CreateVersionHistory(forms.ModelForm):
#     class Meta:
#         model = Temp_VersionHistory
#         fields = ['history_notes']
#         widgets = {
#             'history_notes': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid p-2 mb-3',
#                     'rows': '3',
#                     'placeholder': 'Revision Note..'
                    
#                 }
#             )
#         }


# class CreateHistoryComment(forms.ModelForm):
#     class Meta:
#         model = VersionHistoryComments
#         fields = ['comments']
#         widgets = {
#             'comments': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid p-2 mb-3',
#                     'rows': '3',
#                     'placeholder': 'Comment...'
                    
#                 }
#             )
#         }
class CreateHistoryComment(forms.ModelForm):
    
    class Meta:
        model = Quotation_Notes_Comments
        fields = ['comments']
        widgets = {
            'comments': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid p-2 mb-3',
                    'rows': '3',
                    'placeholder': 'Comment...'
                    
                }
            )
        }

# class Temp_CreateHistoryComment(forms.ModelForm):
#     class Meta:
#         model = Temp_VersionHistoryComments
#         fields = ['comments']
#         widgets = {
#             'comments': forms.Textarea(
#                 attrs={
#                     'class': 'form-control form-control-solid p-2 mb-3',
#                     'rows': '3',
#                     'placeholder': 'Comment...'
                    
#                 }
#             )
#         }

class Temp_CreateHistoryComment(forms.ModelForm):
    
    class Meta:
        model = Temp_Quotation_Notes_Comments
        fields = ['comments']
        widgets = {
            'comments': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid p-2 mb-3',
                    'rows': '3',
                    'placeholder': 'Comment...'
                    
                }
            )
        }
        
class CreateQuotationNote(forms.ModelForm):
    # tag = forms.ModelChoiceField(queryset=Tags.objects.get(pk=1), empty_label='Tag')
    # tag.widget.attrs.update({
    #     'class': 'form-control form-control-solid',
    #     # 'data-control': 'select2',
    #     # 'data-hide-search': 'true',
    #     'data-placeholder': 'Select an option'
    # })
    class Meta:
        model = Quotation_Notes
        fields = ['quotation_notes', 'quote_value']
        widgets = {
            'quotation_notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid p-2 mb-3',
                    'rows': '10',
                    'placeholder': 'Quotation Notes...'
                    
                }
            ),
            'quote_value': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            )
        }
        
        
        
class Temp_CreateQuotationNote(forms.ModelForm):
    # tag = forms.ModelChoiceField(queryset=Tags.objects.all().order_by('-id'), empty_label='Tag')
    # tag.widget.attrs.update({
    #     'class': 'form-control form-control-solid ',
    #     # 'data-control': 'select2',
    #     # 'data-hide-search': 'true',
    #     'data-placeholder': 'Select an option'
    # })
    class Meta:
        model = Temp_Quotation_Notes
        fields = ['quotation_notes', 'quote_value']
        widgets = {
            'quotation_notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid p-2 mb-3',
                    'rows': '10',
                    'placeholder': 'Quotation Notes...'
                    
                }
            ),
            'quote_value': forms.TextInput(
                attrs={
                    'type': 'hidden'
                }
            )
        }
def deduction_items_form(pk):
    class Deduction_ItemsForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(Deduction_ItemsForm, self).__init__(*args, **kwargs)
            
            self.fields['item_desc'].empty_label = "Product Description"
            # self.fields['item_desc'].queryset = EstimationMainProduct.objects.filter(pk=pk) 
            self.fields['item_desc'].queryset = MainProductGlass.objects.filter(estimation_product=pk).distinct()
            self.fields['item_desc'].label_from_instance = self.set_label
            self.fields['item_desc'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        def set_label(self, obj):
            return f'{obj.glass_specif.specifications}'
            
            
        class Meta:
            model = Deduction_Items
            fields = [
                "item_desc",
                # "main_price",
                "item_width",
                "item_height",
                "item_quantity",
                "item_deduction_area",
                "item_deduction_price"
            ]
            
            widgets = {
                'item_width': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 item_width',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Width",
                    }
                ),
                'item_height': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 item_height',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Height",
                        
                    }
                ),
                'item_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 item_quantity',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Quantity",
                        
                    }
                ),
                'item_deduction_area': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 deduction_total_area',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Total Area",
                        
                    }
                ),
                'item_deduction_price': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 deduction_price',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Price",
                    }
                ),
            }
    return Deduction_ItemsForm

def temp_deduction_items_form(pk):
    class Temp_Deduction_ItemsForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(Temp_Deduction_ItemsForm, self).__init__(*args, **kwargs)
            
            self.fields['item_desc'].empty_label = "Product Description"
            # self.fields['item_desc'].queryset = EstimationMainProduct.objects.filter(pk=pk) 
            self.fields['item_desc'].queryset = Temp_MainProductGlass.objects.filter(estimation_product=pk).distinct()
            self.fields['item_desc'].label_from_instance = self.set_label
            self.fields['item_desc'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        def set_label(self, obj):
            return f'{obj.glass_specif.specifications}'
        
        class Meta:
            model = Temp_Deduction_Items
            fields = [
                "item_desc",
                # "main_price",
                "item_width",
                "item_height",
                "item_quantity",
                "item_deduction_area",
                "item_deduction_price"
            ]
            
            widgets = {
                
                'item_width': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 item_width',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Width",
                    }
                ),
                'item_height': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 item_height',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Height",
                        
                    }
                ),
                'item_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 item_quantity',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Quantity",
                        
                    }
                ),
                'item_deduction_area': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 deduction_total_area',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Total Area",
                        
                    }
                ),
                'item_deduction_price': forms.TextInput(
                    attrs={
                        'class': 'form-control floating-control fs-4 deduction_price',
                        'style': 'border-radius:0px; padding-top: 20px;',
                        'placeholder': "Price",
                    }
                ),
            }
    return Temp_Deduction_ItemsForm

# class CreateEstimationProjectSpec(forms.ModelForm):
#     # specification_header = forms.ModelChoiceField(queryset=ProjectSpecifications.objects.all(), empty_label='Tag')
#     # specification_header.widget.attrs.update({
#     #     'class': 'form-control form-control-solid',
#     #     # 'data-control': 'select2',
#     #     # 'data-hide-search': 'true',
#     #     'data-placeholder': 'Select an option'
#     # })
#     class Meta:
#         model = EstimationProjectSpecifications
#         fields = ['specification_header', 'specification']
#         widgets = {
#                 'specification': forms.TextInput(
#                     attrs={
#                         'class': 'form-control floating-control fs-4',
#                         'style': 'border-radius:0px; padding-top: 20px;',
#                         'placeholder': "Specification",
#                     }
#                 ),
#         }

# class AddTypicalBuilding(forms.ModelForm):
#     class Meta:
#         model = EstimationBuildings
#         fields = ['no_typical_buildings', 'typical_buildings_enabled']
        