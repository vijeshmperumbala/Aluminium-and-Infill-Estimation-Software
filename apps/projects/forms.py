from django import forms
from django.core.files.storage import default_storage
from amoeba.settings import MEDIA_URL
from apps.UoM.models import UoM
from apps.Categories.models import Category
from apps.brands.models import CategoryBrands


from django.forms import ClearableFileInput
from apps.panels_and_others.models import PanelMasterBase, PanelMasterBrands, PanelMasterSeries, PanelMasterSpecifications
from apps.pricing_master.models import Surface_finish_kit
from apps.product_master.models import Product, SecondaryProducts
from apps.product_parts.models import Parts, Profile_Kit
from apps.profiles.models import ProfileMasterType
from apps.projects.models import (
                    ApprovalNotes, ApprovalSpecFiles, CumulativeInvoiceProduct, Delivery_Note, DeliveryNoteCart, EPSBuildingsModel, ElevationModel, Eps_Outsourced_Data, Eps_Product_Details, 
                    Eps_Products, Eps_ShopFloors, 
                    Eps_infill_Details, Eps_infill_Temp, 
                    Eps_main, Fabrication_Attachments, FloorModel, 
                    Outsource_receive_recode, ProjectApprovalStatus, ProjectDeductionPercentage, 
                    ProjectDeliveryQuantity, ProjectInstalledQuantity, 
                    ProjectInvoices, ProjectInvoicingPercentage, 
                    ProjectInvoicingProducts, ProjectWCR, 
                    ProjectsModel, QAQC_parameters, SalesOrderInfill, 
                    SalesOrderItems, SalesOrderSpecification, SalesSecondarySepcPanels, 
                    Schedule_Product, ShopFloor_Doc, WCRProducts,
                    ProjectApprovalTypes,
)
from apps.shopfloors.models import Shopfloors
from apps.suppliers.models import Suppliers
from apps.surface_finish.models import SurfaceFinishColors
from apps.vehicles_and_drivers.models import Drivers, Vehicles



class CreateProject(forms.ModelForm):
    class Meta:
        model = ProjectsModel
        fields = [
                    'project_title', 
                    'project_id', 
                    'created_date', 
                    'due_date',
                ]
        
        widgets = {
            'project_title': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Project Title',
                    # 'required': True,
                }
            ),
            'project_id': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Project ID',
                    'required': True,
                }
            ),
            'created_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Created Date',
                    'type': 'date',
                    'required': True,
                    
                }
            ),
            'due_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Due date',
                    'type': 'date',
                    'required': True,
                    
                }
            ),
        }
        

class CreateInvoicePercentage(forms.ModelForm):
    # def __init__(self, project, *args, **kwargs):
        # super(CreateInvoicePercentage, self).__init__(*args, **kwargs)
        # self.fields['stage'].empty_label = "Stage"
        # self.fields['stage'].queryset = ProjectInvoicingPercentage.objects.filter(project=project) 
        # self.fields['stage'].widget.attrs.update({
        #         'class': 'form-control floating-control invoice_stage',
        #         'data-placeholder': 'Select an option'
        #     })
    # stage = forms.ModelChoiceField(queryset=ProjectInvoicingPercentage.objects.filter(), empty_label="Select a Stage")
    # stage.widget.attrs.update({
    #     'class': 'form-control floating-control',
    #     'data-placeholder': 'Select an option'
    # })
    STAGE = [
        (1, 'Delivery'),
        (2, 'Stage 1'),
        (3, 'Stage 2'),
        (4, 'Stage 3'),
    ]
    stage= forms.ChoiceField(choices=STAGE, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
    }))
    
    class Meta:
        model = ProjectInvoicingPercentage
        fields = ['stage', 'invoice_percentage']
        widgets = {
            'invoice_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Invoicing Percentage',
                }
            ),
        }
        
        
class CreateDeductionPercentage(forms.ModelForm):
    
    STAGE = [
        (1, 'Advance'),
        (2, 'Retention'),
    ]
    deduction_stage = forms.ChoiceField(choices=STAGE, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
    }))
    
    class Meta:
        model = ProjectDeductionPercentage
        fields = ['deduction_stage', 'deduction_percentage']
        widgets = {
            'deduction_percentage': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Deduction Percentage',
                }
            ),
        }
        

class CreateProjectInvoice(forms.ModelForm):
    
    TERMS_OF_PAYMENT = [
            (1, 'Immediate'),
            (2, '15 Days'),
            (3, '30 Days'),
            (4, '45 Days'),
            (5, '60 Days'),
        ]
    MODE_OF_PAYMENT = [
        ('', 'Select a Option'),
        (1, 'Credit'),
        (2, 'Cash'),
    ]
    
    INVOICE_STAGE = [
        (1, 'Work in progress'),
        (2, 'Final'),
    ]
    
    STATUS = [
        (1, 'Uncertified'),
        (2, 'Certified'),
    ]
    
    terms_of_payment = forms.ChoiceField(choices=TERMS_OF_PAYMENT, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
    }))
    mode_of_payment = forms.ChoiceField(choices=MODE_OF_PAYMENT, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
        'required': True,
        
    }))
    
    invoice_stage = forms.ChoiceField(choices=INVOICE_STAGE, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
    }))
    
    project_invoice_status = forms.ChoiceField(choices=STATUS, widget=forms.Select(attrs={
        'class': 'form-select form-select-solid',
    }))
    
    # comapny = forms.ModelChoiceField(queryset=Companies.objects.all(), empty_label="Select a Company")
    # comapny.widget.attrs.update({
    #     'class': 'form-control floating-control',
    #     'data-placeholder': 'Select an option'
    # })
    
    class Meta:
        model = ProjectInvoices
        fields = [
            'invoice_number',
            'invoice_due_date',
            'invoice_notes',
            'created_date',
            'bill_to',
            'invoice_value',
            'terms_of_payment',
            'mode_of_payment',
            'invoice_stage',
            'project_invoice_status',
            'company',
            'bill_to_address',
            'bill_to_name',
            'bill_to_email',
        ]
        widgets = {
            'company': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'hidden',
                }
            ),
            'bill_to_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Name'
                }
            ),
            'bill_to_email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Email'
                    
                }
            ),
            'bill_to_address': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'rows': 3,
                    'placeholder': 'Address'
                    
                }
            ),
            'invoice_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-flush fw-bold text-muted fs-3 w-125px',
                    'placeholder': 'IN-123456',
                    'required': True,
                }
            ),
            'invoice_value': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-flush fw-bold text-muted fs-3 w-125px',
                    'type': 'hidden'
                }
            ),
            'created_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-transparent fw-bold pe-5 flatpickr-input',
                    'readonly':'readonly',
                    'type': 'date'
                }
            ),
            'invoice_due_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-transparent fw-bold pe-5 flatpickr-input',
                    'type': 'date',
                    'placeholder': 'dd/mm/yyyy',
                }
            ),
            'invoice_notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Notes...',
                    'rows': '3'
                }
            ),
        }
        
        
class DeliveryQuantityForm(forms.ModelForm):
    class Meta:
        model = ProjectDeliveryQuantity
        fields = [
            'delivered_not_invoiced'
        ]
        
        widgets = {
            'delivered_not_invoiced': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid fw-bold text-muted fs-5',
                }
            ),
        }
        
        
class InstalledQuantityForm(forms.ModelForm):
    
    class Meta:
        model = ProjectInstalledQuantity
        fields = [
            'installed_qunatity'
        ]
        widgets = {
            'installed_qunatity': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid fw-bold text-muted fs-5',
                }
            ),
        }
        
        
def create_invoice_form(project):
    class Invoiced_ProductForm(forms.ModelForm):
        
        # def __init__(self, *args, **kwargs):
        #     super(Invoiced_ProductForm, self).__init__(*args, **kwargs)
        #     self.fields['invoicing_stage'].empty_label = "Stage"
        #     self.fields['invoicing_stage'].queryset = ProjectInvoicingPercentage.objects.filter(project=project) 
        #     self.fields['invoicing_stage'].widget.attrs.update({
        #             'class': 'form-control floating-control invoice_stage',
        #             'data-placeholder': 'Select an option'
        #         })
        
        class Meta: 
            model = ProjectInvoicingProducts
            fields = [
                # 'invoicing_stage',
                'quantity',
                # 'unit_price',
                'product',
                'total',
                'invoice_percentage',
            ]
            widgets = {
                'quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid fw-bold text-muted fs-5 invoice_product_quantity',
                    }
                ),
                'total': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid fw-bold text-muted fs-5',
                        'type': 'hidden'
                    }
                ),
                'invoice_percentage': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid fw-bold text-muted fs-5 invoice_percentage',
                    }
                ),
                'product': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid fw-bold text-muted fs-5',
                        'type': 'hidden'
                    }
                )
            }
    return Invoiced_ProductForm

def create_cumulative_invoice_form(project):
    class CumulativeInvoicedProductForm(forms.ModelForm):
        
        # def __init__(self, *args, **kwargs):
        #     super(Invoiced_ProductForm, self).__init__(*args, **kwargs)
        #     self.fields['invoicing_stage'].empty_label = "Stage"
        #     self.fields['invoicing_stage'].queryset = ProjectInvoicingPercentage.objects.filter(project=project) 
        #     self.fields['invoicing_stage'].widget.attrs.update({
        #             'class': 'form-control floating-control invoice_stage',
        #             'data-placeholder': 'Select an option'
        #         })
        
        class Meta: 
            model = CumulativeInvoiceProduct
            fields = [
                # 'invoicing_stage',
                'quantity',
                # 'unit_price',
                'product',
                'total',
                'invoice_percentage',
            ]
            widgets = {
                'quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid fw-bold text-muted fs-5 invoice_product_quantity',
                    }
                ),
                'total': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid fw-bold text-muted fs-5',
                        'type': 'hidden'
                    }
                ),
                'invoice_percentage': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid fw-bold text-muted fs-5 invoice_percentage',
                    }
                ),
                'product': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-solid fw-bold text-muted fs-5',
                        'type': 'hidden'
                    }
                )
            }
    return CumulativeInvoicedProductForm
  
  
  
class Create_Project_WCR(forms.ModelForm):
    class Meta:
        model = ProjectWCR
        fields = [
            'wcr_number',
            'wcr_notes',
            'created_date',
            ]
        
        widgets = {
            'wcr_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-flush fw-bold text-muted fs-3 w-125px',
                    'placeholder': '--------'
                }
            ),
            'wcr_notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Notes...',
                    'rows': '3'
                }
            ),
            'created_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-transparent fw-bold pe-5 flatpickr-input',
                    'readonly':'readonly',
                    'type': 'date'
                }
            ),
        }
        
        
# def create_wcr_form(project):
class WCR_Products(forms.ModelForm):
    
    class Meta:
        model = WCRProducts
        fields = [
            'wcr_product',
            'delivery_qunatity',
            'installed_qunatity',
        ]
        widgets = {
            'delivery_qunatity': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid fw-bold text-muted fs-5',
                }
            ),
            'installed_qunatity': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid fw-bold text-muted fs-5',
                }
            ),
        }
    # return WCR_Products
    
    



# 
# 
# EPS FORMS
# 
# 

# *|MARKER_CURSOR|*
class EPSProductForm(forms.ModelForm):
    
    class Meta:
        model = Eps_Products
        fields = [
         'width',
         'height',
         'quantity',
        #  'product_type',
         'eps_product_note',
        #  'delivery_date',
         'eps_product_attachment',
        #  'no_infill_data',
         'fabrication_drawings_not_req',
         'vision_panel',
         'spandrel_panel',
         'openable_panel',
         'is_vp',
         'is_sp',
         'is_op',
         'vp_description',
         'op_description',
         'sp_description',
        ]
        widgets = {
            'vp_description': forms.Textarea(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 floating-control',
                    'cols': 5,
                    'rows': 3,
                }
            ),
            'op_description': forms.Textarea(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 floating-control',
                    'cols': 5,
                    'rows': 3,
                }
            ),
            'sp_description': forms.Textarea(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 floating-control',
                    'cols': 5,
                    'rows': 3,
                }
            ),
            'vision_panel': forms.TextInput(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 w-75px floating-control',
                    # 'style': 'border: 1px solid #e4e4e4;'
                    'required': True,
                }
            ),
            'spandrel_panel': forms.TextInput(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 w-75px floating-control',
                    # 'style': 'border: 1px solid #e4e4e4;'
                    'required': True,
                }
            ),
            'openable_panel': forms.TextInput(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 w-75px floating-control',
                    # 'style': 'border: 1px solid #e4e4e4;'
                    'required': True,
                }
            ),
            'width': forms.TextInput(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 w-100px floating-control',
                    # 'style': 'border-radius: 0px;',
                }
            ),
            'height': forms.TextInput(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 w-100px floating-control',
                }
            ),
            'quantity': forms.TextInput(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2 w-100px floating-control',
                    'required': True,
                }
            ),
            'eps_product_note': forms.Textarea(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2  floating-control',
                    'cols': 30,
                    'rows': 2,
                    'required': True,
                    
                }
            ),
            # 'delivery_date': forms.DateInput(
            #     attrs={
            #         'class': 'form-control fw-bold text-muted fs-5 p-2 w-125px floating-control',
            #         'placeholder': 'Date',
            #         'type': 'date',
            #         'required': True,
            #     }
            # ),
            'eps_product_attachment': forms.FileInput(
                attrs={
                    'class': 'dropzone-select form-control fw-bold text-muted fs-5 p-2 floating-control',
                    'type': 'file'
                }
            ),
            # 'no_infill_data': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-20px',
            #     }
            # ),
            'fabrication_drawings_not_req': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_vp': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_sp': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_op': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
        }
        
        
class infillEPSform(forms.ModelForm):
    class Meta:
        model = Eps_Products
        fields = [
            'is_vp',
            'is_sp',
            'is_op',
            'vp_description',
            'op_description',
            'sp_description',
            'eps_product_note',
            'eps_product_attachment',
        ]
        
        widgets = {
            
            'is_vp': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_sp': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'is_op': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-20px',
                }
            ),
            'eps_product_attachment': forms.FileInput(
                attrs={
                    'class': 'dropzone-select form-control fw-bold text-muted fs-5 p-2 floating-control',
                    'type': 'file'
                }
            ),
            'eps_product_note': forms.Textarea(
                attrs={
                    'class': 'form-control fw-bold fs-5 p-2  floating-control',
                    'cols': 30,
                    'rows': 2,
                    'required': True,
                    
                }
            ),
        }
        
        
def EPSProductDetails(category):
    class EPSProductDetailsForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(EPSProductDetailsForm, self).__init__(*args, **kwargs)
            self.fields['product_part'].empty_label = "Select Parts"
            self.fields['product_part'].queryset = Parts.objects.filter(parts_category=category)
            self.fields['product_part'].required = False 
            self.fields['product_part'].widget.attrs.update({
                    'class': 'form-control floating-control form-select p-2 w-250px',
                    'data-placeholder': 'Select an option'
                })
            
        class Meta:
            model: Eps_Product_Details
            fields = [
                'product_part',
                'product_code',
                'product_quantity',
                'product_length',
                'product_width',
                'product_height',
                'product_area',
                'product_total_area',
                'product_description',
                'product_total_length',
            ]
            widgets = {
                
                'product_code': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 p-2 w-100px floating-control',
                        # 'placeholder': 'Code'
                    }
                ),
                
                'product_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 product_quantity p-2 w-100px floating-control',
                        # 'placeholder': 'Quantity'
                    }
                ),
                
                'product_length': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 p-2 w-100px floating-control product_length',
                        # 'placeholder': 'Length'
                        
                    }
                ),
                
                'product_total_length': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 p-2 w-100px floating-control product_total_length',
                        # 'placeholder': 'Length'
                        
                    }
                ),
                'product_width': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 product_width p-2 w-100px floating-control',
                        # 'placeholder': 'Width'
                        
                    }
                ),
                'product_height': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 product_height p-2 w-100px floating-control',
                        # 'placeholder': 'Height'
                        
                    }
                ),
                'product_area': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 product_area p-2 w-100px floating-control',
                        # 'placeholder': 'Area'
                        'readonly': True,
                    }
                ),
                'product_total_area': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 product_total_area p-2 w-100px floating-control',
                        # 'placeholder': 'Area'
                        
                    }
                ),
                'product_description': forms.TextInput(
                    attrs={
                        'class': 'form-control fw-bold text-muted fs-5 product_description p-2 w-200px floating-control',
                        # 'placeholder': 'Description'
                        
                    }
                ),
                
            }
    return EPSProductDetailsForm


def eps_infill_details(product):
    class EPS_Infill_Details(forms.ModelForm):
        
        def __init__(self, *args, **kwargs):
            super(EPS_Infill_Details, self).__init__(*args, **kwargs)
            self.fields['infill'].empty_label = "Select Panel"
            self.fields['infill'].queryset = SalesSecondarySepcPanels.objects.filter(specifications=product, panel_type=1)
            self.fields['infill'].required = False 
            self.fields['infill'].widget.attrs.update({
                    'class': 'form-control floating-control form-control-sm p-2 w-400px',
                    'data-placeholder': 'Select an option'
                })
        
        class Meta:
            model = Eps_infill_Details
            fields = [
                'infill',
                'infill_width',
                'infill_code',
                'infill_height',
                'infill_area',
                'infill_quantity',
                'is_outsourced'
            ]
            
            widgets = {
                'infill_width': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_width p-2 w-75px vision_width',
                        'placeholder': 'Width'
                    }
                ),
                'infill_height': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_height p-2 w-75px vision_height',
                        'placeholder': 'Height'
                    }
                ),
                'infill_code': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-50px',
                        'placeholder': 'Code'
                    }
                ),
                'infill_area': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_area p-2 w-50px vision_area',
                        'placeholder': 'Area'
                    }
                ),
                'infill_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-75px infill_quantity vision_qty',
                        'placeholder': 'Quantity',
                    }
                ),
                'is_outsourced': forms.CheckboxInput(
                    attrs={
                        'class': 'form-check-input h-20px w-20px',
                    }
                ),
            }
            
    return EPS_Infill_Details

def eps_spandrel_details(product):
    class EPS_Spandrel_Details(forms.ModelForm):
        
        def __init__(self, *args, **kwargs):
            super(EPS_Spandrel_Details, self).__init__(*args, **kwargs)
            
            self.fields['infill'].empty_label = "Select Panel"
            self.fields['infill'].queryset = SalesSecondarySepcPanels.objects.filter(specifications=product, panel_type=2)
            self.fields['infill'].required = False
            self.fields['infill'].widget.attrs.update({
                    'class': 'form-control floating-control form-control-sm p-2 w-400px',
                    'data-placeholder': 'Select an option'
                })
        
        class Meta:
            model = Eps_infill_Details
            fields = [
                'infill',
                'infill_width',
                'infill_code',
                'infill_height',
                'infill_area',
                'infill_quantity',
                'is_outsourced'
            ]
            
            widgets = {
                'infill_width': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_width p-2 w-75px spandrel_width',
                        'placeholder': 'Width'
                    }
                ),
                'infill_height': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_height p-2 w-75px spandrel_height',
                        'placeholder': 'Height'
                    }
                ),
                'infill_code': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-50px',
                        'placeholder': 'Code'
                    }
                ),
                'infill_area': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_area p-2 w-50px spandrel_area',
                        'placeholder': 'Area'
                    }
                ),
                'infill_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-75px infill_quantity spandrel_qty',
                        'placeholder': 'Quantity',
                    }
                ),
                'is_outsourced': forms.CheckboxInput(
                    attrs={
                        'class': 'form-check-input h-20px w-20px',
                    }
                ),
            }
            
    return EPS_Spandrel_Details

def eps_openable_details(product):
    class EPS_Openable_Details(forms.ModelForm):
        
        def __init__(self, *args, **kwargs):
            super(EPS_Openable_Details, self).__init__(*args, **kwargs)
            
            self.fields['infill'].empty_label = "Select Panel"
            self.fields['infill'].queryset = SalesSecondarySepcPanels.objects.filter(specifications=product, panel_type=3)
            self.fields['infill'].required = False
            self.fields['infill'].widget.attrs.update({
                    'class': 'form-control floating-control form-control-sm p-2 w-400px',
                    'data-placeholder': 'Select an option'
                })
        
        class Meta:
            model = Eps_infill_Details
            fields = [
                'infill',
                'infill_width',
                'infill_code',
                'infill_height',
                'infill_area',
                'infill_quantity',
                'is_outsourced'
            ]
            
            widgets = {
                'infill_width': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_width p-2 w-75px openable_width',
                        'placeholder': 'Width'
                    }
                ),
                'infill_height': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_height p-2 w-75px openable_height',
                        'placeholder': 'Height'
                    }
                ),
                'infill_code': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-50px',
                        'placeholder': 'Code'
                    }
                ),
                'infill_area': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_area p-2 w-50px openable_area',
                        'placeholder': 'Area'
                    }
                ),
                'infill_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-75px infill_quantity openable_qty',
                        'placeholder': 'Quantity',
                    }
                ),
                'is_outsourced': forms.CheckboxInput(
                    attrs={
                        'class': 'form-check-input h-20px w-20px',
                    }
                ),
            }
            
    return EPS_Openable_Details


def eps_infill_temp(product):
    class EPS_Infill_Temp(forms.ModelForm):
        
        def __init__(self, *args, **kwargs):
            super(EPS_Infill_Temp, self).__init__(*args, **kwargs)
            self.fields['infill'].empty_label = "Select Vision Panel"
            self.fields['infill'].queryset = SalesSecondarySepcPanels.objects.filter(specifications=product, panel_type=1)
            self.fields['infill'].required = False 
            self.fields['infill'].widget.attrs.update({
                    'class': 'form-control floating-control form-control-sm p-2 w-400px',
                    'data-placeholder': 'Select an option'
                })
        
        class Meta:
            model = Eps_infill_Temp
            fields = [
                'infill',
                'infill_width',
                'infill_code',
                'infill_height',
                'infill_area',
                'infill_quantity',
            ]
            
            widgets = {
                'infill_width': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 infill_width p-2 w-75px floating-control vision_width',
                        'placeholder': 'Width'
                    }
                ),
                'infill_height': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 infill_height p-2 w-75px floating-control vision_height',
                        'placeholder': 'Height'
                    }
                ),
                'infill_code': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 p-2 w-50px floating-control',
                        'placeholder': 'Code'
                    }
                ),
                'infill_area': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 infill_area p-2 w-50px floating-control vision_area',
                        'placeholder': 'Area'
                    }
                ),
                'infill_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 p-2 w-75px infill_quantity floating-control vision_qty',
                        'placeholder': 'Quantity',
                        'required': True,
                    }
                ),
                
            }
            
    return EPS_Infill_Temp

def eps_spandrel_details_temp(product):
    class EPS_Temp_Spandrel_Details(forms.ModelForm):
        
        def __init__(self, *args, **kwargs):
            super(EPS_Temp_Spandrel_Details, self).__init__(*args, **kwargs)
            
            self.fields['infill'].empty_label = "Select Spandrel Panel"
            self.fields['infill'].queryset = SalesSecondarySepcPanels.objects.filter(specifications=product, panel_type=2)
            self.fields['infill'].required = False
            self.fields['infill'].widget.attrs.update({
                    'class': 'form-control floating-control form-control-sm p-2 w-400px',
                    'data-placeholder': 'Select an option'
                })
        
        class Meta:
            model = Eps_infill_Temp
            fields = [
                'infill',
                'infill_width',
                'infill_code',
                'infill_height',
                'infill_area',
                'infill_quantity',
            ]
            
            widgets = {
                'infill_width': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_width p-2 w-75px spandrel_width',
                        'placeholder': 'Width'
                    }
                ),
                'infill_height': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_height p-2 w-75px spandrel_height',
                        'placeholder': 'Height'
                    }
                ),
                'infill_code': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-50px',
                        'placeholder': 'Code'
                    }
                ),
                'infill_area': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_area p-2 w-50px spandrel_area',
                        'placeholder': 'Area'
                    }
                ),
                'infill_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-75px infill_quantity spandrel_qty',
                        'placeholder': 'Quantity',
                        'required': True,
                    }
                ),
                
            }
            
    return EPS_Temp_Spandrel_Details

def eps_openable_details_temp(product):
    class EPS_Temp_Openable_Details(forms.ModelForm):
        
        def __init__(self, *args, **kwargs):
            super(EPS_Temp_Openable_Details, self).__init__(*args, **kwargs)
            
            self.fields['infill'].empty_label = "Select Openable Panel"
            self.fields['infill'].queryset = SalesSecondarySepcPanels.objects.filter(specifications=product, panel_type=3)
            self.fields['infill'].required = False
            self.fields['infill'].widget.attrs.update({
                    'class': 'form-control floating-control form-control-sm p-2 w-400px',
                    'data-placeholder': 'Select an option'
                })
        
        class Meta:
            model = Eps_infill_Temp
            fields = [
                'infill',
                'infill_width',
                'infill_code',
                'infill_height',
                'infill_area',
                'infill_quantity',
            ]
            
            widgets = {
                'infill_width': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_width p-2 w-75px openable_width',
                        'placeholder': 'Width'
                    }
                ),
                'infill_height': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_height p-2 w-75px openable_height',
                        'placeholder': 'Height'
                    }
                ),
                'infill_code': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-50px',
                        'placeholder': 'Code'
                    }
                ),
                'infill_area': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 infill_area p-2 w-50px openable_area',
                        'placeholder': 'Area'
                    }
                ),
                'infill_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm floating-control fw-bold text-muted fs-5 p-2 w-75px infill_quantity openable_qty',
                        'placeholder': 'Quantity',
                        'required': True,
                    }
                ),
                
            }
            
    return EPS_Temp_Openable_Details

class EPSSubmitForm(forms.ModelForm):
    
    PRIORITY = [
        
        (1, 'Critical'),
        (2, 'High'),
        (3, 'Normal'),
    ]
    eps_priority = forms.ChoiceField(choices=PRIORITY, initial=3, widget=forms.Select(attrs={
                                                    'class': 'form-select form-select-solid',
                                                    'data-placeholder': 'Priority',
                                                    'data-control': "select2",
                                                    'data-hide-search': 'true',
                                                }))
    
    class Meta:
        model = Eps_main
        fields = [
            'expec_delivery_date',
            # 'is_understand',
            'is_confirm',
            # 'is_agreed',
            'eps_priority',
            'eps_note',
        ]
        widgets = {
                'expec_delivery_date': forms.DateTimeInput(
                    attrs={
                        'class': 'form-control  form-control-solid fw-bold text-muted fs-5',
                        'type': 'date',
                        'required': True
                    },
                ),
                # 'is_understand': forms.CheckboxInput(
                #     attrs={
                #         'class': 'form-check-input h-20px w-20px',
                #         'required': True
                #     }
                # ),
                'is_confirm': forms.CheckboxInput(
                    attrs={
                        'class': 'form-check-input h-20px w-20px',
                        'required': True
                    }
                ),
                # 'is_agreed': forms.CheckboxInput(
                #     attrs={
                #         'class': 'form-check-input h-20px w-20px',
                #         'required': True
                #     }
                # ),
                'eps_note': forms.Textarea(
                    attrs={
                        'class': 'form-control  form-control-solid fw-bold text-muted fs-5',
                        'cols': 100,
                        'rows': 4,
                        # 'required': True,
                        'placeholder': 'EPS Note'
                        
                    }
                )
                
            }  
        

class Fabrication_AttachmentsForms(forms.ModelForm):
    class Meta:
        model = Fabrication_Attachments
        fields = ['fabrication_docs']
        widgets = {
            # 'fabrication_docs': MultiWidget(widgets={'multiple': True, 'required': True}),
            'fabrication_docs': ClearableFileInput(attrs={'multiple': True, 'required': True}),
        }


class OutSourceSubmitForm(forms.ModelForm):
    
    outsource_supplier = forms.ModelChoiceField(queryset=Suppliers.objects.all(), empty_label='Select an Option')
    outsource_supplier.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    })
    
    class Meta:
        model = Eps_Outsourced_Data
        fields = [
            # 'outsource_date',
            # 'batch_number',
            # 'outsource_number',
            'outsource_supplier',
            # 'products',
            'expected_dalivery_date',
        ]
        
        widgets = {
            # 'outsource_date': forms.TextInput(
            #     attrs={
            #         'class': 'form-control form-control-solid',
            #         'type': 'date',
            #         'placeholder': 'Outsource Date',        
            #     }
            # ),
            'expected_dalivery_date': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid ',
                    'type': 'date',
                    'placeholder': 'Expected Delivery',        
                }
            ),
            # 'batch_number': forms.TextInput(
            #     attrs={
            #         'class': 'form-control form-control-solid',
            #         'placeholder': 'Batch Number',        
            #     }
            # ),
            # 'outsource_number': forms.TextInput(
            #     attrs={
            #         'class': 'form-control form-control-solid',
            #         'placeholder': 'Outsource Number',        
            #     }
            # ),
            
        }
        

class ReceiveOutsourceProduct(forms.ModelForm):
    class Meta:
        model = Outsource_receive_recode
        fields = [
            'receive_date',
            # 'receive_quantity',
            'OS_delivery_number',
            ]
        widgets = {
            'receive_date': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid ',
                    'type': 'date',
                    'placeholder': 'Received Date',        
                }
            ),
            # 'receive_quantity': forms.TextInput(
            #     attrs={
            #         'class': 'form-control form-control-solid',
            #         'placeholder': 'Received Quantity',        
            #     }
            # ),
            'OS_delivery_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'placeholder': 'Delivery Number',        
                }
            ),
            
        }


class ScheduleProductForm(forms.ModelForm):
    SHOPFLOOR_STATUS = [
        (1, "Received"),
        (2, "Scheduled"),
        (3, "On-Hold"),
        (4, "Completed"),
    ]
    shopfloor_status = forms.ChoiceField(
                    choices=SHOPFLOOR_STATUS, 
                    widget=forms.Select(
                                attrs={
                                    'class': 'form-select form-select-solid',
                                    'data-placeholder': 'Status',
                                }))
    class Meta:
        model = Schedule_Product
        fields = [
            'expected_completion',
            'start_date',
            'shopfloor_status',
            'notes',
        ]
        widgets = {
            'start_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'date',
                    'required': True,
                }
            ),
            'expected_completion': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'date',
                    'required': True,
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'rows': 3,
                }
            ),
        }


class DeliveryNoteCartCheckoutForm(forms.ModelForm):
    
    driver = forms.ModelChoiceField(queryset=Drivers.objects.all(), empty_label='Select a Driver')
    driver.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    })
    vehicle = forms.ModelChoiceField(queryset=Vehicles.objects.all(), empty_label='Select a Vehicle')
    vehicle.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-placeholder': 'Select an option'
    })
    
    class Meta:
        model = DeliveryNoteCart
        fields = [
            'driver',
            'vehicle',
        ]
        
    
class DeliveryNoteForm(forms.ModelForm):
    
    # driver = forms.ModelChoiceField(queryset=Drivers.objects.all(), empty_label='Select a Driver')
    # driver.widget.attrs.update({
    #     'class': 'form-select mb-2',
    #     'data-placeholder': 'Select an option'
    # })
    # vehicle = forms.ModelChoiceField(queryset=Vehicles.objects.all(), empty_label='Select a Vehicle')
    # vehicle.widget.attrs.update({
    #     'class': 'form-select mb-2',
    #     'data-placeholder': 'Select an option'
    # })
    
    
    class Meta:
        model = Delivery_Note
        fields = [
            'delivery_date',
            # 'driver',
            # 'vehicle',
            'delivery_notes',
        ]
        widgets = {
            'delivery_date': forms.DateInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'date',
                }
            ),
            'delivery_notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'rows': 4,
                    
                }
            ),

        }
   
        
class FabricationMultiAttachment(forms.ModelForm):
    
    class Meta:
        model = Fabrication_Attachments
        fields = [
            'fabrication_docs',
        ]
        widgets = {
            # 'fabrication_docs': MultiWidget(widgets={'multiple': True, 'class': 'form-control form-control-solid', 'type': 'file', 'onchange': 'displaySelectedFiles()'})
            'fabrication_docs': forms.FileInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'file',
                    'multiple': True,
                    'onchange': 'displaySelectedFiles()',
                }
            ),
        }
  
        
class Eps_ShopFloorsSet(forms.ModelForm):
    
    shopfloor = forms.ModelChoiceField(queryset=Shopfloors.objects.all(), required=False, empty_label='Select a Shopfloor')
    shopfloor.widget.attrs.update({
        'class': 'form-select mb-2',
        'data-placeholder': 'Select a Shopfloor'
    })
    
    class Meta:
        model = Eps_ShopFloors
        fields = [
            'shopfloor',
            'required_delivery_date',
            'shop_floor_notes',
        ]
        widgets = {
            'required_delivery_date': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'date',
                }
            ),
            'shop_floor_notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid',
                    'rows': 4, 
                    'placeholder': 'Notes...'
                }
            ),
            
        }
        
        
class ShopFloorAttachment(forms.ModelForm):
    
    class Meta:
        model = ShopFloor_Doc
        fields = [
            'shopfloor_doc',
        ]
        widgets = {
            'shopfloor_doc': forms.FileInput(
                attrs={
                    'class': 'form-control form-control-solid',
                    'type': 'file',
                    'multiple': True,
                    'onchange': 'displaySelectedFiles()',
                }
            ),
        }
        
        
        
class CreateSalesItem(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id', None)
        super(CreateSalesItem, self).__init__(*args, **kwargs)
        
        myChoices = [(c.categories.id, c.categories.category) for c in SalesOrderSpecification.objects.filter(project=project_id).order_by('categories')]
        myChoices = [('', 'Select a Category')] + myChoices
        
        self.fields['category'].choices = set(myChoices)
        self.fields['category'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an option'
            })
        self.fields['category'].empty_label = 'Select a Category'
        
        # try:
        #     # myChoices2 = [(c.panel_specification.id, c.panel_specification) for c in EnquirySpecifications.objects.filter(estimation__enquiry=enquiry_id)]
        #     myChoices2 = [(c.panel_product.id, c.panel_product) for c in SalesOrderSpecification.objects.filter(project=project_id)] 
        #     myChoices2.insert(0, ('', 'Select a Product'))
        #     myChoices2.insert(-1, ('#', 'N/A'))
            
        #     self.fields['panel_product'].choices = set(myChoices2)
        #     self.fields['panel_product'].widget.attrs.update({
        #             'class': 'form-control floating-control',
        #             'data-placeholder': 'Select an option'
        #         })
        # except Exception as e:
        #     self.fields['panel_product'].widget.attrs.update({
        #             'class': 'form-control floating-control',
        #             'data-placeholder': 'Select an option'
        #         })
        try:
            myChoices2 = [(c.aluminium_products.id, c.aluminium_products) for c in SalesOrderSpecification.objects.filter(project=project_id)]
            myChoices2.insert(0, ('', 'Select a Product'))
            self.fields['product'].choices = set(myChoices2)
            self.fields['product'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        except Exception:
            self.fields['product'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
        
        
        self.fields['specification_Identifier'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                                         queryset=SalesOrderSpecification.objects.filter(project=project_id).order_by('id'), 
                                                                         empty_label="Select a Identifier", required=True)
        self.fields['building'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                                         queryset=EPSBuildingsModel.objects.filter(project=project_id).order_by('id'), 
                                                                         empty_label="Select a Building", required=False)

        self.fields['elevation'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                                         queryset=ElevationModel.objects.filter(building__project=project_id).order_by('id'), 
                                                                         empty_label="Select a Elevation", required=False)
        
        self.fields['floor'] = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control floating-control'}), 
                                                                         queryset=FloorModel.objects.filter(elevation__building__project=project_id).order_by('id'), 
                                                                         empty_label="Select a Floor", required=False)
        
    uom = forms.ModelChoiceField(queryset=UoM.objects.all(), empty_label="Select a Unit")
    uom.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })
    surface_finish = forms.ModelChoiceField(queryset=Surface_finish_kit.objects.all(), required=False, empty_label="Select a Surface Finish")
    surface_finish.widget.attrs.update({
                        'class': 'form-control floating-control',
                        'data-placeholder': 'Select an option'
                    })
    category = forms.ModelChoiceField(
            queryset=Category.objects.all().order_by('id'),
            empty_label="Select a Category"
        )
    category.widget.attrs.update({
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
                        
                    })
    series = forms.ModelChoiceField(queryset=Profile_Kit.objects.all(), required=False,
                                    empty_label="Select a Series")
    series.widget.attrs.update({
        'class': 'form-control floating-control',
        'data-placeholder': 'Select an option',
        
    })
    
    EPS_UOM = [
        (1, "No's"),
        (2, "Lumpsum"),
        (3, "Linear Meter"),
    ]
    
    eps_uom = forms.ChoiceField(choices=EPS_UOM, initial=3, widget=forms.Select(attrs={
                                                    'class': 'form-control floating-control',
                                                    'data-placeholder': 'EPS UoM',
                                                    # 'data-control': "select2",
                                                    # 'data-hide-search': 'true',
                                                }))
    
    
    # PANEL_TYPE = [
    #     (1, "Vision Panel"),
    #     (2, "Spandrel Panel"),
    #     (3, "Openable Panel"),
    # ]
    
    # panel_type = forms.ChoiceField(choices=PANEL_TYPE, initial=1, widget=forms.Select(attrs={
    #                                                 'class': 'form-control floating-control',
    #                                                 'data-placeholder': 'Select Panel Type',
    #                                             }))
    


    class Meta:
        model = SalesOrderItems        
        fields = [
            'category',
            'specification_Identifier',
            'product',
            # 'panel_product',
            'brand',
            'series',
            # 'panel_brand',
            # 'panel_series',
            'surface_finish',
            'product_code',
            'product_description',
            'uom',
            'width',
            'height',
            'quantity',
            'area', 
            'unit_price',   
            'building',
            'elevation',
            'floor',
            'eps_uom',
            # 'panel_type',
            # 'is_secondary_panels',
              
        ]
        
        widgets = {
            
            'width': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    'style': 'border-radius:0px;  ',
                    # 'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$',
                    'placeholder': 'Width/Lm',
                    
                }
            ),
            'height': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    'style': 'border-radius:0px;',
                    # 'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+\s*$',
                    'placeholder': 'Height',
                }
            ),
            'area': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    'style': 'border-radius:0px;',
                    'placeholder': 'Area',
                }
            ),
            'quantity': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    'style': 'border-radius:0px; ',
                    'placeholder': 'Quantity',
                }
            ),
            'unit_price': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    'style': 'border-radius:0px; ',
                    'placeholder': 'Unit Price',
                }
            ),
            'product_code': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    'style': 'border-radius:0px; ',
                    'placeholder': 'Product Type',
                    
                }
            ),
            'product_description': forms.Textarea(
                attrs={
                    'class': 'form-control fs-5 pt-5',
                    'style': 'border-radius:0px; ',
                    # 'placeholder': 'Product Description',
                    'rows': 4,
                    'cols': 5,
                }
            ),
            # 'is_secondary_panels': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-30px',
            #     }
            # )
            
            
        }
        

class UpdatsalesSpecificationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        surface_finish_kit_id = kwargs.pop('surface_finish_kit_id')
        super(UpdatsalesSpecificationForm, self).__init__(*args, **kwargs)
        self.fields['surface_finish'].empty_label = "Select Surface Finish"
        self.fields['surface_finish'].queryset = Surface_finish_kit.objects.filter(master=surface_finish_kit_id) 
        self.fields['surface_finish'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an option'
            })
        
        # surface_finish = forms.ModelChoiceField(queryset=Surface_finish_kit.objects.filter(master=), required=False, empty_label="Select a Surface Finish")
        # # surface_finish = forms.ModelChoiceField(queryset=Surface_finish.objects.all(), required=False, empty_label="Select a Surface Finish")
        # surface_finish.widget.attrs.update({
        #                     'class': 'form-control floating-control',
        #                     'data-placeholder': 'Select an option'
        #                 })
        
    categories = forms.ModelChoiceField(queryset=Category.objects.all().order_by('id'), required=False, empty_label="Select a Category")
    categories.widget.attrs.update({
                            'class': 'form-control floating-control',
                            'data-placeholder': 'Select an option',
                            # 'disabled': True,
                        })
    
    
    aluminium_products = forms.ModelChoiceField(queryset=Product.objects.filter(product_type=1).order_by('product_name'), required=False, empty_label="select a Product")
    aluminium_products.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option',
        # 'disabled': True,
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
        'data-placeholder': 'Select an option',
        # 'disabled': True,
    })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all().order_by('panel_brands__brands'), required=False,
                                         empty_label="select a brand")
    panel_brand.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option'
    })
    panel_product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('product_name'), required=False,
                                         empty_label="select a Panel Product")
    panel_product.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select a Panel Product',
        # 'disabled': True,
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all().order_by('series'), required=False,
                                          empty_label="select a series")
    panel_series.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option',
        'data-control':'select2'
    })

    panel_specification = forms.ModelChoiceField(queryset=PanelMasterSpecifications.objects.all().order_by('specifications'), required=False,
                                                 empty_label="select a specifictaion")
    panel_specification.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option',
        'data-control':'select2'
    })
    
    
    surface_finish_color = forms.ModelChoiceField(queryset=SurfaceFinishColors.objects.all(), required=False,
                                                 empty_label="select a option")
    surface_finish_color.widget.attrs.update({
        'class': 'form-select form-select-solid',
        'data-placeholder': 'Select an option',
        'data-control':'select2'
        
    })
    
    # PANEL_TYPE = [
    #     (0, "N/A"),
    #     (1, "Vision Panel"),
    #     (2, "Spandrel Panel"),
    #     (3, "Openable Panel"),
    # ]
    # panel_type = forms.ChoiceField(
    #             choices=PANEL_TYPE, 
    #             widget=forms.Select(
    #                         attrs={
    #                             'class': 'form-control floating-control',
    #                             'data-placeholder': 'Status',
    #                         }))
    
    class Meta():
        model = SalesOrderSpecification        
        fields = [
            'reference_specification',
            'identifier',
            'categories',
            'aluminium_products',
            'aluminium_system',
            'aluminium_specification',
            'aluminium_series',
            'panel_category',
            'panel_brand',
            'panel_series',
            'panel_specification',
            'panel_product',
            'surface_finish',
            'surface_finish_color',
            # 'panel_type',
            # 'is_secondary_panels',
            'have_vision_panels',
            'have_spandrel_panels',
            'have_openable_panels',
            
            'vision_panels',
            'spandrel_panels',
            'openable_panels',
              
        ]
        
        widgets = {
            
            'vision_panels': forms.TextInput(
                attrs={
                    'class': 'form-control w-75px',
                    'style': 'min-height: 40px; padding-left: 5px;',
                }
            ),
            'spandrel_panels': forms.TextInput(
                attrs={
                    'class': 'form-control w-75px',
                    'style': 'min-height: 40px; padding-left: 5px;',
                }
            ),
            'openable_panels': forms.TextInput(
                attrs={
                    'class': 'form-control w-75px',
                    'style': 'min-height: 40px; padding-left: 5px;',
                }
            ),
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
                    # 'placeholder': 'Description',
                    'style': 'min-height: 40px; padding-left: 5px;',
                    'cols': '4',
                    'rows': '3',
                }
            ),
            # 'is_secondary_panels': forms.CheckboxInput(
            #     attrs={
            #         'class': 'form-check-input h-20px w-30px',
            #     }
            # ),
            'have_vision_panels': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                }
            ),
            'have_spandrel_panels': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                }
            ),
            'have_openable_panels': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input h-20px w-30px',
                }
            )
        }
        
        
        
class AddSecondaryProductsForm(forms.ModelForm):
    
   
    def __init__(self, *args, **kwargs):
        project_id = kwargs.pop('project_id')
        super(AddSecondaryProductsForm, self).__init__(*args, **kwargs)
        # self.fields['product'].queryset = SecondaryProducts.objects.filter(product_category=category_id)
        # self.fields['product'].queryset = Product.objects.filter(product_type=2)
        # self.fields['product'].widget.attrs.update({
        #         'class': 'form-control floating-control',
        #         'data-placeholder': 'Select an Secondary Product',
        #         'required': True,
        #     })
        # self.fields['product'].empty_label = 'Select a Secondary Product'
        
        self.fields['product'].queryset = Product.objects.filter(product_type=2)
        self.fields['product'].widget.attrs.update({
                'class': 'form-control floating-control',
                'data-placeholder': 'Select an Secondary Product',
                'required': True,
            })
        self.fields['product'].empty_label = 'Select a Secondary Product'
        
    EPS_UOM = [
        (1, "No's"),
        (2, "Lumpsum"),
        (3, "Linear Meter"),
    ]
    
    eps_uom = forms.ChoiceField(choices=EPS_UOM, initial=3, widget=forms.Select(attrs={
                                                    'class': 'form-control floating-control',
                                                    'data-placeholder': 'EPS UoM',
                                                    # 'data-control': "select2",
                                                    # 'data-hide-search': 'true',
                                                }))
    
        
    class Meta:
        model= SalesOrderItems
        fields=[
                    "product",
                    # "width",
                    # "height",
                    # "area",
                    "quantity",
                    # "total_area",
                    "product_code",
                    "product_description",
                    "eps_uom",
                ]
        widgets = {
            
            # 'width': forms.TextInput(
            #     attrs={
            #         'class': 'form-control fs-5',
            #         'style': 'border-radius:0px;  ',
            #         'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$',
            #         'placeholder': 'Width/Lm',
                    
            #     }
            # ),
            # 'height': forms.TextInput(
            #     attrs={
            #         'class': 'form-control fs-5',
            #         'style': 'border-radius:0px;  ',
            #         'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$',
            #         'placeholder': 'Height',
                    
            #     }
            # ),
            # 'area': forms.TextInput(
            #     attrs={
            #         'class': 'form-control fs-5',
            #         'style': 'border-radius:0px;  ',
            #         'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$',
            #         'placeholder': 'Area',
                    
            #     }
            # ),
            # 'total_area': forms.TextInput(
            #     attrs={
            #         'class': 'form-control fs-5',
            #         'style': 'border-radius:0px;  ',
            #         'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$',
            #         'placeholder': 'Total Area',
                    
            #     }
            # ),
            'product_description': forms.Textarea(
                attrs={
                    'class': 'form-control fs-5 pt-5',
                    'style': 'border-radius:0px; ',
                    'placeholder': 'Product Description',
                    'rows': 4,
                    'cols': 5,
                }
            ),
            'quantity': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    'style': 'border-radius:0px;  ',
                    'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$',
                    'placeholder': 'Quantity',
                    'required': True,
                }
            ),
            'product_code': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    'style': 'border-radius:0px;  ',
                    # 'pattern': '^(?!0\.00$|0$)\d{1,8}\.\d{2}|^(?!0$)\d+$',
                    'placeholder': 'Product Code',
                    
                }
            ),
        }
        


class ProjectApprovalTypesForm(forms.ModelForm):
    
    class Meta:
        model = ProjectApprovalTypes
        fields = [
            'approval_type',
        ]
        widgets = {
            'approval_type': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                }
            ),
        }


class ProjectApprovalStatusForm(forms.ModelForm):
    
    class Meta:
        model = ProjectApprovalStatus
        fields = [
            'approval_status',
            'color',
        ]
        widgets = {
            'approval_status': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-solid',
                }
            ),
            'color': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-color w-50px h-50px p-1',
                    'type': 'color',
                }
            ),
            
        }
        
    
class ApprovalNotesForm(forms.ModelForm):
    class Meta:
        model = ApprovalNotes
        fields = [
            'notes',
            
        ]
        widgets = {
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-solid p-2',
                    'cols': 6,
                    'rows': 3,
                }
            ),
            
        }


class ApprovalSpecFile(forms.ModelForm):
    
    class Meta:
        model = ApprovalSpecFiles
        fields = [
            'approval_file',
        ]
        widgets = {
            'approval_file': forms.FileInput(
                attrs={
                    'class': 'form-control form-control-solid p-2',
                    'multiple': True,
                }
            ),
            
        }


def sec_infill_form(project_id):
    class SecInfillsForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            # project_id = kwargs.pop('project_id', None)
            super(SecInfillsForm, self).__init__(*args, **kwargs)
            myChoices = [(c.panel_specification.id, c.panel_specification) for c in SalesOrderSpecification.objects.filter(project=project_id).distinct('panel_specification')]
            myChoices = myChoices + [('#', 'N/A')]
            
            self.fields['infill_specification'].choices = set(myChoices)
            self.fields['infill_specification'].widget.attrs.update({
                    'class': 'form-control floating-control',
                    'data-placeholder': 'Select an option'
                })
            self.fields['infill_specification'].empty_label = 'Select a Panel'
            
        PANEL_TYPE = [
            (1, "Vision Panel"),
            (2, "Spandrel Panel"),
            (3, "Openable Panel"),
        ]
        panel_type = forms.ChoiceField(
                    choices=PANEL_TYPE, 
                    widget=forms.Select(
                                attrs={
                                    'class': 'form-control floating-control',
                                    'data-placeholder': 'Status',
                                }))
            
        class Meta:
            model = SalesOrderInfill
            fields = [
                'infill_specification',
                'infill_area',
                'infill_width',
                'infill_height',
                'infill_quantity',
                'panel_type',
            ]
            widgets = {
                
                'infill_width': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 sec_infill_width p-2 w-100px floating-control',
                        'placeholder': 'Width'
                    }
                ),
                'infill_height': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 sec_infill_height p-2 w-100px floating-control',
                        'placeholder': 'Height'
                    }
                ),
                
                'infill_area': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 sec_infill_area p-2 w-100px floating-control',
                        'placeholder': 'Area'
                    }
                ),
                'infill_quantity': forms.TextInput(
                    attrs={
                        'class': 'form-control form-control-sm fw-bold text-muted fs-5 p-2 w-100px sec_infill_quantity floating-control',
                        'placeholder': 'Quantity',
                        'required': True,
                    }
                ),
                
            }

    return SecInfillsForm




# def sec_spec_infill_form(project_id):
class SecSpecVisionPanelsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # project_id = kwargs.pop('project_id', None)
        super(SecSpecVisionPanelsForm, self).__init__(*args, **kwargs)
        myChoices = [('', 'Select Panel Specification')] + [(c.id, c.specifications) for c in PanelMasterSpecifications.objects.all().order_by('specifications')]
        
        self.fields['panel_specification'].choices = set(myChoices)
        self.fields['panel_specification'].widget.attrs.update({
                'class': 'form-control floating-control sec_panel_specification',
                'data-placeholder': 'Select an Panel',
                'data-control':'select2',
            })
        self.fields['panel_specification'].empty_label = 'Select a Panel'
        
        panel_category = forms.ChoiceField(
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-sm sec_panel_category',
                'data-placeholder': 'Select a Category',
                'data-control': 'select2',
            })
        )
        
        myChoices2 = [('', 'Select Panel Category')] + [(c.panel_category.id, c.panel_category) for c in PanelMasterBase.objects.all().order_by('panel_category__category')]
        self.fields['panel_category'].choices = set(myChoices2)
        self.fields['panel_category'].empty_label = 'Select Panel Category'
        self.fields['panel_category'].widget.attrs.update({
            'class': 'form-select form-select-sm sec_panel_category',
            'data-placeholder': 'Select an option',
        })
    
    # panel_category = forms.ModelChoiceField(queryset=PanelMasterBase.objects.all().order_by('panel_category__category'), required=False,
    #                                      empty_label="Select a Category")
        # panel_category.widget.attrs.update({
        #     'class': 'form-select form-select-sm sec_panel_category',
        #     'data-placeholder': 'Select an option',
            
        # })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all().order_by('panel_brands__brands'), required=False,
                                         empty_label="Select a brand")
    panel_brand.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_brand',
        'data-placeholder': 'Select an option'
    })
    panel_product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('product_name'), required=False,
                                         empty_label="Select a Panel Product")
    panel_product.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_product ',
        'data-placeholder': 'Select a Panel Product',
        
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all().order_by('series'), required=False,
                                          empty_label="Select a series")
    panel_series.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_series',
        'data-placeholder': 'Select an option',
        'data-control':'select2'
    })
   
    class Meta:
        model = SalesSecondarySepcPanels
        fields = [
            'panel_specification',
            # 'panel_type',
            'panel_category',
            'panel_brand',
            'panel_series',
            'panel_product',
        ]
        

class SecSpecSpandrelPanelsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # project_id = kwargs.pop('project_id', None)
        super(SecSpecSpandrelPanelsForm, self).__init__(*args, **kwargs)
        myChoices = [('', 'Select Panel Specification')] + [(c.id, c.specifications) for c in PanelMasterSpecifications.objects.all().order_by('specifications')]
        
        self.fields['panel_specification'].choices = set(myChoices)
        self.fields['panel_specification'].widget.attrs.update({
                'class': 'form-control floating-control sec_panel_specification',
                # 'data-placeholder': 'Select an Panel',
                'data-control':'select2',
            })
        self.fields['panel_specification'].empty_label = 'Select a Panel'
        
        panel_category = forms.ChoiceField(
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-sm sec_panel_category',
                'data-placeholder': 'Select a Category',
                'data-control': 'select2',
            })
        )
        
        myChoices2 = [('', 'Select Panel Category')] + [(c.panel_category.id, c.panel_category) for c in PanelMasterBase.objects.all().order_by('panel_category__category')]
        self.fields['panel_category'].choices = set(myChoices2)
        self.fields['panel_category'].empty_label = 'Select a Category'
        self.fields['panel_category'].widget.attrs.update({
            'class': 'form-select form-select-sm sec_panel_category',
            'data-placeholder': 'Select an option',
        })
        
    
    # panel_category = forms.ModelChoiceField(queryset=PanelMasterBase.objects.all().order_by('panel_category__category'), required=False,
    #                                      empty_label="select a category")
    # panel_category.widget.attrs.update({
    #     'class': 'form-select sec_panel_category form-select-sm',
    #     'data-placeholder': 'Select an option',
    # })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all().order_by('panel_brands__brands'), required=False,
                                         empty_label="select a brand")
    panel_brand.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_brand',
        'data-placeholder': 'Select an option'
    })
    panel_product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('product_name'), required=False,
                                         empty_label="select a Panel Product")
    panel_product.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_product',
        'data-placeholder': 'Select a Panel Product',
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all().order_by('series'), required=False,
                                          empty_label="select a series")
    panel_series.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_series',
        'data-placeholder': 'Select an option',
        'data-control':'select2'
    })
   
    class Meta:
        model = SalesSecondarySepcPanels
        fields = [
            'panel_specification',
            # 'panel_type',
            'panel_category',
            'panel_brand',
            'panel_series',
            'panel_product',
        ]
  
  
class SecOpenablePanelsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # project_id = kwargs.pop('project_id', None)
        super(SecOpenablePanelsForm, self).__init__(*args, **kwargs)
        myChoices = [('', 'Select Panel Specification')] + [(c.id, c.specifications) for c in PanelMasterSpecifications.objects.all().order_by('specifications')]
        
        self.fields['panel_specification'].choices = set(myChoices)
        self.fields['panel_specification'].widget.attrs.update({
                'class': 'form-control floating-control sec_panel_specification',
                'data-placeholder': 'Select an Panel',
                'data-control':'select2',
            })
        self.fields['panel_specification'].empty_label = 'Select a Panel'
    
    
        panel_category = forms.ChoiceField(
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-select form-select-sm sec_panel_category',
                'data-placeholder': 'Select a Category',
                'data-control': 'select2',
            })
        )
        
        myChoices2 = [('', 'Select Panel Category')] + [(c.panel_category.id, c.panel_category) for c in PanelMasterBase.objects.all().order_by('panel_category__category')]
        self.fields['panel_category'].choices = set(myChoices2)
        self.fields['panel_category'].empty_label = 'Select a Category'
        self.fields['panel_category'].widget.attrs.update({
            'class': 'form-select form-select-sm sec_panel_category',
            'data-placeholder': 'Select an option',
        })
        
    # panel_category = forms.ModelChoiceField(queryset=PanelMasterBase.objects.all().order_by('panel_category__category'), required=False,
    #                                      empty_label="select a category")
    # panel_category.widget.attrs.update({
    #     'class': 'form-select form-select-sm sec_panel_category',
    #     'data-placeholder': 'Select an option',
    # })

    panel_brand = forms.ModelChoiceField(queryset=PanelMasterBrands.objects.all().order_by('panel_brands__brands'), required=False,
                                         empty_label="select a brand")
    panel_brand.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_brand',
        'data-placeholder': 'Select an option'
    })
    panel_product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('product_name'), required=False,
                                         empty_label="select a Panel Product")
    panel_product.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_product',
        'data-placeholder': 'Select a Panel Product',
    })

    panel_series = forms.ModelChoiceField(queryset=PanelMasterSeries.objects.all().order_by('series'), required=False,
                                          empty_label="select a series")
    panel_series.widget.attrs.update({
        'class': 'form-select form-select-sm sec_panel_series',
        'data-placeholder': 'Select an option',
        'data-control':'select2'
    })
   
    class Meta:
        model = SalesSecondarySepcPanels
        fields = [
            'panel_specification',
            # 'panel_type',
            'panel_category',
            'panel_brand',
            'panel_series',
            'panel_product',
        ]
  
  
class QAQCParametersFrom(forms.ModelForm):
    
    class Meta:
        model = QAQC_parameters
        fields = [
            'parameter_name',
        ]  
        
        widgets = {
            
            'parameter_name': forms.TextInput(
                attrs={
                    'class': 'form-control fs-5',
                    
                }
            ),
        }
  

  
  
  
  
  
  
  
  
  
  
  
        