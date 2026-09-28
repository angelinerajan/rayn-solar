from django.db import models

# Create your models here.
class user(models.Model):
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10)
    password = models.CharField(max_length=150)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default="India")
    photo = models.ImageField(upload_to='donor_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Employee(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10)
    password = models.CharField(max_length=150)  # store hashed password ideally
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    address = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=False)
    def __str__(self):
        return self.full_name
    
    

from django.db import models


class SolarEstimation(models.Model):
    LOCATION_CHOICES = [
        ("urban", "Urban"),
        ("semi_urban", "Semi Urban"),
        ("rural", "Rural"),
    ]

    BUILDING_TYPE_CHOICES = [
        ("house", "House"),
        ("apartment", "Apartment"),
        ("factory", "Factory"),
        ("warehouse", "Warehouse"),
        ("hospital", "Hospital"),
        ("school", "School"),
        ("skyscraper", "Skyscraper"),
        ("office", "Office Building"),
        ("cultural", "Cultural Centre"),
        ("industrial", "Industrial Building"),
        ("carport", "Residential Carports"),
        ("agricultural", "Agricultural Building"),
    ]

    ROOF_TYPE_CHOICES = [
        ("flat", "Flat"),
        ("sloped", "Sloped"),
    ]

    POWER_CUT_CHOICES = [
        ("none", "None"),
        ("occasional", "Occasional"),
        ("frequent", "Frequent"),
    ]

    YES_NO_CHOICES = [
        ("yes", "Yes"),
        ("no", "No"),
    ]
    
    SUBSIDY_TYPE_CHOICES = [
        ("no", "No Subsidy"),
        ("percentage", "Custom Percentage"),
        ("fixed_amount", "Custom Fixed Amount"),
    ]

    user = models.ForeignKey(
        'user', # Ensure this matches your user model name
        on_delete=models.CASCADE,
        related_name="solar_estimations"
    )
    
    location = models.CharField(max_length=100)
    monthly_units = models.PositiveIntegerField(help_text="Monthly electricity consumption (units)")

    building_type = models.CharField(max_length=30, choices=BUILDING_TYPE_CHOICES)
    roof_type = models.CharField(max_length=10, choices=ROOF_TYPE_CHOICES)
    roof_area = models.PositiveIntegerField(help_text="Roof area in sq.ft")

    power_cut = models.CharField(max_length=15, choices=POWER_CUT_CHOICES)
    backup_required = models.CharField(max_length=3, choices=YES_NO_CHOICES)
    
    apply_subsidy = models.CharField(max_length=15, choices=SUBSIDY_TYPE_CHOICES, default="no")
    subsidy_percentage = models.FloatField(default=0.0)
    subsidy_fixed_amount = models.FloatField(default=0.0)

    lightning_protection = models.CharField(max_length=3, choices=YES_NO_CHOICES, default="no")
    surge_protection = models.CharField(max_length=3, choices=YES_NO_CHOICES, default="no")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location} - {self.monthly_units} units"


class SolarTechnicalData(models.Model):
    estimation = models.OneToOneField(
        SolarEstimation,
        on_delete=models.CASCADE,
        related_name="technical"
    )

    daily_units = models.FloatField()
    system_size = models.FloatField()      # kW
    roof_required = models.IntegerField()  # sq.ft
    panels_needed = models.IntegerField()

    panel_wattage = models.IntegerField(default=0)

    panel_unit_price = models.FloatField(default=0.0)
    panel_cost = models.FloatField(default=0.0)

    inverter_cost = models.FloatField(default=0.0)

    battery_cost = models.FloatField(default=0.0)

    mppt_cost = models.FloatField(default=0.0)

    structure_cost = models.FloatField(default=0.0)

    installation_fee = models.FloatField(default=0.0)

    tax_amount = models.FloatField(default=0.0)

    base_price = models.FloatField(default=0.0)

    sun_hours = models.FloatField(default=5)
    loss_factor = models.FloatField(default=1.2)
    system = models.CharField(max_length=100, null=True, blank=True)

    subsidy_percentage = models.FloatField(default=0.0) # e.g., 30.0 for 30%
    subsidy_amount = models.FloatField(default=0.0)
    protection_cost = models.FloatField(default=0.0)    # Combined cost of Lightning/Surge
    total_final_cost = models.FloatField(default=0.0)

    is_finalized = models.BooleanField(default=False) # Explicit tracking flag for Quotation page visit

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_system_display_name(self):
        mapping = {
            "ongrid": "On-Grid",
            "hybrid": "Hybrid",
            "offgrid": "Off-Grid"
        }
        return mapping.get(self.system, self.system.capitalize())

    def __str__(self):
        return f"{self.estimation.user} – {self.system_size}kW"
    

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
class PasswordResetOTP(models.Model):
    # Nullable foreign keys allow one table to handle both types
    user = models.ForeignKey(user, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.created_at + datetime.timedelta(minutes=10)


class SolarInstallationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('investigation_scheduled', 'Site Investigation Scheduled'),
        ('investigation_completed', 'Site Investigation Completed'),
        ('approved', 'Approved for Installation'),
        ('completed', 'Installation Completed'),
        ('rejected', 'Request Rejected'),
    ]

    user = models.ForeignKey('user', on_delete=models.CASCADE)
    estimation = models.ForeignKey(SolarEstimation, on_delete=models.SET_NULL, null=True, blank=True)

    EQUIPMENT_SOURCES = [
        ('estimation', 'Based on my last estimation'),
        ('store', 'Bought from the Solar Store'),
        ('external', 'Already have my own equipment'),
    ]
    equipment_source = models.CharField(max_length=20, choices=EQUIPMENT_SOURCES, default='estimation')

    system_size = models.FloatField(help_text="kW")
    panels_count = models.PositiveIntegerField()

    address = models.TextField()
    preferred_date = models.DateField()
    installation_date = models.DateField(null=True, blank=True)
    site_photos = models.ImageField(upload_to='installation_sites/', null=True, blank=True)
    additional_notes = models.TextField(blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    admin_feedback = models.TextField(blank=True)

    # ✅ NEW FIELD
    installation_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.full_name} - {self.system_size}kW"


from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class WorkAssignment(models.Model):
    WORK_TYPES = [
        ('investigation', 'Site Investigation'),
        ('installation', 'System Installation'),
    ]
    
    request = models.ForeignKey(SolarInstallationRequest, on_delete=models.CASCADE, related_name='assignments')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tasks')
    work_type = models.CharField(max_length=20, choices=WORK_TYPES)
    scheduled_date = models.DateField()
    
    # Track completion status and timing
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True) # NEW: Track exactly when they finished
    
    notes = models.TextField(blank=True, help_text="Specific instructions from admin")
    employee_feedback = models.TextField(blank=True, help_text="Notes from employee after completion") # NEW
    
    # NEW FIELDS: Mandatory media proof and text report
    proof_file = models.FileField(
        upload_to='work_proofs/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'mp4', 'mkv', 'mov'])]
    )
    report_text = models.TextField(blank=True, help_text="Detailed summary of the work done.")


    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_date', '-assigned_at']
        # Keeping your unique constraint - this is good!
        unique_together = ('request', 'employee', 'work_type')

    # Updated helper method signature to process files and reports
    def mark_as_complete(self, report_text, proof_file, feedback=None):
        """Handles mandatory completion validation and logging"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.report_text = report_text
        self.proof_file = proof_file
        if feedback:
            self.employee_feedback = feedback
        self.save()

    def __str__(self):
        return f"{self.get_work_type_display()} - {self.employee.full_name} ({self.scheduled_date})"
    



from django.db import models
from django.core.validators import MinValueValidator
import json


class Product(models.Model):
    UTILITY_GROUPS = [
        ('infra', 'Installation Components (Panels, Inverters, etc.)'),
        ('appliance', 'Solar Appliances (Fans, Lights, Pumps)'),
        ('other', 'Other Products'),
    ]

    CATEGORY_CHOICES = [
        # Infrastructure
        ('panel', 'Solar Panel'),
        ('inverter', 'Inverter'),
        ('mppt', 'MPPT Charger'),
        ('battery', 'Battery'),
        ('protection', 'Surge/Lighting Protector'),
        ('structure', 'Mounting & Racking'),
        ('accessory', 'Cables & Accessories'),
        ('monitoring', 'Monitoring & Smart Gateways'),
        # Appliances
        ('light', 'Solar Street/Garden Light'),
        ('fan', 'Solar DC Fan'),
        ('pump', 'Solar Water Pump'),
        ('heater', 'Solar Water Heater'),
        # Misc
        ('other', 'Miscellaneous Item'),
    ]

    name = models.CharField(max_length=150)
    utility_group = models.CharField(max_length=20, choices=UTILITY_GROUPS, default='infra')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    brand = models.CharField(max_length=100)
    model_no = models.CharField(max_length=100, blank=True, null=True)
    country_of_origin = models.CharField(max_length=100, default="India")
    
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(1.00)]
    )
    
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    # Professional Dynamic Specs stored as a Dictionary/JSON
    # Example: {"Material": "Monocrystalline", "Cells": 144, "Efficiency": "21%"}
    technical_specs = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True,null=True)

    # Professional Standard Fields
    efficiency = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="e.g. 21% for panels or 98% for inverters"
    )
    warranty_years = models.PositiveIntegerField(
        default=0, 
        help_text="Warranty period in years. Enter 0 for no warranty."
    )
    highlights = models.TextField(
        blank=True, 
        help_text="What makes this product stand out? (e.g., Best for high-temperature areas, sleek all-black design)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def technical_specs_json(self):
        return json.dumps(self.technical_specs)
    def __str__(self):
        # This shows: "Luminous - Poly Crystalline Solar Panel (Poly 110W/12V)"
        if self.model_no:
            return f"{self.brand} - {self.name} ({self.model_no})"
        # Fallback if model_no is empty: "Luminous - Poly Crystalline Solar Panel"
        return f"{self.brand} - {self.name}"

from django.db import models
from .models import Product, user   # ✅ use your custom model

class CartItem(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price per item
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    added_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.price = self.product.price
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

from django.db import models

class Product_payment(models.Model):
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField(null=True, blank=True)
    PAYMENT_METHODS = [
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='upi')
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
    ]

    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='Pending')
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InstallationPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('netbanking', 'Net Banking'),
    ]

    installation_request = models.OneToOneField(
        SolarInstallationRequest,
        on_delete=models.CASCADE,
        related_name='installationpayment'
    )

    user = models.ForeignKey(user, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # New Fields
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, null=True, blank=True)
    transaction_details = models.CharField(max_length=100, null=True, blank=True) # Stores UPI ID or Bank Name

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)



class ShippingAddress(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name='shipping_address')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

