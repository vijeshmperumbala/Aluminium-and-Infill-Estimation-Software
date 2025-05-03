from django import forms

from apps.brands.models import CategoryBrands
from apps.companies.models import Companies
# from apps.configuration_master.models import (
#     ConfigurationMasterBrands, 
#     ConfigurationMasterSeries, 
#     ConfigurationMasterBase,
#     )
from apps.enquiries.models import (
        Enquiries, 
        Enquiry_Discontinued_History, 
        EnquirySpecifications, 
        EstimationNotes, 
        Temp_EstimationNotes,
)
from apps.customers.models import Customers
# from apps.Categories.models import Category
# from apps.enquiry_type.models import EnquiryTypeModal
# from apps.surface_finish.models import Surface_finish
from apps.industry_type.models import IndustryTypeModal
# from apps.panels_and_others.models import (
#                     PanelMasterBase, 
#                     PanelMasterBrands, 
#                     PanelMasterSeries, 
#                     PanelMasterSpecifications,
#                 )
from apps.pricing_master.models import AdditionalandLabourPriceMaster, SealantPriceMaster
# from apps.product_master.models import Product
from apps.estimations.models import MainProductAluminium
# from apps.tags.models import Tags
from apps.user.models import User

    
class CreateEnquiryForm(forms.ModelForm):
    TYPE = [
        (1, 'Client'),
        (2, 'In House'),
    ]
    PRICING_TYPE = [
        (1, 'International'),
        (2, 'Local')
    ]
    
    ENQUIRY_TYPE = [
        (1, 'Ongoing'),
        (2, 'Tender'),
    ]
    

    enquiry_category = forms.ChoiceField(choices=TYPE, widget=forms.Select(attrs={
        'class': 'form-control floating-control mb-2',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status',
        'style': "border-radius:0px; padding-top: 10px;"
        
    }))
    
    pricing_type_select = forms.ChoiceField(choices=PRICING_TYPE, initial=2, widget=forms.Select(attrs={
        'class': 'form-control floating-control mb-2',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status',
        'style': "border-radius:0px; padding-top: 10px;"
        
    }))

    customers = forms.ModelMultipleChoiceField(queryset=Customers.objects.all().order_by('name'))
    customers.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select an option',
        'multiple': 'true',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    
    enquiry_members = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_superuser=False).order_by('name'), required=False)
    enquiry_members.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select Members',
        'multiple': 'true',
        'style': "border-radius:0px; padding-top: 10px;"
    })
    
    try:
        additional_and_labour = forms.ModelChoiceField(queryset=AdditionalandLabourPriceMaster.objects.all().order_by('-id'), 
                                                   initial=AdditionalandLabourPriceMaster.objects.last() , empty_label='Select an Option')
    except Exception:
        additional_and_labour = forms.ModelChoiceField(queryset=AdditionalandLabourPriceMaster.objects.all().order_by('-id'), empty_label='Select an Option')
    
    additional_and_labour.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Select an option',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    try:
        sealant_pricing = forms.ModelChoiceField(queryset=SealantPriceMaster.objects.all().order_by('-id'), initial=SealantPriceMaster.objects.last() , empty_label='Select an Option')
    except Exception:
        sealant_pricing = forms.ModelChoiceField(queryset=SealantPriceMaster.objects.all().order_by('-id'), empty_label='Select an Option')
    sealant_pricing.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Select an option',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    
    # enquiry_type = forms.ModelChoiceField(queryset=EnquiryTypeModal.objects.all(), empty_label='Select an Option')
    # enquiry_type.widget.attrs.update({
    #     'class': 'form-select mb-2',
    #     'data-placeholder': 'Select an option'
    # })
    enquiry_type = forms.ChoiceField(choices=ENQUIRY_TYPE, widget=forms.Select(attrs={
        'class': 'form-control floating-control mb-2',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status',
        'style': "border-radius:0px; padding-top: 10px;"
        
    }))
    
    company = forms.ModelChoiceField(queryset=Companies.objects.all().order_by('company_name'), empty_label='Select an Option')
    company.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        'data-placeholder': 'Select an option',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    
    industry_type = forms.ModelChoiceField(queryset=IndustryTypeModal.objects.all().order_by('industry_type'), empty_label='Select an Option')
    industry_type.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        'data-placeholder': 'Select an option',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })

    class Meta:
        model = Enquiries
        fields = [
                    'title',
                    'enquiry_category',
                    'customers',
                    'received_date',
                    'due_date',
                    'additional_and_labour',
                    'sealant_pricing',
                    'pricing_type_select',
                    'enquiry_type',
                    'industry_type',
                    'company',
                    'enquiry_members',
                    'enquiry_id',
                ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'placeholder': 'Project Title',
                    "required": True,
                    'style': "border-radius:0px; padding-top: 10px;"
                    
                }
            ),
            
            'received_date': forms.DateInput(
                attrs={
                    'class': 'form-control floating-control',
                    'type': 'date',
                    "required": True,
                    'style': "border-radius:0px; padding-top: 10px;"
                    
                }
            ),
            'due_date': forms.DateInput(
                attrs={
                    'class': 'form-control floating-control',
                    'type': 'date',
                    "required": True,
                    'style': "border-radius:0px; padding-top: 10px;"
                }
            ),
            'enquiry_id': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'placeholder': 'Enquiry Id',
                    "required": True,
                    'style': "border-radius:0px; padding-top: 10px;"
                    
                }
            ),
            

        }


# class Tender_customerForm(forms.ModelForm):
#     tender_customers = forms.ModelMultipleChoiceField(queryset=Customers.objects.all(), required=False)
#     tender_customers.widget.attrs.update({
#         'class': 'form-select mb-2',
#         'data-control': 'select2',
#         'data-hide-search': 'true',
#         'multiple': 'true',
#         'placeholder': 'Select an option',
#         'allowClear': 'true'
#     })
#     class Meta:
#         model = Tender_Customers
#         fields = [
#             'tender_customers',
#         ]
        
        
class EditMainEnquiryForm(forms.ModelForm):
    TYPE = [
        (1, 'Client'),
        (2, 'In House'),
    ]
    
    PRICING_TYPE = [
        (1, 'International'),
        (2, 'Local')
    ]
    
    ENQUIRY_TYPE = [
        (1, 'Ongoing'),
        (2, 'Tender'),
    ]
    
    STATUS = [
    #    ("", "Select a Status"),
    #    (2, 'Estimating'),
       (0, 'Status'),
       (1, 'Active'),
       (4, 'Inactive'),
       (7, 'Enquiry On Hold'),
    ]

    enquiry_category = forms.ChoiceField(choices=TYPE, widget=forms.Select(attrs={
        'class': 'form-control floating-control',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status',
        'style': "border-radius:0px; padding-top: 10px;"
        
    }))
    
    pricing_type_select = forms.ChoiceField(choices=PRICING_TYPE, initial=2, widget=forms.Select(attrs={
        'class': 'form-control floating-control',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status',
        'style': "border-radius:0px; padding-top: 10px;"
        
    }))
    status = forms.ChoiceField(choices=STATUS, required=False, widget=forms.Select(attrs={
        'class': 'form-control floating-control',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status',
        'style': "border-radius:0px; padding-top: 10px;"
        
    }))

    # customer = forms.ModelChoiceField(queryset=Customers.objects.all(), required=False, initial=1)
    # customer.widget.attrs.update({
    #     'class': 'form-select mb-2',
    #     'data-control': 'select2',
    #     'data-hide-search': 'true',
    #     'data-placeholder': 'Select an option'
    # })
    customers = forms.ModelMultipleChoiceField(queryset=Customers.objects.all().order_by('name'))
    customers.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        # # 'data-placeholder': 'Select an option',
        # 'multiple': 'true',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    
    enquiry_members = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_superuser=False).order_by('name'), required=False)
    enquiry_members.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select Members',
        'multiple': 'true',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    
    additional_and_labour = forms.ModelChoiceField(queryset=AdditionalandLabourPriceMaster.objects.all().order_by('-id'), empty_label='Select an Option')
    additional_and_labour.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Select an option',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    
    sealant_pricing = forms.ModelChoiceField(queryset=SealantPriceMaster.objects.all().order_by('-id'), empty_label='Select an Option')
    sealant_pricing.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Select an option',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    
    # enquiry_type = forms.ModelChoiceField(queryset=EnquiryTypeModal.objects.all(), empty_label='Select an Option')
    # enquiry_type.widget.attrs.update({
    #     'class': 'form-select mb-2',
    #     'data-placeholder': 'Select an option'
    # })
    
    enquiry_type = forms.ChoiceField(choices=ENQUIRY_TYPE, widget=forms.Select(attrs={
        'class': 'form-control floating-control mb-2',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status',
        'style': "border-radius:0px; padding-top: 10px;"
        
    }))
    
    industry_type = forms.ModelChoiceField(queryset=IndustryTypeModal.objects.all(), empty_label='Select an Option')
    industry_type.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        'data-placeholder': 'Select an option',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    
    company = forms.ModelChoiceField(queryset=Companies.objects.all().order_by('company_name'), empty_label='Select an Option')
    company.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        'data-placeholder': 'Select an option',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })


    class Meta:
        model = Enquiries
        fields = [
                    'title',
                    'enquiry_category',
                    'customers',
                    'received_date',
                    'due_date',
                    'additional_and_labour',
                    'sealant_pricing',
                    'pricing_type_select',
                    'enquiry_type',
                    'industry_type',
                    'company',
                    'enquiry_members',
                    'status',
                    'enquiry_id',
                ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'placeholder': 'Enquiry Title',
                    'style': "border-radius:0px; padding-top: 20px;",
                    'required': True,
                }
            ),
            'received_date': forms.DateInput(
                attrs={
                    'class': 'form-control floating-control',
                    'type': 'date',
                    'style': "border-radius:0px; padding-top: 20px;",
                    'required': True,
                }
            ),
            'due_date': forms.DateInput(
                attrs={
                    'class': 'form-control floating-control',
                    'type': 'date',
                    'style': "border-radius:0px; padding-top: 20px;",
                    'required': True,
                }
            ),
            'enquiry_id': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'placeholder': 'Enquiry Id',
                    "required": True,
                    'style': "border-radius:0px; padding-top: 10px;"
                }
            ),

        }


class CreateCustomerEnquiryForm(forms.ModelForm):
    
    TYPE = [
        (1, 'Client'),
        (2, 'In House'),
    ]
    PRICING_TYPE = [
        (1, 'International'),
        (2, 'Local')
    ]
    ENQUIRY_TYPE = [
        (1, 'Ongoing'),
        (2, 'Tender'),
    ]
    

    enquiry_category = forms.ChoiceField(choices=TYPE, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status'
    }))
    
    pricing_type_select = forms.ChoiceField(choices=PRICING_TYPE, initial=2, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status'
    }))
    try:
        additional_and_labour = forms.ModelChoiceField(queryset=AdditionalandLabourPriceMaster.objects.all().order_by('-id'), initial=AdditionalandLabourPriceMaster.objects.last() , empty_label='Select an Option')
    except Exception:
        additional_and_labour = forms.ModelChoiceField(queryset=AdditionalandLabourPriceMaster.objects.all().order_by('-id'), empty_label='Select an Option')
    additional_and_labour.widget.attrs.update({
        'class': 'form-select mb-2',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })
    
    try:
        sealant_pricing = forms.ModelChoiceField(queryset=SealantPriceMaster.objects.all().order_by('-id'), initial=SealantPriceMaster.objects.last() , empty_label='Select an Option')
    except Exception:
        sealant_pricing = forms.ModelChoiceField(queryset=SealantPriceMaster.objects.all().order_by('-id'), empty_label='Select an Option')
        
    sealant_pricing.widget.attrs.update({
        'class': 'form-select mb-2',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })
    
    enquiry_type = forms.ChoiceField(choices=ENQUIRY_TYPE, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Status',
        'data-kt-ecommerce-product-filter': 'status'
    }))
    
    industry_type = forms.ModelChoiceField(queryset=IndustryTypeModal.objects.all().order_by('industry_type'), empty_label='Select an Option')
    industry_type.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    })
    
    company = forms.ModelChoiceField(queryset=Companies.objects.all().order_by('company_name'), empty_label='Select an Option')
    company.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    })
    
    enquiry_members = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_superuser=False).order_by('name'), required=False)
    enquiry_members.widget.attrs.update({
        'class': 'form-control floating-control mb-2',
        'data-control': 'select2',
        'data-hide-search': 'true',
        'data-placeholder': 'Select Members',
        'multiple': 'true',
        'style': "border-radius:0px; padding-top: 10px;"
        
    })
    

    class Meta:
        model = Enquiries
        fields = [
                    'title',
                    'enquiry_category',
                    'received_date',
                    'due_date',
                    'additional_and_labour',
                    'sealant_pricing',
                    'pricing_type_select',
                    'enquiry_type',
                    'industry_type',
                    'company',
                    'enquiry_id',
                    'enquiry_members', 
                ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Project Title',
                    'required': True,
                }
            ),
            'enquiry_id': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Enquiry ID',
                    'required': True,
                }
            ),
            
            'received_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'date',
                    'required': True,
                }
            ),
            'due_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'date',
                    'required': True,
                }
            ),

        }


class EditEnquiryForm(forms.ModelForm):

    STATUS = [
        # (1, 'New'),
        (2, 'Active'),
        # (3, 'Submitted'),
        # (4, 'Review'),
        # (5, 'Completed'),
        (6, 'Cancelled'),
        (7, 'Enquiry On hold'),
    ]
    status = forms.ChoiceField(choices=STATUS, required=False, widget=forms.Select(attrs={
        'class': 'form-control',
        'data-placeholder': 'Status',
    }))
    
    sealant_pricing = forms.ModelChoiceField(queryset=SealantPriceMaster.objects.all().order_by('-id'), empty_label='Select an Option')
    sealant_pricing.widget.attrs.update({
        'class': 'form-control ',
        # 'data-control': 'select2',
        # 'data-hide-search': 'true',
        'data-placeholder': 'Select an option'
    })
    
    # surface_finish = forms.ModelChoiceField(queryset=Surface_finish.objects.all(), empty_label='Select an Option')
    # surface_finish.widget.attrs.update({
    #     'class': 'form-control ',
    #     # 'data-control': 'select2',
    #     # 'data-hide-search': 'true',
    #     'data-placeholder': 'Select an option'
    # })
    
    
    class Meta:
        model = Enquiries
        fields = [
                    'title',
                    'received_date',
                    'due_date',
                    'labour_percentage',
                    'overhead_percentage',
                    'price_per_kg',
                    # 'enquiry_active_status',
                    'status',
                    'sealant_pricing',
                    'price_per_kg_markup'
                    # 'structural_price',
                    # 'weather_price',
                    # 'surface_finish'
                ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enquiry Title',
                }
            ),
            'received_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Received Date',
                    'type': 'date'
                }
            ),
            'due_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Due Date',
                    'type': 'date'
                }
            ),
            'labour_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Labour Percentage',
                }
            ),
            'overhead_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Overhead Percentage',
                }
            ),
            'price_per_kg': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Price/KG',
                }
            ),
            'price_per_kg_markup': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Default Markup',
                }
            ),
            # 'structural_price': forms.TextInput(
            #     attrs={
            #         'class': 'form-control',
            #         'placeholder': 'Structural Sealant Price'
            #     }
            # ),
            # 'weather_price': forms.TextInput(
            #     attrs={
            #         'class': 'form-control',
            #         'placeholder': 'Weather Sealant Price '
            #     }
            # ),

        }


class EstimationProductDuplicate(forms.ModelForm):
    class Meta:
        model = MainProductAluminium
        fields = ['width', 'height', 'quantity', 'product_type', 'product_description']
        widgets = {
            'width': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'height': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'quantity': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'product_type': forms.TextInput(
                attrs={
                    'class': 'form-control floating-control',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            ),
            'product_description': forms.Textarea(
                attrs={
                    'class': 'form-control floating-control',
                    'cols': '5',
                    'rows': '4',
                    'placeholder': 'Estimation Description',
                    'style': 'border-radius:0px; padding-top: 20px;',
                }
            )
        }
        
class CreateEstimationNotesForms(forms.ModelForm):
    # tag = forms.ModelChoiceField(queryset=Tags.objects.filter(pk__gt=10).order_by('-id'), required=False, empty_label='Tag')
    # tag.widget.attrs.update({
    #     'class': 'form-select form-select-sm',
    #     # 'data-control': 'select2',
    #     # 'data-hide-search': 'true',
    #     'data-placeholder': 'Select an option'
    # })
    
    class Meta:
        model = EstimationNotes
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control floating-control mb-3',
                    'cols': '1',
                    'rows': '4',
                    'style': 'border-radius:0px; padding-top: 10px;',
                    'placeholder': 'Type a message',
                }
            )
        }
        
class TempCreateEstimationNotesForms(forms.ModelForm):
    # tag = forms.ModelChoiceField(queryset=Tags.objects.filter(pk__gt=10).order_by('-id'), required=False, empty_label='Tag')
    # tag.widget.attrs.update({
    #     'class': 'form-select ',
    #     # 'data-control': 'select2',
    #     # 'data-hide-search': 'true',
    #     'data-placeholder': 'Select an option'
    # })
    
    class Meta:
        model = Temp_EstimationNotes
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-flush mb-3',
                    'cols': '1',
                    'rows': '3',
                    'placeholder': 'Type a message',
                }
            )
        }


class EnquiryDiscontinuedHistoryForm(forms.ModelForm):
    class Meta:
        model = Enquiry_Discontinued_History
        fields = ["discontinue_note"]
        widgets = {
            'discontinue_note': forms.Textarea(
                attrs={
                    'class': 'form-control floating-control',
                    'cols': '1',
                    'rows': '4',
                    'placeholder': 'Reason...',
                }
            )
        }