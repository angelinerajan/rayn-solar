from pyexpat.errors import messages
from django.shortcuts import render, redirect,HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .import models
from django.db.models import Q


def index(request):
    return render(request,'index.html')

def register(request):
    msg = None
    success_registration = False
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        country = request.POST.get('country')
        photo = request.FILES.get('photo')
        password = request.POST.get('password')

        # EMAIL DUPLICATE CHECK 
        if models.user.objects.filter(email=email).exists():
            msg = "Email already registered"

            return render(request, 'user_register.html', {
                'msg': msg,
                'success_registration': False
            })

        # HASH THE PASSWORD BEFORE CREATING
        hashed_password = make_password(password)

        models.user.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password=hashed_password,  # Save the hashed version
            street_address=street_address,
            city=city,
            state=state,
            pincode=pincode,
            country=country,
            photo=photo
        )
        success_registration = True

    return render(request, 'user_register.html', {
        'msg': msg,
        'success_registration': success_registration
    })

from django.contrib.auth.hashers import check_password

def user_login(request):
    msg = None
    success_login = False

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = models.user.objects.get(email=email)

            if check_password(password, user_obj.password):
                request.session['user_id'] = user_obj.id
                request.session['user_email'] = user_obj.email                
                success_login = True
            else:
                msg = "Invalid email or password"
        except models.user.DoesNotExist:
            msg = "Invalid email or password"

    return render(request, 'user_login.html', {
        'msg': msg,
        'success_login': success_login
    })


def user_home(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
    
    # Retrieve user object
    user = models.user.objects.get(id=user_id)
    
    # Extract first name: splits by space and takes the first part
    # If full_name is "John Doe", first_name becomes "John"
    first_name = user.full_name.split()[0] if user.full_name else "User"
    
    context = {
        'user': user,
        'first_name': first_name  # Ensure this variable name matches the template
    }
    return render(request, 'user_home.html', context)


def user_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user= models.user.objects.get(id=user_id)
    

    return render(request, 'user_profile.html', {
        'user': user,
        
    })
    
def edit_user_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = models.user.objects.get(id=user_id)

    if request.method == 'POST':
        user.full_name = request.POST.get('full_name')
        #user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.street_address = request.POST.get('street_address')
        user.city = request.POST.get('city')
        user.state = request.POST.get('state')
        user.pincode = request.POST.get('pincode')
        user.country = request.POST.get('country')
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']
        user.save()
        return redirect('user_profile')

    return render(request, 'edit_user_profile.html', {'user': user})


from django.shortcuts import redirect
from django.contrib import messages
from . import models

def delete_user_account(request):
    if 'user_id' in request.session:
        user_id = request.session.get('user_id')
        try:
            user = models.user.objects.get(id=user_id)
            user.delete()
            request.session.flush()
        except models.user.DoesNotExist:
            pass
    return redirect('index')


def employee_register(request):
    success_registration = False
    msg = None
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        department = request.POST.get('department')
        designation = request.POST.get('designation')
        address = request.POST.get('residential_address')
        photo = request.FILES.get('photo')

        # EMAIL DUPLICATE CHECK
        if models.Employee.objects.filter(email=email).exists():
            msg = "Email already registered"

        models.Employee.objects.create(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password = make_password(password),  
            department=department,
            designation=designation,
            address=address,
            photo=photo
        )
        success_registration = True

    return render(request, 'employee_register.html', {
        'msg': msg,
        'success_registration': success_registration
    })


from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from . import models

from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from . import models

def employee_login(request):
    msg = None
    success_login = False
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            employee = models.Employee.objects.get(email=email)

            # 1. Secure Hashed Password Check
            if check_password(password, employee.password):
                
                # 2. Check if Admin has approved the account
                if employee.is_active:
                    # Set Session Data
                    request.session['employee_id'] = employee.id
                    request.session['employee_email'] = employee.email
                    request.session.modified = True
                    
                    # Set flag to trigger our success pop-up modal
                    success_login = True
                else:
                    msg = "Your account is currently inactive. Please wait for Admin approval."
            else:
                msg = "Invalid password. Please try again."

        except models.Employee.DoesNotExist:
            msg = "Email not registered in our system."

    return render(request, 'employee_login.html', {
        'msg': msg, 
        'success_login': success_login
    })


from datetime import date
from django.shortcuts import render, redirect
from . import models

def employee_home(request):
    employee_id = request.session.get('employee_id')
    if not employee_id:
        return redirect('employee_login')

    try:
        employee = models.Employee.objects.get(id=employee_id)
    except models.Employee.DoesNotExist:
        return redirect('employee_login')

    # Get all assignments for this employee
    # Note: Use the 'related_name' you defined in your WorkAssignment model
    # If you didn't define one, Django uses 'workassignment_set'
    all_assignments = models.WorkAssignment.objects.filter(employee=employee).order_by('scheduled_date')

    today = date.today()

    context = {
        'employee': employee,
        # 1. Today's Tasks: Specifically for today AND not yet finished
        'today_tasks': all_assignments.filter(scheduled_date=today, is_completed=False),
        
        # 2. Upcoming Tasks: Anything scheduled for tomorrow onwards (regardless of completion)
        'upcoming_tasks': all_assignments.filter(scheduled_date__gt=today),
        
        # 3. Past Works: Anything marked as completed
        'past_tasks': all_assignments.filter(is_completed=True).order_by('-scheduled_date') # Newest first
    }
    
    return render(request, 'employee_home.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . import models

def submit_work_report(request, assignment_id):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('employee_login')

    assignment = get_object_or_404(
        models.WorkAssignment,
        id=assignment_id,
        employee__id=employee_id
    )

    if request.method == 'POST':
        report_text = request.POST.get('report_text', '').strip()
        proof_file = request.FILES.get('proof_file')
        feedback = request.POST.get('employee_feedback', '').strip()

        if not report_text or not proof_file:
            return redirect('/employee_home/?status=error')

        assignment.mark_as_complete(
            report_text=report_text,
            proof_file=proof_file,
            feedback=feedback
        )

        return redirect('/employee_home/?status=success')

    return redirect('employee_home')


def logout(request):
    # 1. Check who is logged in BEFORE flushing
    is_admin = 'official_id' in request.session
    is_employee = 'employee_id' in request.session
    
    # 2. Clear the entire session
    request.session.flush()
    
    # 3. Redirect to the appropriate login page
    if is_admin:
        return redirect('admin_login')
    elif is_employee:
        return redirect('employee_login')
    else:
        # Defaults to the general user login or index
        return redirect('index')
    

def employee_profile(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('employee_login')

    employee = models.Employee.objects.get(id=employee_id)

    return render(request, 'employee_profile.html', {
        'employee': employee
    })



def edit_employee_profile(request):
    employee_id = request.session.get('employee_id')

    if not employee_id:
        return redirect('employee_login')

    employee = models.Employee.objects.get(id=employee_id)

    if request.method == "POST":
        employee.full_name = request.POST.get('full_name')
        employee.phone_number = request.POST.get('phone_number')
        employee.department = request.POST.get('department')
        employee.designation = request.POST.get('designation')
        employee.address = request.POST.get('address')

        if 'photo' in request.FILES:
            employee.photo = request.FILES['photo']

        employee.save()
        # messages.success(request, "Profile updated successfully")
        return redirect('employee_profile')

    return render(request, 'edit_employee_profile.html', {
        'employee': employee
    })


from django.shortcuts import render, redirect

def admin_login(request):
    error_msg = None
    success_login = False

    if request.method == 'POST':
        official_id = request.POST.get('official_id')
        password = request.POST.get('password')

        if official_id == 'your_admin_id' and password == 'your_admin_password':
            # Store ID in session to authenticate
            request.session['official_id'] = official_id
            # Set flag to trigger our custom confirmation modal on the frontend
            success_login = True
        else:
            error_msg = "Invalid admin credentials"

    return render(request, 'admin_login.html', {
        'error_msg': error_msg,
        'success_login': success_login
    })


from . import models

def admin_dashboard(request):
    if not 'official_id'  in request.session:
        return redirect('admin_login')
    users = models.user.objects.all()
    employees = models.Employee.objects.all()
    active_staff = employees.filter(is_active=True)
    install_reqs = SolarInstallationRequest.objects.all().order_by('-created_at')
    active_requests_count = install_reqs.filter(
        status__in=['pending', 'investigation_scheduled', 'approved'],
        is_deleted=False
    ).count()
    # NEW: Fetch the products for your new tab
    products = models.Product.objects.all().order_by('-created_at')
    user_query = request.GET.get('user_search')
    if user_query:
        # We use icontains so it works even if they don't type the '#'
        # or we can use exact match for IDs
        
        users = users.filter(
            Q(id__icontains=user_query.replace('#', '')) | 
            Q(full_name__icontains=user_query) | 
            Q(email__icontains=user_query)
        )
    context = {
        'users': users,
        'employees': employees,
        'active_staff': active_staff,
        'installation_requests': install_reqs,
        'active_count': active_requests_count,
        'products': products, # This must match the {% for p in products %} in your HTML
    }
    return render(request, 'admin_dashboard.html', context)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import SolarInstallationRequest

def save_installation_amount(request):
    if request.method == "POST":
        request_id = request.POST.get('request_id')
        amount = request.POST.get('amount')

        if not request_id or not amount:
            return JsonResponse({'success': False, 'error': 'Missing data'})

        try:
            installation = get_object_or_404(SolarInstallationRequest, id=request_id)
            # Check if a payment record already exists and if it's paid
            # Using hasattr or a try-except to check the OneToOne relation
            payment = getattr(installation, 'installationpayment', None)
            
            if payment and payment.status == 'paid':
                return JsonResponse({
                    'success': False, 
                    'error': 'Cannot edit amount. Payment has already been finalized by the user.'
                })

            # 1. Update the Main Request
            installation.installation_amount = amount
            installation.save()

            # 2. Update the Payment model automatically if it exists
            if payment:
                payment.amount = amount
                payment.save()
            # Note: We don't create the payment here because your 'pay_installation' 
            # view handles creation when the user clicks "Pay Now".

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Employee

def approve_employee(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    # Toggle status
    employee.is_active = not employee.is_active
    employee.save()
    
    status = "approved/activated" if employee.is_active else "deactivated"
    # messages.success(request, f"Employee {employee.full_name} has been {status}.")
    
    # Redirect back to the admin dashboard (ensure 'admin_dashboard' matches your URL name)
    return redirect('admin_dashboard')

from django.shortcuts import redirect
from .models import WorkAssignment, SolarInstallationRequest, Employee

def assign_work(request):
    if request.method == 'POST':
        req_id = request.POST.get('request_id')
        emp_id = request.POST.get('employee_id')
        work_type = request.POST.get('work_type')
        notes = request.POST.get('notes')

        scheduled_date = request.POST.get('scheduled_date')

        if scheduled_date:
            selected_date = date.fromisoformat(scheduled_date)

            if selected_date < date.today():
                messages.error(
                    request,
                    "Assignment date cannot be in the past."
                )
                return redirect('admin_dashboard')
        # Create the assignment
        WorkAssignment.objects.create(
            request_id=req_id,
            employee_id=emp_id,
            work_type=work_type,
            scheduled_date=scheduled_date,
            notes=notes
        )
        # Optional: Update the status of the main request
        # solar_req = SolarInstallationRequest.objects.get(id=req_id)
        # solar_req.status = 'investigation_scheduled' (or similar)
        # solar_req.save()

        return redirect('admin_dashboard')

from django.utils import timezone

def complete_assignment(request, assignment_id):
    if request.method == 'POST':
        task = get_object_or_404(models.WorkAssignment, id=assignment_id)
        
        # Capture feedback from the form (if you add a textarea)
        feedback = request.POST.get('feedback', '')
        
        # Use the helper method we added to the model
        task.is_completed = True
        task.completed_at = timezone.now()
        task.employee_feedback = feedback
        task.save()
        
    return redirect('employee_home')

def services(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    return render(request, "services.html")

import math
from django.shortcuts import render, redirect, get_object_or_404
from . import models

from django.shortcuts import render, redirect

def solar_estimation_form(request, estimation_id=None):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = models.user.objects.get(id=user_id)
    estimation = None

    # If an ID is provided, fetch the existing data to pre-populate the form
    if estimation_id:
        estimation = models.SolarEstimation.objects.filter(id=estimation_id, user=user).first()

    if request.method == "POST":
        data = {
            "location": request.POST.get("location"),
            "monthly_units": request.POST.get("monthly_units"),
            "building_type": request.POST.get("building_type"),
            "roof_type": request.POST.get("roof_type"),
            "roof_area": request.POST.get("roof_area"),
            "power_cut": request.POST.get("power_cut"),
            "backup_required": request.POST.get("backup_required"),
            "apply_subsidy": request.POST.get("apply_subsidy"),
            "subsidy_percentage": request.POST.get("subsidy_percentage", 0), 
            "subsidy_fixed_amount": request.POST.get("subsidy_fixed_amount", 0), 
            "lightning_protection": request.POST.get("lightning_protection"),
            "surge_protection": request.POST.get("surge_protection"),
        }

        if not all([data["location"], data["monthly_units"], data["building_type"]]):
            return render(request, "solar_estimation_form.html", {"error": "Please fill all required fields.", "estimation": estimation})

        # Process standard clean parsing integers/floats
        parsed_units = int(data["monthly_units"])
        parsed_area = int(data["roof_area"])
        parsed_pct = float(data["subsidy_percentage"]) if data["subsidy_percentage"] else 0.0
        parsed_amt = float(data["subsidy_fixed_amount"]) if data["subsidy_fixed_amount"] else 0.0

        if estimation:
            # Update existing instance instead of duplicating database records
            estimation.location = data["location"]
            estimation.monthly_units = parsed_units
            estimation.building_type = data["building_type"]
            estimation.roof_type = data["roof_type"]
            estimation.roof_area = parsed_area
            estimation.power_cut = data["power_cut"]
            estimation.backup_required = data["backup_required"]
            estimation.apply_subsidy = data["apply_subsidy"]
            estimation.subsidy_percentage = parsed_pct
            estimation.subsidy_fixed_amount = parsed_amt
            estimation.lightning_protection = data["lightning_protection"]
            estimation.surge_protection = data["surge_protection"]
            estimation.save()
        else:
            # Create a brand new record if starting fresh
            estimation = models.SolarEstimation.objects.create(
                user=user,
                location=data["location"],
                monthly_units=parsed_units,
                building_type=data["building_type"],
                roof_type=data["roof_type"],
                roof_area=parsed_area,
                power_cut=data["power_cut"],
                backup_required=data["backup_required"],
                apply_subsidy=data["apply_subsidy"],
                subsidy_percentage=parsed_pct,
                subsidy_fixed_amount=parsed_amt,
                lightning_protection=data["lightning_protection"],
                surge_protection=data["surge_protection"],
            )

        return redirect("solar_recommendation", estimation_id=estimation.id)

    return render(request, "solar_estimation_form.html", {"estimation": estimation})


def solar_recommendation(request, estimation_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = get_object_or_404(models.user, id=user_id)
    estimation = get_object_or_404(models.SolarEstimation, id=estimation_id, user=user)

    # A. Check if the user already selected or saved a manual system choice previously
    existing_tech = models.SolarTechnicalData.objects.filter(estimation=estimation).first()
    
    # FIXED LOGIC MAP: Prioritize whatever is currently inside your technical data database row
    if existing_tech and existing_tech.system:
        recommended_system_code = existing_tech.system
    else:
        # Fall back to automated rules only if starting completely fresh
        power_cut = estimation.power_cut
        backup_required = estimation.backup_required

        if backup_required == "no" and power_cut == "none":
            recommended_system_code = "ongrid"
        elif backup_required == "yes" and power_cut == "frequent":
            recommended_system_code = "offgrid"
        else:
            recommended_system_code = "hybrid"

    # B. Map code back to presentation strings for the context dictionary
    display_maps = {
        "ongrid": ("On-Grid System", "Lowest cost and maximum savings due to stable electricity"),
        "offgrid": ("Off-Grid System", "Best choice for frequent power cuts and full backup requirement"),
        "hybrid": ("Hybrid System", "Balanced solution with savings and battery backup")
    }
    
    display_name, reason = display_maps.get(recommended_system_code, display_maps["hybrid"])

    # C. Commit cleanly to DB without overwriting custom selections
    # Fetch or create the object instance explicitly so the context dictionary stays current
    tech_record, created = models.SolarTechnicalData.objects.update_or_create(
        estimation=estimation,
        defaults={
            "system": recommended_system_code,
            "daily_units": round(float(estimation.monthly_units) / 30, 2),
            # Only set these structure minimums to 0 on the very first creation run
            # so we don't accidentally wipe calculated data out if they navigate backward
            "system_size": existing_tech.system_size if existing_tech else 0.0,
            "roof_required": existing_tech.roof_required if existing_tech else 0,
            "panels_needed": existing_tech.panels_needed if existing_tech else 0,
        }
    )

    context = {
        "estimation": estimation,
        "recommended_system": display_name,
        "reason": reason,
        "tech_record": tech_record, # FIXED: Send the newly synchronized/verified record instance
    }
    return render(request, "solar_recommendation.html", context)
 

import math


def solar_system_size(request, estimation_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    user = get_object_or_404(models.user, id=user_id)
    estimation = get_object_or_404(models.SolarEstimation, id=estimation_id, user=user)

    # 1. Read existing system type string directly from Technical Data store
    if request.method == "POST":
        selected_system = request.POST.get("system")
    else:
        tech_record = models.SolarTechnicalData.objects.filter(estimation=estimation).first()
        # Fallback to 'ongrid' if a record hasn't been created yet for some reason
        selected_system = tech_record.system if tech_record else "ongrid"

    system_key = selected_system.lower().strip()
    
    # 2. Base Technical Calculations
    monthly_units = float(estimation.monthly_units)
    daily_units = monthly_units / 30
    sun_hours = 5
    loss_factor = 1.2
    raw_size = (daily_units / sun_hours) * loss_factor
    system_size = round(raw_size * 2) / 2 

    # 3. Identify the Commercial Footprint
    is_commercial = estimation.building_type in ['factory', 'warehouse', 'hospital', 'industrial', 'skyscraper', 'school', 'office']
        
    # 4. Dynamic Protection & Sizing Matrix Calculations
    if is_commercial:
        lp_cost = 25000 if estimation.lightning_protection == "yes" else 0
        sp_cost = 12000 if estimation.surge_protection == "yes" else 0
        roof_required = int(system_size * 70)
        panel_wattage = 600
        panel_unit_price = 15000
    else:
        lp_cost = 4000 if estimation.lightning_protection == "yes" else 0
        sp_cost = 2500 if estimation.surge_protection == "yes" else 0
        roof_required = int(system_size * 80)
        panel_wattage = 500
        panel_unit_price = 16000
        
    protection_total = lp_cost + sp_cost
    panels_needed = math.ceil((system_size * 1000) / panel_wattage)
    structure_per_sqft = 60
    
    if is_commercial:
        inverter_rates = {"ongrid": 10000, "hybrid": 22000, "offgrid": 28000}
        battery_rates = {"ongrid": 0, "hybrid": 20000, "offgrid": 45000}
    else:
        inverter_rates = {"ongrid": 12000, "hybrid": 18000, "offgrid": 14000}
        battery_rates = {"ongrid": 0, "hybrid": 18000, "offgrid": 24000}

    total_panel_cost = panels_needed * panel_unit_price
    inverter_cost = system_size * inverter_rates.get(system_key, 15000)
    structure_cost = roof_required * structure_per_sqft
    battery_cost = system_size * battery_rates.get(system_key, 0)
    
    mppt_cost = 0.0
    if system_key == "offgrid" and not is_commercial:
        mppt_cost = 6500 + (system_size * 4000)
        
    base_price = total_panel_cost + inverter_cost + structure_cost + battery_cost + mppt_cost
    installation_fee = base_price * 0.07
    
    # 5. CUSTOM SUBSIDY CALCULATOR ENGINE (Percentage vs Fixed Amount)
    sub_percent = 0.0
    sub_amount = 0.0
    subsidy_choice = estimation.apply_subsidy

    if system_key in ["ongrid", "hybrid"] and subsidy_choice == "percentage":
        sub_percent = estimation.subsidy_percentage
        sub_amount = base_price * (sub_percent / 100)
    elif system_key in ["ongrid", "hybrid"] and subsidy_choice == "fixed_amount":
        sub_amount = getattr(estimation, 'subsidy_fixed_amount', 0.0)
        sub_percent = (sub_amount / base_price) * 100 if base_price > 0 else 0.0
    
    # Finalize Total Layout
    taxable_amount = base_price + installation_fee + protection_total
    tax = taxable_amount * 0.138
    final_total = (taxable_amount + tax) - sub_amount

    # 6. Save data completely into Technical Data Store (updating the record)
    models.SolarTechnicalData.objects.update_or_create(
        estimation=estimation,
        defaults={
            "daily_units": round(daily_units, 2),
            "system_size": system_size,
            "roof_required": roof_required,
            "panels_needed": panels_needed,
            "panel_wattage": panel_wattage,

            "panel_unit_price": panel_unit_price,
            "panel_cost": total_panel_cost,
            "inverter_cost": inverter_cost,
            "battery_cost": battery_cost,
            "mppt_cost": mppt_cost,
            "structure_cost": structure_cost,

            "installation_fee": installation_fee,
            "tax_amount": tax,
            "base_price": base_price,
            "system": selected_system,
            "subsidy_percentage": sub_percent,
            "subsidy_amount": sub_amount,
            "protection_cost": protection_total,
            "total_final_cost": final_total,
        }
    )

    system_display_names = {
        "ongrid": "On-Grid System",
        "hybrid": "Hybrid System",
        "offgrid": "Off-Grid System"
    }
    clean_display_name = system_display_names.get(system_key, system_key.capitalize())

    context = {
        "daily_units": daily_units,
        "monthly_units": monthly_units,
        "estimation": estimation,
        "system_display_name": clean_display_name,
        "system": system_key,
        "system_size": system_size,
        "roof_required": roof_required,
        "panels_needed": panels_needed,
        "base_price": round(base_price, 2),
        "sub_percent": sub_percent,
        "sub_amount": round(sub_amount, 2),
        "protection_cost": protection_total,
        "total_cost": round(final_total, 2),
    }
    return render(request, "solar_system_size.html", context)

def solar_history(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    user = models.user.objects.get(id=user_id)

    estimations = (
        models.SolarEstimation.objects
        .filter(user=user)
        .select_related('technical')
        .order_by('-created_at')
    )

    # Check each estimation record's completion status dynamically
    # UPDATED COMPLETION CHECK: Depend directly on our new database flag
    for est in estimations:
        has_tech = hasattr(est, 'technical') and est.technical is not None
        
        # 1. Fully Complete: They viewed the quotation page
        est.is_complete = has_tech and est.technical.is_finalized
        
        # 2. Partially Complete: They at least finished the calculations/size page
        # If system_size is 0, they dropped off *before* this page processed anything
        est.has_calculations = has_tech and est.technical.system_size > 0.0

    return render(request, "solar_history.html", {
        "estimations": estimations
    })


def delete_estimation(request, estimation_id):
    user_id = request.session.get('user_id')
    estimation = get_object_or_404(models.SolarEstimation, id=estimation_id, user_id=user_id)
    estimation.delete()
    return redirect('solar_history')


from django.shortcuts import render, redirect, get_object_or_404
from . import models

def format_indian_currency(amount):
    """Converts a float/int into an Indian numbering system string format (without the symbol)."""
    try:
        amount = float(amount)
        # Handle negative values safely if any slip through
        is_negative = amount < 0
        amount = abs(amount)
        
        # Split into integer and fractional components
        s = f"{amount:.2f}"
        parts = s.split('.')
        dec = parts[1]
        num = parts[0]
        
        # Handle the last 3 digits (Hundreds, Tens, Units)
        if len(num) <= 3:
            result = num
        else:
            last_three = num[-3:]
            remaining = num[:-3]
            
            # Group remaining digits in pairs of twos (Lakhs, Crores)
            out = []
            while len(remaining) > 2:
                out.append(remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                out.append(remaining)
            out.reverse()
            result = ",".join(out) + "," + last_three
            
        final_str = f"{result}.{dec}"
        return f"-{final_str}" if is_negative else final_str
    except (ValueError, TypeError):
        return "0.00"
    

def solar_quotation(request, estimation_id):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    user = get_object_or_404(models.user, id=user_id)

    estimation = get_object_or_404(
        models.SolarEstimation,
        id=estimation_id,
        user=user
    )

    tech_data = get_object_or_404(
        models.SolarTechnicalData,
        estimation=estimation
    )

    if not tech_data or tech_data.system_size == 0.0:
        return redirect(
            'solar_recommendation',
            estimation_id=estimation_id
        )

    if not tech_data.is_finalized:
        tech_data.is_finalized = True
        tech_data.save(update_fields=['is_finalized'])

    is_commercial = estimation.building_type in [
        'factory', 'warehouse', 'hospital', 'industrial',
        'skyscraper', 'school', 'office'
    ]

    total_price = float(tech_data.total_final_cost)

    # =========================================================
    # 1. PERFORMANCE RATIO & MAINTENANCE FACTOR CALCULATION
    # =========================================================
    system_type_lower = tech_data.system.lower().replace('-', '').strip()

    if system_type_lower == 'offgrid':
        performance_ratio = 0.65
        maintenance_factor = 0.18
    elif system_type_lower == 'hybrid':
        performance_ratio = 0.70
        maintenance_factor = 0.12
    else:
        performance_ratio = 0.82 if is_commercial else 0.78
        maintenance_factor = 0.08

    # =========================================================
    # 2. YEAR 1 ENERGY GENERATION
    # =========================================================
    annual_units_year1 = (
        float(tech_data.system_size)
        * 4.5
        * 365
        * performance_ratio
    )

    daily_generation = annual_units_year1 / 365
    monthly_generation = annual_units_year1 / 12

    # =========================================================
    # 3. FINANCIAL BASELINES
    # =========================================================
    initial_unit_rate = 9.5 if is_commercial else 8.2

    annual_savings_year1 = annual_units_year1 * initial_unit_rate
    average_unit_reduction = monthly_generation
    monthly_savings = average_unit_reduction * initial_unit_rate

    # =========================================================
    # 4. PAYBACK PERIOD
    # =========================================================
    payback_years = round(
        total_price / annual_savings_year1,
        1
    ) if annual_savings_year1 > 0 else 0

    # =========================================================
    # 5. DYNAMIC 25 YEAR ROI FORECASTING (FIXED LOOP)
    # =========================================================
    cumulative_savings = 0.0
    current_unit_rate = initial_unit_rate
    current_generation = annual_units_year1

    # Loop runs from 1 to 25 inclusive (25 full cycles)
    for year in range(1, 26):
        yearly_savings = current_generation * current_unit_rate
        cumulative_savings += yearly_savings

        # Scale panel degradation and tariff inflation forward
        current_generation *= 0.993
        current_unit_rate *= 1.03

    maintenance_deduction = cumulative_savings * maintenance_factor
    lifetime_savings = cumulative_savings - maintenance_deduction - total_price

    context = {
        "estimation": estimation,
        "tech_data": tech_data,

        # Cost Breakdown Strings
        "panel_cost": format_indian_currency(tech_data.panel_cost),
        "inverter_cost": format_indian_currency(tech_data.inverter_cost),
        "battery_cost": format_indian_currency(tech_data.battery_cost),
        "mppt_cost": format_indian_currency(tech_data.mppt_cost),
        "structure_cost": format_indian_currency(tech_data.structure_cost),
        "installation_fee": format_indian_currency(tech_data.installation_fee),
        "tax": format_indian_currency(tech_data.tax_amount),
        "base_price": format_indian_currency(tech_data.base_price),
        "sub_percent": round(tech_data.subsidy_percentage, 2),
        "subsidy_amount": format_indian_currency(tech_data.subsidy_amount),
        "protection_cost": format_indian_currency(tech_data.protection_cost),
        "total_price": format_indian_currency(total_price),

        # ROI & Financial Outputs
        "annual_savings_year1": format_indian_currency(annual_savings_year1),
        "monthly_savings": format_indian_currency(monthly_savings),
        "average_unit_reduction": round(average_unit_reduction, 1),
        "payback_years": payback_years,
        "lifetime_savings": format_indian_currency(lifetime_savings),

        # Production Metrics
        "daily_generation": round(daily_generation, 1),
        "monthly_generation": round(monthly_generation, 1),
        "annual_generation": round(annual_units_year1, 1),

        # System Constants
        "performance_ratio": round(performance_ratio * 100, 1),
        "maintenance_factor": round(maintenance_factor * 100, 1),
        "currency": "₹",
    }

    return render(request, "solar_quotation.html", context)


from django.shortcuts import render, redirect, get_object_or_404 # Ensure redirect and get_object_or_404 are here
from django.utils import timezone
import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
def download_quotation_pdf(request, estimation_id):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    user = get_object_or_404(models.user, id=user_id)

    estimation = get_object_or_404(
        models.SolarEstimation,
        id=estimation_id,
        user=user
    )

    tech_data = get_object_or_404(
        models.SolarTechnicalData,
        estimation=estimation
    )

    is_commercial = estimation.building_type in [
        'factory',
        'warehouse',
        'hospital',
        'industrial',
        'skyscraper',
        'school',
        'office'
    ]

    # -----------------------------
    # ROI CALCULATIONS
    # -----------------------------
    system_type_lower = tech_data.system.lower().replace('-', '').strip()
    if system_type_lower == 'offgrid':
        performance_ratio, maintenance_factor = 0.65, 0.18
    elif system_type_lower == 'hybrid':
        performance_ratio, maintenance_factor = 0.70, 0.12
    else:
        performance_ratio, maintenance_factor = (0.82 if is_commercial else 0.78), 0.08

    annual_units_year1 = float(tech_data.system_size) * 4.5 * 365 * performance_ratio
    initial_unit_rate = 9.5 if is_commercial else 8.2
    total_price = float(tech_data.total_final_cost)

    # 25-Year Loop
    cumulative_savings = 0.0
    current_unit_rate = initial_unit_rate
    current_generation = annual_units_year1
    for year in range(1, 26):
        cumulative_savings += (current_generation * current_unit_rate)
        current_generation *= 0.993
        current_unit_rate *= 1.03

    maintenance_deduction = cumulative_savings * maintenance_factor
    lifetime_savings = cumulative_savings - maintenance_deduction - total_price

    context = {
        "company_name": "Rayn Solar",
        "customer_name": f"{user.full_name}" or "Valued Customer",
        "generation_date": timezone.now().strftime("%d %b %Y"),
        "estimation": estimation,
        "tech_data": tech_data,
        "building_type": estimation.get_building_type_display(),
    
        # Costs
        "base_subtotal": round(tech_data.base_price, 2),
        "panel_cost": round(tech_data.panel_cost, 2),
        "inverter_cost": round(tech_data.inverter_cost, 2),
        "battery_cost": round(tech_data.battery_cost, 2),
        "mppt_cost": round(tech_data.mppt_cost, 2),
        "structure_cost": round(tech_data.structure_cost, 2),
        "installation_fee": round(tech_data.installation_fee, 2),
        "tax": round(tech_data.tax_amount, 2),
        "subsidy_amount": round(tech_data.subsidy_amount, 2),
        "sub_percent": round(tech_data.subsidy_percentage, 2),
        "protection_cost": round(tech_data.protection_cost, 2),
        "total_price": round(total_price, 2),
        
        # ROI & Financials
        "annual_savings": round(annual_units_year1 * initial_unit_rate, 2),
        "monthly_savings": round((annual_units_year1 / 12) * initial_unit_rate, 2),
        "payback_years": round(total_price / (annual_units_year1 * initial_unit_rate), 1) if annual_units_year1 > 0 else 0,
        "lifetime_savings": round(lifetime_savings, 2),
        
        # NEW: Production Metrics (To match your dashboard)
        "daily_generation": round(annual_units_year1 / 365, 1),
        "monthly_generation": round(annual_units_year1 / 12, 1),
        "annual_generation": round(annual_units_year1, 1),
        
        # NEW: System Constants
        "performance_ratio": round(performance_ratio * 100, 1),
        "maintenance_factor": round(maintenance_factor * 100, 1),
        "currency": "₹",
    }

    template = get_template('solar_quotation_pdf.html')

    html = template.render(context)

    result = io.BytesIO()

    pdf = pisa.pisaDocument(
        io.BytesIO(html.encode("UTF-8")),
        result
    )

    if not pdf.err:
        response = HttpResponse(
            result.getvalue(),
            content_type='application/pdf'
        )

        response['Content-Disposition'] = (
            f'attachment; filename="RaynSolar_Quotation_{estimation.id}.pdf"'
        )

        return response

    return HttpResponse(
        "PDF Generation Error",
        status=400
    )


import logging  # <--- This is the one for the logger
import traceback



# Set up logging so you can see errors in your terminal
logger = logging.getLogger(__name__)

@csrf_exempt
def chatbot(request):

    if request.method == "GET":
        request.session["chatbot_conversation"] = []
        return render(request, "chatbot.html")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"response": "Please enter a message"})

            conversation = request.session.get("chatbot_conversation", [])
            
            if not conversation:
                ray_identity = {
                    "role": "system",
                    "content": (
                       "You are Ray, the AI assistant of Rayn Solar."

                "Rayn Solar provides Solar cost estimation, Solar product marketplace, Solar installation services"

                "Users can estimate systems, buy products, request installations, track status, make payments, and download invoices."

                "Installation workflow:Pending → Site Investigation → Approved/Rejected → Installation Scheduled → Installation Completed → Finalized"

                "Admins manage users, employees, investigations, installations, and approvals."

                "Users cannot view employee work reports or perform admin actions."

                "Be professional, concise, and helpful."
                """For product-related questions:
                    - Refer users to the marketplace inventory for the latest available products and brands.
                    - Do not invent product information.
                    - If you are unsure whether a product is available, ask the user to check the inventory.
                    - Do not ask users if they want to be redirected, navigated, or taken to a page.
- Do not claim you can open pages, navigate the website, click buttons, submit forms, process payments, or perform actions on behalf of users."""
                        

                    )
                }
                conversation.append(ray_identity)

            conversation.append({"role": "user", "content": user_message})

            payload = {
                "model": settings.GROQ_MODEL2,
                "messages": conversation,
                "temperature": 0.7,
                "max_tokens": 400
            }

            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY2}",
                "Content-Type": "application/json"
            }
            #  4. Request response from Groq            
            resp = requests.post(settings.GROQ_API_URL2, headers=headers, json=payload, timeout=30)
            resp.raise_for_status() # Check for API errors
            resp_data = resp.json()
            reply = resp_data["choices"][0]["message"]["content"].strip()
            # 5. Add Ray's reply to the history and save session
            conversation.append({"role": "assistant", "content": reply})
            request.session["chatbot_conversation"] = conversation

            return JsonResponse({"response": reply})

        except Exception as e:
            # traceback.print_exc() 
            # logger.error(f"Chatbot Error: {str(e)}")
            # return JsonResponse({"response": f"System error: {str(e)}"}, status=500)
            # Log the actual error to your terminal for debugging
            logger.error(f"Chatbot Error: {e}")
            return JsonResponse({"response": "I'm having a little trouble thinking right now. Try again?"})

    return JsonResponse({"response": "Invalid request"}, status=405)


import json
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def chatbot_index(request):

    # ---------------------------
    # 1️⃣ Initialize Conversation
    # ---------------------------
    if request.method == "GET":
        request.session["solar_conversation"] = [
            {
                "role": "system",
                "content": (
                    "Your name is Ray. You are a professional and helpful AI assistant in the Rayn Solar.  "
                    "Rayn Solar provides Solar cost estimation, Solar product marketplace, Solar installation services"

                "Users can estimate systems, buy products, request installations, track status, make payments, and download invoices."

                "Installation workflow:Pending → Site Investigation → Approved/Rejected → Installation Scheduled → Installation Completed → Finalized"

                "Admins manage users, employees, investigations, installations, and approvals."

                "Users cannot view employee work reports or perform admin actions."

                "Be professional, concise, and helpful."

                    "Follow these rules strictly:\n"

                    "1. If the user greets you (hi, hello, how are you, good morning, etc.), "
                    "respond politely and guide them to ask about solar services.\n\n"

                    "2. You ONLY provide detailed answers about Rayn Solar and the following\n"
                    "- Solar cost estimation\n"
                    "- Solar installation services\n"
                    "- Solar panels, inverters & batteries\n"
                    "- Government solar subsidy in India\n"
                    "- Energy savings and ROI\n\n"

                    "3. If the question is NOT related to Rayn Solar or solar services, "
                    "reply strictly with:\n"
                    "'I can only help with Rayn Solar services and cost estimation.'\n\n"
                    """For product-related questions:
                    - Refer users to the marketplace inventory for the latest available products and brands.
                    - Do not invent product information.
                    - If you are unsure whether a product is available, ask the user to check the inventory.
                    - Do not ask users if they want to be redirected, navigated, or taken to a page.
- Do not claim you can open pages, navigate the website, click buttons, submit forms, process payments, or perform actions on behalf of users."""
                    "Do not answer general knowledge, entertainment, politics, coding, "
                    "sports, or any unrelated topics."
                )
            }
        ]
        return render(request, "chatbot_index.html")

    # ---------------------------
    # 2️⃣ Handle Chat Messages
    # ---------------------------
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({
                    "response": "Please ask a solar-related question ☀️"
                })

            lower_msg = user_message.lower()

            # ---------------------------
            # 3️⃣ Greeting Handler
            # ---------------------------
            greetings = [
                "hi", "hello", "hey",
                "how are you", "good morning",
                "good evening", "good afternoon"
            ]

            if lower_msg in greetings:
                return JsonResponse({
                    "response":
                    "Hello 👋 I'm Ray. "
                    "How can I help you with solar cost estimation or installation services today?"
                })

            # ---------------------------
            # 4️⃣ Strict Unrelated Filter
            # ---------------------------
            blocked_keywords = [
                "joke", "movie", "actor", "cricket",
                "football", "python", "code",
                "president", "politics", "celebrity"
            ]

            if any(word in lower_msg for word in blocked_keywords):
                return JsonResponse({
                    "response":
                    "I can only help with RaynSolar solar services and cost estimation."
                })

            # ---------------------------
            # 5️⃣ Continue Conversation
            # ---------------------------
            conversation = request.session.get("solar_conversation", [])
            conversation.append({"role": "user", "content": user_message})

            payload = {
                "model": settings.GROQ_MODEL2,
                "messages": conversation,
                "temperature": 0.2,
                "max_tokens": 350
            }

            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY2}",
                "Content-Type": "application/json"
            }

            resp = requests.post(
                settings.GROQ_API_URL2,
                headers=headers,
                json=payload,
                timeout=60
            )

            reply = resp.json()["choices"][0]["message"]["content"].strip()

            conversation.append({"role": "assistant", "content": reply})
            request.session["solar_conversation"] = conversation

            return JsonResponse({"response": reply})

        except Exception as e:
            return JsonResponse({
                "response": "Something went wrong. Please try again."
            })

    return JsonResponse({"response": "Invalid request"}, status=405)

# User forgot password
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from . import models
import random
def get_user_model(user_type):
    return models.user if user_type == 'user' else models.Employee

def forgot_password(request, user_type):
    context = {'user_type': user_type}
    if request.method == "POST":
        email = request.POST.get("email")
        model = get_user_model(user_type)
        try:
            user_obj = model.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            
            # Save OTP
            if user_type == 'user':
                models.PasswordResetOTP.objects.create(user=user_obj, otp=otp)
            else:
                models.PasswordResetOTP.objects.create(employee=user_obj, otp=otp)
            
            request.session['reset_user_id'] = user_obj.id
            request.session['reset_user_type'] = user_type
            
            # Email Content
            subject = "Important: OTP for Your Password Reset Request"
            html_content = f"""
            <div style="font-family: 'Segoe UI', sans-serif; max-width: 500px; margin: auto; padding: 25px; border: 1px solid #e0e0e0; border-radius: 15px;">
                <div style="text-align: center; border-bottom: 3px solid #fbc02d; padding-bottom: 15px;">
                    <h1 style="color: #1a5f7a; margin: 0;">Rayn Solar</h1>
                </div>
                <div style="padding: 20px 0; text-align: center;">
                    <h3>Verification Code</h3>
                    <div style="background-color: #fffde7; border: 2px solid #fbc02d; padding: 20px; margin: 25px 0; border-radius: 12px;">
                        <span style="font-size: 36px; font-weight: bold; letter-spacing: 10px; color: #1a5f7a;">{otp}</span>
                    </div>
                    <p style="color: #d32f2f;">☀️ Valid for the next 10 minutes.</p>
                </div>
            </div>
            """

            send_mail(
                subject=subject,
                message=f"Your OTP is {otp}",
                from_email=None, # Uses DEFAULT_FROM_EMAIL from settings.py
                recipient_list=[email],
                html_message=html_content,
                fail_silently=False,
            )
            
            return redirect('verify_otp', user_type=user_type)
        except model.DoesNotExist:
            context['error'] = "This email is not registered."
            
    return render(request, 'forgot_password.html', context)

def verify_otp(request, user_type):
    context = {'user_type': user_type}
    user_id = request.session.get('reset_user_id')
    if not user_id: return redirect('forgot_password', user_type=user_type)

    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        query = {'otp': entered_otp, ('user_id' if user_type == 'user' else 'employee_id'): user_id}
        
        try:
            otp_obj = models.PasswordResetOTP.objects.filter(**query).latest('created_at')
            if otp_obj.is_expired():
                context['error'] = "OTP expired."
            else:
                request.session['otp_verified'] = True
                return redirect('reset_password', user_type=user_type)
        except models.PasswordResetOTP.DoesNotExist:
            context['error'] = "Invalid OTP."
    
    return render(request, 'verify_otp.html', context)

from django.contrib.auth.hashers import make_password, check_password

def reset_password(request, user_type):
    context = {'user_type': user_type}
    if not request.session.get('otp_verified'): 
        return redirect('forgot_password', user_type=user_type)
    
    user_id = request.session.get('reset_user_id')
    user_obj = get_object_or_404(get_user_model(user_type), id=user_id)

    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # 1. Check if passwords match
        if password != confirm_password:
            context['error'] = "Passwords do not match."
            
        # 2. Check if new password is the same as the old one
        elif check_password(password, user_obj.password):
            context['error'] = "New password cannot be the same as the old password."
            
        else:
            # 3. Success: Update and clear
            user_obj.password = make_password(password)
            user_obj.save()
            request.session.flush()
            return redirect(f'{user_type}_login')
            
    return render(request, 'reset_password.html', context)

# Emploee forgot password
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
import random
from django.core.mail import send_mail
from .models import PasswordResetOTP
import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from . import models

from django.shortcuts import render, redirect
from .models import SolarEstimation, SolarTechnicalData, SolarInstallationRequest, User # Import your User model
from . import models

def installation_request_view(request):
    # 1. Manual Session Check
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    # 2. Fetch the User object
    try:
        current_user = models.user.objects.get(id=user_id)
    except models.user.DoesNotExist:
        request.session.flush()
        return redirect('user_login')

    # 3. Get the last estimation (needed for pre-filling the form)
    last_est = models.SolarEstimation.objects.filter(user_id=user_id).order_by('-created_at').first()
    
    technical = None
    if last_est:
        technical = getattr(last_est, 'technical', None)

    # 4. Handle Form Submission
    if request.method == "POST":
        equipment_source = request.POST.get('equipment_source')
        estimation_to_save = last_est if equipment_source == 'estimation' else None
        
        models.SolarInstallationRequest.objects.create(
            user=current_user,
            estimation=estimation_to_save,
            equipment_source=equipment_source,
            system_size=request.POST.get('system_size'),
            panels_count=request.POST.get('panels_count'),
            address=request.POST.get('address'),
            preferred_date=request.POST.get('preferred_date'),
            additional_notes=request.POST.get('notes'),
            site_photos=request.FILES.get('site_photo')
        )
        # CHANGE: Redirect to history page instead of services
        return redirect('installation_history') 

    # CHANGE: Removed 'existing_request' from context
    context = {
        'last_est': last_est,
        'technical': technical,
    }
    
    return render(request, 'installation_request.html', context)

# admin.py
from django.contrib import admin
from .models import SolarInstallationRequest


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import SolarInstallationRequest

from datetime import date
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def manage_installation_request(request, pk, status):
    admin_id = request.session.get('official_id')
    if not admin_id:
        return redirect('admin_login')
    
    obj = get_object_or_404(SolarInstallationRequest, pk=pk)
    if obj.is_deleted:
        messages.error(request, "This request has been deleted by the user and cannot be modified.")
        return redirect('admin_dashboard')
    # 3. Validation: Prevent approval before the investigation date occurs
    if status == 'approved':
        if obj.status == 'pending':
            messages.error(request, "You must schedule a site investigation before approving.")
            return redirect('admin_dashboard')
        
        if obj.preferred_date > date.today():
            messages.error(request, f"Cannot approve yet. Site investigation is set for {obj.preferred_date}.")
            return redirect('admin_dashboard')

    # 4. Update the status and Save
    obj.status = status
    
    # Logic: If admin is approving, we assume the investigation date 
    # now represents the actual Installation Date.
    obj.save() 

    # 5. Success Message logic
    # display_status = status.replace('_', ' ').capitalize()
    # if status == 'rejected':
    #     messages.error(request, f"Request #{pk} has been {display_status}.")
    # else:
    #     messages.success(request, f"Request #{pk} updated to: {display_status}.")

    return redirect('admin_dashboard')

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def delete_installation_request(request, pk):
    # 1. Get user_id from session
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    # 2. Look for the request AND ensure it belongs to this user
    installation = get_object_or_404(SolarInstallationRequest, pk=pk, user_id=user_id)

    # Block deletion for both 'completed' and 'rejected' statuses
    if installation.status in ['completed', 'rejected']:
        messages.error(request, f"Finalized requests (ID #{pk}) cannot be removed.")
        return redirect('installation_history')
    
    # 3. Perform the soft delete
    installation.is_deleted = True
    installation.save()
    
    # messages.success(request, "Request removed from your history.")
    return redirect('installation_history')

def edit_request_date(request, pk):
    # Ensure admin is logged in
    if 'official_id' not in request.session:
        return redirect('admin_login')

    obj = get_object_or_404(SolarInstallationRequest, pk=pk)
    
    if obj.is_deleted:
            return JsonResponse({'success': False, 'error': 'Request is deleted'}, status=403)
    
    if request.method == 'POST':
        new_date = request.POST.get('new_date')
        if new_date:
            obj.preferred_date = new_date
            # Update status if it was previously pending
            if obj.status == 'pending':
                obj.status = 'investigation_scheduled'
            
            obj.save()
            # messages.success(request, f"Schedule for Request #{pk} updated to {new_date}.")
            return redirect('admin_dashboard')

    return render(request, 'edit_request_date.html', {'obj': obj})

from django.http import JsonResponse

from django.shortcuts import get_object_or_404

def update_date_ajax(request):
    if request.method == 'POST':
        pk = request.POST.get('request_id')
        new_date = request.POST.get('new_date')
        mode = request.POST.get('mode') 

        obj = get_object_or_404(SolarInstallationRequest, pk=pk)
        
        if obj.is_deleted:
            return JsonResponse({'success': False, 'error': 'Request is deleted'}, status=403)

        
        
        # Check for "investigation" exactly as sent by JS
        if mode == "investigation":
            obj.preferred_date = new_date
            if obj.status == 'pending':
                obj.status = 'investigation_scheduled'
            # messages.success(request, f"Investigation scheduled for {new_date}")
            
        elif mode == "approve_with_date":
            # Logic: Set installation date AND move status to approved
            obj.installation_date = new_date
            obj.status = 'approved'
            # messages.success(request, f"Request #{pk} approved and scheduled for installation on {new_date}.")
            
        elif mode == "reschedule":
            # If already approved/completed, reschedule installation, otherwise investigation
            if obj.status in ['approved', 'completed']:
                obj.installation_date = new_date
            else:
                obj.preferred_date = new_date
            # messages.success(request, "Date updated successfully.")
        
        obj.save()

        return JsonResponse({
            'success': True,
            'request_id': pk,
            'new_date': new_date,
            'new_status': obj.get_status_display(),
            'status_slug': obj.status 
        })
    
    return JsonResponse({'success': False}, status=400)


def installation_history(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    # Fetch all requests for this user, newest first
    # Optimization: use select_related if 'estimation' is used in the template
    # Optimization: Use select_related to join the InstallationPayment table
    history = SolarInstallationRequest.objects.filter(
        user_id=user_id, 
        is_deleted=False
    ).select_related('installationpayment').order_by('-created_at')
    return render(request, 'installation_history.html', {'history': history})

def manage_installation_request_with_reason(request):
    if request.method == "POST":
        request_id = request.POST.get('request_id')
        status = request.POST.get('status')
        feedback = request.POST.get('feedback')
        # VALIDATION STEP
        if not feedback:
            return JsonResponse({
                "success": False, 
                "error": "Please provide a reason for the rejection."
            }, status=400)
        
        install_req = get_object_or_404(SolarInstallationRequest, id=request_id)
        install_req.status = status
        if status == 'rejected':
            install_req.admin_feedback = feedback
        install_req.save()
        
        return JsonResponse({'success': True}) # or redirect


from django.shortcuts import render, redirect
from .models import Product
from django.contrib import messages

def add_product(request):
    admin_id = request.session.get('official_id')
    if not admin_id:
        return redirect('admin_login')

    if request.method == "POST":
        # Capture Standard Professional Fields
        efficiency = request.POST.get('efficiency')
        warranty = request.POST.get('warranty_years') or 0
        description_data = request.POST.get('description', '') # Get the data from the form
        
        # Build the Product Object
        # Standard fields
        p = Product(
            name=request.POST.get('name'),
            brand=request.POST.get('brand'),
            utility_group=request.POST.get('utility_group'),
            category=request.POST.get('category'),
            price=request.POST.get('price'),
            stock_quantity=request.POST.get('stock', 0),
            efficiency=efficiency,
            warranty_years=warranty,
            image=request.FILES.get('image'),
            description=description_data, # This prevents the NOT NULL error
            model_no=request.POST.get('model_no'),
            country_of_origin=request.POST.get('country_of_origin'),
            highlights=request.POST.get('highlights'),
        )

        # Logic to pack dynamic specs based on category
        specs = {}

        # Global Measurement Specs (Important for all professional items)
        specs['Dimensions'] = request.POST.get('dimensions')
        specs['Rating'] = request.POST.get('rating')
        specs['Voltage'] = request.POST.get('voltage')
        if p.category == 'panel':
            specs['Material'] = request.POST.get('spec_material')
            specs['Cells'] = request.POST.get('spec_cells')
            specs['Voc'] = request.POST.get('spec_voc')
            specs['Isc'] = request.POST.get('spec_isc')
        elif p.category == 'inverter':
            specs['Inverter Type'] = request.POST.get('spec_inverter_type')
            specs['Waveform'] = request.POST.get('spec_waveform')
            specs['Max PV Input'] = request.POST.get('spec_max_pv')
            specs['Max Charge Current'] = request.POST.get('spec_charge_curr')
            specs['Weight'] = request.POST.get('weight')
            specs['Battery Included'] = request.POST.get('spec_battery_included', 'No')
            specs['Typical Load/Backup'] = request.POST.get('spec_backup_desc')
        
        elif p.category == 'battery':
            specs['Battery Type'] = request.POST.get('spec_battery_type')
            specs['Capacity'] = request.POST.get('spec_battery_capacity')
            specs['Voltage'] = request.POST.get('spec_battery_voltage')
            specs['Cycle Life'] = request.POST.get('spec_battery_cycle')
            specs['Warranty'] = request.POST.get('spec_battery_warranty')

        elif p.category == 'mppt':
            specs['Max PV Voltage'] = request.POST.get('spec_mppt_pv_voltage')
            specs['Charging Current'] = request.POST.get('spec_mppt_current')
            specs['Tracking Efficiency'] = request.POST.get('spec_mppt_efficiency')
            specs['Battery Type'] = request.POST.get('spec_mppt_battery')
            specs['Cooling'] = request.POST.get('spec_mppt_cooling')

        elif p.category == 'protection':
            specs['Protection Type'] = request.POST.get('spec_protection_type')
            specs['Rated Current'] = request.POST.get('spec_protection_current')
            specs['Voltage Rating'] = request.POST.get('spec_protection_voltage')
            specs['Poles'] = request.POST.get('spec_protection_poles')
            specs['IP Rating'] = request.POST.get('spec_protection_ip')

        elif p.category == 'structure':
            specs['Material'] = request.POST.get('spec_structure_material')
            specs['Mount Type'] = request.POST.get('spec_structure_type')
            specs['Wind Resistance'] = request.POST.get('spec_structure_wind')

        elif p.category == 'heater':
            specs['Tank Capacity'] = request.POST.get('spec_heater_capacity')
            specs['Collector Type'] = request.POST.get('spec_heater_collector')
            specs['Tank Material'] = request.POST.get('spec_heater_material')
            specs['Insulation'] = request.POST.get('spec_heater_insulation')
            specs['Max Temperature'] = request.POST.get('spec_heater_temp')

        elif p.category in ['light', 'fan', 'pump']:
            specs['Wattage'] = request.POST.get('spec_wattage')
            specs['Backup'] = request.POST.get('spec_backup')
            specs['Operating Voltage'] = request.POST.get('spec_appliance_voltage')
            specs['Application Area'] = request.POST.get('spec_application')
            specs['Body Material'] = request.POST.get('spec_body_material')
        
        p.technical_specs = specs
        p.save()

        # messages.success(request, f"Successfully added {p.name} to Rayn Solar.")
        return redirect('admin_dashboard')

    return render(request, 'add_product.html', {
        'product_categories': Product.CATEGORY_CHOICES,
        'utility_groups': Product.UTILITY_GROUPS,
        'edit_mode': False
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Product

def update_stock(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        new_stock = request.POST.get('stock_quantity')
        
        if new_stock is not None:
            product.stock_quantity = new_stock
            product.save()
            # messages.success(request, f"Stock updated for {product.name}.")
            
    # Redirects back to the page the user was on
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))


from django.contrib import messages

def remove_product_admin(request, pk):
    admin_id = request.session.get('official_id')
    if not admin_id:
        return redirect('admin_login')
    # Security check for admin session
    admin_id = request.session.get('official_id')
    if not admin_id:
        return redirect('admin_login')
    
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    
    # Cascade delete happens automatically here
    product.delete()
    
    # messages.success(request, f"Product '{product_name}' has been completely removed from inventory and user carts.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))


def edit_product(request, pk):
    if 'official_id' not in request.session:
        return redirect('admin_login')
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":

        product.name = request.POST.get('name')
        product.brand = request.POST.get('brand')
        product.utility_group = request.POST.get('utility_group')
        product.category = request.POST.get('category')

        product.price = request.POST.get('price')
        product.stock_quantity = request.POST.get('stock', 0)

        product.efficiency = request.POST.get('efficiency')
        product.warranty_years = request.POST.get('warranty_years') or 0

        product.description = request.POST.get('description')
        product.model_no = request.POST.get('model_no')
        product.country_of_origin = request.POST.get('country_of_origin')
        product.highlights = request.POST.get('highlights')

        # Image update only if new image uploaded
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        # Technical Specs
        specs = {}

        specs['Dimensions'] = request.POST.get('dimensions')
        specs['Voltage'] = request.POST.get('voltage')
        specs['Rating'] = request.POST.get('rating')
        if product.category == 'panel':
            specs['Material'] = request.POST.get('spec_material')
            specs['Cells'] = request.POST.get('spec_cells')
            specs['Voc'] = request.POST.get('spec_voc')
            specs['Isc'] = request.POST.get('spec_isc')

        elif product.category == 'inverter':
            specs['Inverter Type'] = request.POST.get('spec_inverter_type')
            specs['Waveform'] = request.POST.get('spec_waveform')
            specs['Max PV Input'] = request.POST.get('spec_max_pv')
            specs['Max Charge Current'] = request.POST.get('spec_charge_curr')
            specs['Battery Included'] = request.POST.get('spec_battery_included')
            specs['Typical Load/Backup'] = request.POST.get('spec_backup_desc')
            specs['Weight'] = request.POST.get('weight')

        elif product.category == 'battery':
            specs['Battery Type'] = request.POST.get('spec_battery_type')
            specs['Capacity'] = request.POST.get('spec_battery_capacity')
            specs['Voltage'] = request.POST.get('spec_battery_voltage')
            specs['Cycle Life'] = request.POST.get('spec_battery_cycle')
            specs['Warranty'] = request.POST.get('spec_battery_warranty')
            
        elif product.category == 'mppt':
            specs['Max PV Voltage'] = request.POST.get('spec_mppt_pv_voltage')
            specs['Charging Current'] = request.POST.get('spec_mppt_current')
            specs['Battery Type'] = request.POST.get('spec_mppt_battery')            
            specs['Tracking Efficiency'] = request.POST.get('spec_mppt_efficiency')
            specs['Cooling'] = request.POST.get('spec_mppt_cooling')

        elif product.category == 'protection':
            specs['Protection Type'] = request.POST.get('spec_protection_type')
            specs['Rated Current'] = request.POST.get('spec_protection_current')
            specs['Voltage Rating'] = request.POST.get('spec_protection_voltage')
            specs['Poles'] = request.POST.get('spec_protection_poles')
            specs['IP Rating'] = request.POST.get('spec_protection_ip')

        elif product.category == 'structure':
            specs['Material'] = request.POST.get('spec_structure_material')
            specs['Mount Type'] = request.POST.get('spec_structure_type')
            specs['Wind Resistance'] = request.POST.get('spec_structure_wind')

        elif product.category == 'heater':
            specs['Tank Capacity'] = request.POST.get('spec_heater_capacity')
            specs['Collector Type'] = request.POST.get('spec_heater_collector')
            specs['Tank Material'] = request.POST.get('spec_heater_material')
            specs['Insulation'] = request.POST.get('spec_heater_insulation')
            specs['Max Temperature'] = request.POST.get('spec_heater_temp')

        elif product.category in ['light', 'fan', 'pump']:
            specs['Wattage'] = request.POST.get('spec_wattage')
            specs['Backup'] = request.POST.get('spec_backup')
            specs['Operating Voltage'] = request.POST.get('spec_appliance_voltage')
            specs['Application Area'] = request.POST.get('spec_application')
            specs['Body Material'] = request.POST.get('spec_body_material')

        product.technical_specs = specs

        product.save()

        # messages.success(request, "Product updated successfully.")
        return redirect('admin_dashboard')

    return render(request, 'add_product.html', {
        'product': product,
        'product_categories': Product.CATEGORY_CHOICES,
        'utility_groups': Product.UTILITY_GROUPS,
        'edit_mode': True
    })

from django.shortcuts import render
from .models import Product

def product_marketplace(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
    selected_category = request.GET.get('category')
    
    if selected_category:
        products = Product.objects.filter(category=selected_category).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')

    context = {
        'products': products,
        'categories': Product.CATEGORY_CHOICES,
        'selected_category': selected_category,
    }
    return render(request, 'marketplace.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Product

# view to let users see the product details
def product_detail(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
    current_user = get_object_or_404(user, id=user_id)
    product = get_object_or_404(Product, pk=pk)

    # Check if this specific product is already in the user's cart
    in_cart = CartItem.objects.filter(user=current_user, product=product).exists()
    context = {
        'product': product,
        'in_cart': in_cart  # This will be True or False
    }
    return render(request, 'product_detail.html', context)





from .models import Product, CartItem, user # Ensure 'user' is your custom model

def add_to_cart(request, product_id):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    current_user = get_object_or_404(user, id=user_id)
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=current_user,
        product=product,
        defaults={'price': product.price, 'total_price': product.price}
    )

    if not created:
        if cart_item.quantity < product.stock_quantity:   #  max limit
            cart_item.quantity += 1
            cart_item.save()

    return redirect('view_cart')

from .models import ShippingAddress

def view_cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
        
    # Get the actual object from your custom user model
    current_user = get_object_or_404(user, id=user_id)
    cart_items = CartItem.objects.filter(user=current_user)
    total = sum(item.total_price for item in cart_items)
    # Check if user has a shipping address
    address = ShippingAddress.objects.filter(user=current_user).first()
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total, 'address': address})

def remove_from_cart(request, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
        
    current_user = get_object_or_404(user, id=user_id)
    
    # Ensure the item belongs to the session user
    cart_item = get_object_or_404(CartItem, id=item_id, user=current_user)
    cart_item.delete()
    return redirect('view_cart')

def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if cart_item.quantity < cart_item.product.stock_quantity:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')

def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

    return redirect('view_cart')

def add_address(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
    
    current_user = get_object_or_404(user, id=user_id)
    # Get existing address or None
    address = ShippingAddress.objects.filter(user=current_user).first()

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')

        # Update existing or create new
        ShippingAddress.objects.update_or_create(
            user=current_user,
            defaults={
                'full_name': full_name,
                'phone': phone,
                'address_line': address_line,
                'city': city,
                'pincode': pincode
            }
        )
        return redirect('view_cart')

    return render(request, 'add_address.html', {'address': address})
    
from .models import Product_payment

def checkout(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    current_user = get_object_or_404(user, id=user_id)
    cart_items = CartItem.objects.filter(user=current_user)

    if not cart_items:
        return redirect('view_cart')
    
    # Remove any existing 'Pending' payments for this user to avoid duplicates 
    # if they click checkout multiple times without paying.
    Product_payment.objects.filter(user=current_user, payment_status='Pending').delete()

    # Save each cart item as a separate payment row
    for item in cart_items:
        models.Product_payment.objects.create(
            user=current_user,
            product=item.product,
            quantity=item.quantity,
            price=item.price,
            total_price=item.total_price,
            payment_status='Pending'
        )

    return redirect('payment_page')

def payment_page(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('user_login')

    current_user = get_object_or_404(user, id=user_id)

    payments = models.Product_payment.objects.filter(
        user=current_user,
        payment_status='Pending'
    )

    total = sum(p.total_price for p in payments)

    return render(request, 'payment.html', {
        'payments': payments,
        'total': total
    })
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction # Import transaction for safety

from django.utils import timezone
from django.contrib import messages  # Highly recommended for sending user alerts

def process_payment(request):
    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        
        # --- BACKEND VALIDATION GUARD RAILS ---
        if payment_method == 'upi':
            upi_id = request.POST.get('upi_id')
            if not upi_id or not upi_id.strip():
                return HttpResponse("Bad Request: UPI ID is required.", status=400)
                
        elif payment_method == 'card':
            # Note: Card numbers shouldn't touch your main DB tables untreated, 
            # but for dummy structure prototyping check that values exist.
            expiry = request.POST.get('expiry')
            cvv = request.POST.get('cvv')
            if not expiry or not cvv:
                return HttpResponse("Bad Request: Incomplete Card credentials.", status=400)
                
        elif payment_method == 'netbanking':
            bank_name = request.POST.get('bank_name')
            if not bank_name:
                return HttpResponse("Bad Request: Please select a supporting bank core.", status=400)
        else:
            return HttpResponse("Bad Request: Invalid payment mechanism specified.", status=400)
        # --------------------------------------

        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('user_login')

        current_user = get_object_or_404(user, id=user_id)

        payments = Product_payment.objects.filter(
            user=current_user,
            payment_status='Pending'
        )

        if not payments.exists():
            return redirect('payment_page')

        paid_ids = []  
        with transaction.atomic(): 
            for p in payments:
                product = p.product
                product.refresh_from_db()

                if product.stock_quantity < p.quantity:
                    return HttpResponse(f"{product.name} is out of stock")

                Product.objects.filter(id=product.id).update(
                    stock_quantity=F('stock_quantity') - p.quantity
                )
                p.payment_method = payment_method
                # If UPI method, save it; otherwise save fallback/null metadata
                p.upi_id = request.POST.get('upi_id') if payment_method == 'upi' else None
                p.payment_status = 'Success'
                p.paid_at = timezone.now()
                p.save()

                paid_ids.append(p.id)  

        CartItem.objects.filter(user=current_user).delete()
        request.session['paid_payment_ids'] = paid_ids

        return redirect('payment_success')

    return redirect('payment_page')


def payment_success(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    # 1. Grab the IDs from the session
    paid_ids = request.session.get('paid_payment_ids', [])

    # 2. CRITICAL BOUNCE: If they hit back or refresh, these IDs won't exist anymore
    if not paid_ids:
        return redirect('product_marketplace')  # Or your specific home/marketplace page

    # 3. Fetch data for this single execution display
    payments = Product_payment.objects.filter(id__in=paid_ids)
    total = sum(p.total_price for p in payments)

    # 4. CLEAR THE SESSION FLAG RIGHT NOW so the next hit fails safely
    if 'paid_payment_ids' in request.session:
        del request.session['paid_payment_ids']

    return render(request, 'payment_success.html', {
        'payments': payments,
        'total': total
    })

from django.shortcuts import render, redirect
from .models import Product_payment

def product_orders(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    orders = Product_payment.objects.filter(
        user_id=user_id,
        payment_status='Success'
    ).order_by('-created_at')

    return render(request, 'product_orders.html', {'orders': orders})



from django.shortcuts import render, redirect, get_object_or_404
from .models import SolarInstallationRequest, InstallationPayment

# STEP 1: PAY NOW (create pending payment)
def pay_installation(request, pk):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')

    installation_request = get_object_or_404(SolarInstallationRequest, id=pk)
    if installation_request.status != 'completed':
        # messages.error(request, "Payment is only available after your installation has been completed.")
        return redirect('installation_history')
    payment, created = InstallationPayment.objects.get_or_create(
        installation_request=installation_request,
        defaults={
            'user_id': user_id,
            'amount': installation_request.installation_amount or 0,
            'status': 'pending'
        }
    )

    return redirect('installation_order_success', payment_id=payment.id)

# STEP 2: SUCCESS PAGE (before confirmation)
def installation_order_success(request, payment_id):
    payment = get_object_or_404(InstallationPayment, id=payment_id)
    return render(request, 'installation_order_success.html', {'payment': payment})


# STEP 3: CONFIRM PAYMENT
def confirm_installation_payment(request, payment_id):
    payment = get_object_or_404(InstallationPayment, id=payment_id)

    if request.method == 'POST':
       # 1. Capture the selected method
        method = request.POST.get('payment_method')
        payment.payment_method = method

        # 2. Capture the specific details based on the method
        if method == 'upi':
            payment.transaction_details = request.POST.get('upi_id')
        elif method == 'netbanking':
            payment.transaction_details = request.POST.get('bank_name')
        elif method == 'card':
            payment.transaction_details = "Card Payment" # We don't save card numbers for security
            
        payment.status = 'paid'
        payment.paid_at = timezone.now()
        payment.save()
        
        # Now redirect to the final success page (Step 4)
        return redirect('installation_payment_success', payment.id)
    
    # Fallback if accessed via GET
    return redirect('installation_order_success', payment.id)


# STEP 4: FINAL SUCCESS PAGE
def installation_payment_success(request, payment_id):
    payment = get_object_or_404(InstallationPayment, id=payment_id)
    return render(request, 'installation_payment_success.html', {'payment': payment})


#reciept for installation payment
def render_installation_receipt(request, payment_id):
    # Fetch the payment record using the ID provided in the URL
    payment = get_object_or_404(InstallationPayment, id=payment_id)
    #Fetch the user details from your custom table using the ID
    # 'payment.user_id' stores the integer ID of your custom user
    customer = get_object_or_404(models.user, id=payment.user_id)
    # Render the specific installation receipt template
    return render(request, 'receipt_installation_payment.html', {'payment': payment, 'customer_name': customer.full_name,'customer_email': customer.email})

from django.shortcuts import render, get_object_or_404
from .models import Product, Product_payment

def product_transactions(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Fetch all successful payments for this product
    transactions = Product_payment.objects.filter(product=product, payment_status='Success').order_by('-created_at')
    
    context = {
        'product': product,
        'transactions': transactions
    }
    return render(request, 'product_transactions.html', context)


