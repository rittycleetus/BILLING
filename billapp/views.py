from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.models import auth
from django.utils.crypto import get_random_string
import random
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.http.response import JsonResponse
from billapp.models import Company,Employee,Party,Item,Unit,ItemTransactions,ItemTransactionsHistory

def home(request):
  return render(request, 'home.html')

def login(request):
  return render(request, 'login.html')

def forgot_password(request):
  return render(request, 'forgot_password.html')

def cmp_register(request):
  return render(request, 'cmp_register.html')

def cmp_details(request,id):
  context = {'id':id}
  return render(request, 'cmp_details.html', context)

def emp_register(request):
  return render(request, 'emp_register.html')

def register_company(request):
  if request.method == 'POST':
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    uname = request.POST['uname']
    phno = request.POST['phno']
    passw = request.POST['pass']
    cpass = request.POST['cpass']
    rfile = request.FILES.get('rfile')

    if passw == cpass:
      if CustomUser.objects.filter(username = uname).exists():
        messages.info(request, 'Sorry, Username already in Use !!')
        return redirect('cmp_register')
      
      elif Company.objects.filter(contact = phno).exists():
        messages.info(request, 'Sorry, Phone Number already in Use !!')
        return redirect('cmp_register')

      elif not CustomUser.objects.filter(email = email).exists():
        user_data = CustomUser.objects.create_user(first_name = fname, last_name = lname, username = uname, email = email, password = passw, is_company = 1)
        cmp = Company( contact = phno, user = user_data, profile_pic = rfile)
        cmp.save()
        return redirect('cmp_details',user_data.id)

      else:
        messages.info(request, 'Sorry, Email already in Use !!')
        return redirect('cmp_register')
      
    messages.info(request, 'Sorry, Passwords must match !!')
    return render(request,'cmp_register.html')
  
def register_company_details(request,id):
  if request.method == 'POST':
    cname = request.POST['cname']
    address = request.POST['address']
    city = request.POST['city']
    state = request.POST['state']
    country = request.POST['country']
    pincode = request.POST['pincode']
    pannumber = request.POST['pannumber']
    gsttype = request.POST['gsttype']
    gstno = request.POST['gstno']

    if Company.objects.filter(pan_number = pannumber).exclude(pan_number='').exists():
      messages.info(request, 'Sorry, Pan number is already in Use !!')
      return redirect('cmp_details',id)
    
    if Company.objects.filter(gst_no = gstno).exclude(gst_no='').exists():
      messages.info(request, 'Sorry, GST number is already in Use !!')
      return redirect('cmp_details',id)

    code=get_random_string(length=6)

    usr = CustomUser.objects.get(id = id)
    cust = Company.objects.get(user = usr)
    cust.company_name = cname
    cust.address = address
    cust.city = city
    cust.state = state
    cust.company_code = code
    cust.country = country
    cust.pincode = pincode
    cust.pan_number = pannumber
    cust.gst_type = gsttype
    cust.gst_no = gstno
    cust.save()
    return redirect('login')

def register_employee(request):
  if request.method == 'POST':
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    uname = request.POST['uname']
    phno = request.POST['phno']
    passw = request.POST['pass']
    cpass = request.POST['cpass']
    ccode = request.POST['ccode']
    rfile = request.FILES.get('rfile')

    if not Company.objects.filter(company_code = ccode).exists():
      messages.info(request, 'Sorry, Company Code is Invalid !!')
      return redirect('emp_register')
    
    cmp = Company.objects.get(company_code = ccode)
    emp_names = Employee.objects.filter(company = cmp).values_list('user',flat=True)
    for e in emp_names:
       usr = CustomUser.objects.get(id=e)
       if str(fname).lower() == (usr.first_name ).lower() and str(lname).lower() == (usr.last_name).lower():
        messages.info(request, 'Sorry, Employee With this name already exits, try adding an initial !!')
        return redirect('emp_register')
    
    if passw == cpass:
      if CustomUser.objects.filter(username = uname).exists():
        messages.info(request, 'Sorry, Username already exists !!')
        return redirect('emp_register')
      
      elif Employee.objects.filter(contact = phno).exists():
        messages.info(request, 'Sorry, Phone Number already in Use !!')
        return redirect('emp_register')

      elif not CustomUser.objects.filter(email = email).exists():
        user_data = CustomUser.objects.create_user(first_name = fname, last_name = lname, username = uname, email = email, password = passw)
        emp = Employee(user = user_data, company = cmp, profile_pic = rfile, contact=phno)
        emp.save()
        return redirect('login')

      else:
        messages.info(request, 'Sorry, Email already exists !!')
        return redirect('emp_register')
      
    messages.info(request, 'Sorry, Passwords must match !!')
    return render(request,'emp_register.html')
  
def change_password(request):
  if request.method == 'POST':
    email= request.POST.get('email')
    if not CustomUser.objects.filter(email=email).exists():
      messages.success(request,'Sorry, No user found with this email !!')
      return redirect('forgot_password')
    
    else:
      otp = random.randint(100000, 999999)
      usr = CustomUser.objects.get(email=email)
      usr.set_password(str(otp))
      usr.save()

      subject = 'Password Reset Mail'
      message = f'Hi {usr.first_name} {usr.last_name}, Your Otp for password reset is {otp}'
      email_from = settings.EMAIL_HOST_USER
      recipient_list = [email ]
      send_mail(subject, message, email_from, recipient_list)
      messages.info(request,'Password reset mail sent !!')
      return redirect('forgot_password')

def user_login(request):
  if request.method == 'POST':
    email = request.POST['email']
    cpass = request.POST['pass']

    try:
      usr = CustomUser.objects.get(email=email)
      log_user = auth.authenticate(username = usr.username, password = cpass)
      if log_user is not None:
        if usr.is_company == 1:
          auth.login(request, log_user)
          return redirect('dashboard')
        else:
          emp = Employee.objects.get(user=usr)
          if emp.is_approved == 0:
            messages.info(request,'Employee is not Approved !!')
            return redirect('login')
          else:
            auth.login(request, log_user)
            return redirect('dashboard')
      messages.info(request,'Invalid Login Details !!')
      return redirect('login')
    
    except:
        messages.info(request,'Employee do not exist !!')
        return redirect('login')
    
# def user_login(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['pass']

#         try:
#             user = CustomUser.objects.get(email=email)
#             log_user = auth.authenticate(request, username=user.username, password=password)

#             if log_user is not None:
#                 # Assuming you have 'company_id' and 'user_id' fields in your CustomUser model
#                 request.session['company_id'] = user.company_id
#                 request.session['user_id'] = user.id

#                 auth.login(request, log_user)

#                 if user.is_company == 1:
#                     return redirect('dashboard')
#                 else:
#                     emp = Employee.objects.get(user=user)
#                     if emp.is_approved == 0:
#                         messages.info(request, 'Employee is not Approved !!')
#                         return redirect('login')
#                     else:
#                         return redirect('dashboard')

#             messages.info(request, 'Invalid Login Details !!')
#             return redirect('login')

#         except CustomUser.DoesNotExist:
#             messages.info(request, 'User does not exist !!')
#             return redirect('login')

#     # Render your login template
#     return render(request, 'login.html')

def dashboard(request):
  context = {'usr':request.user}
  return render(request, 'dashboard.html', context)

def logout(request):
  auth.logout(request)
  return redirect('/')

def cmp_profile(request):
  cmp = Company.objects.get(user = request.user)
  context = {'usr':request.user, 'cmp':cmp}
  return render(request,'cmp_profile.html',context)

def load_edit_cmp_profile(request):
  cmp = Company.objects.get(user = request.user)
  context = {'usr':request.user, 'cmp':cmp}
  return render(request,'cmp_profile_edit.html',context)

def edit_cmp_profile(request):
  cmp =  Company.objects.get(user = request.user)
  if request.method == 'POST':
    email = request.POST['email']
    current_email = cmp.user.email
    if email != current_email:
      if CustomUser.objects.filter(email=email).exists():
        messages.info(request,'Sorry, Email Already in Use !!')
        return redirect('load_edit_cmp_profile')
      
    phno_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('contact', flat=True)))
    gst_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('pan_number', flat=True)))
    gno_list = list(filter(None,Company.objects.exclude(user = request.user).values_list('gst_no', flat=True)))

    if request.POST['phno'] in phno_list:
      messages.info(request,'Sorry, Phone number already in Use !!')
      return redirect('load_edit_cmp_profile')

    if request.POST['pan'] in gst_list:
      messages.info(request,'Sorry, PAN number already in Use !!')
      return redirect('load_edit_cmp_profile')

    if request.POST['gstnoval'] in gno_list:
      messages.info(request,'Sorry, GST number already in Use !!')
      return redirect('load_edit_cmp_profile')

    cmp.company_name = request.POST['cname']
    cmp.user.email = request.POST['email']
    cmp.user.first_name = request.POST['fname']
    cmp.user.last_name = request.POST['lname']
    cmp.contact = request.POST['phno']
    cmp.address = request.POST['address']
    cmp.city = request.POST['city']
    cmp.state = request.POST['state']
    cmp.country = request.POST['country']
    cmp.pincode = request.POST['pincode']
    cmp.pan_number = request.POST['pan']
    cmp.gst_type = request.POST['gsttype']
    cmp.gst_no = request.POST['gstnoval']
    old=cmp.profile_pic
    new=request.FILES.get('image')
    if old!=None and new==None:
      cmp.profile_pic=old
    else:
      cmp.profile_pic=new
    
    cmp.save() 
    cmp.user.save() 
    return redirect('cmp_profile') 
  
def emp_profile(request):
  emp = Employee.objects.get(user=request.user)
  context = {'usr':request.user, 'emp':emp}
  return render(request,'emp_profile.html',context)

def load_edit_emp_profile(request):
  emp = Employee.objects.get(user=request.user)
  context = {'usr':request.user, 'emp':emp}
  return render(request,'emp_profile_edit.html',context)

def edit_emp_profile(request):
  emp =  Employee.objects.get(user = request.user)
  if request.method == 'POST':
    email = request.POST['email']
    current_email = emp.user.email
    if email != current_email:
      if CustomUser.objects.filter(email=email).exists():
        messages.info(request,'Email Already in Use')
        return redirect('load_edit_emp_profile')
          
    phno_list = list(Employee.objects.exclude(user = request.user).values_list('contact', flat=True))

    if request.POST['phno'] in phno_list:
      messages.info(request,'Sorry, Phone number already in Use !!')
      return redirect('load_edit_emp_profile')

    emp.user.email = request.POST['email']
    emp.user.first_name = request.POST['fname']
    emp.user.last_name = request.POST['lname']
    emp.contact = request.POST['phno']
    old=emp.profile_pic
    new=request.FILES.get('image')
    if old!=None and new==None:
      emp.profile_pic=old
    else:
      emp.profile_pic=new
    
    emp.save() 
    emp.user.save() 
    return redirect('emp_profile') 

def load_staff_request(request):
  cmp = Company.objects.get(user = request.user)
  emp = Employee.objects.filter(company = cmp, is_approved = 0)
  context = {'usr':request.user, 'emp':emp, 'cmp':cmp}
  return render(request,'staff_request.html',context)

def load_staff_list(request):
  cmp = Company.objects.get(user = request.user)
  emp = Employee.objects.filter(company = cmp, is_approved = 1)
  context = {'usr':request.user, 'emp':emp, 'cmp':cmp}
  return render(request,'staff_list.html',context)

def accept_staff(request,id):
  emp = Employee.objects.get(id=id)
  emp.is_approved = 1
  emp.save()
  messages.info(request,'Employee Approved !!')
  return redirect('load_staff_request')

def reject_staff(request,id):
  emp = Employee.objects.get(id=id)
  emp.user.delete()
  emp.delete()
  messages.info(request,'Employee Deleted !!')
  return redirect('load_staff_request')

def firstdebitnote(request):
    # You may need to fetch data or perform any logic related to the first debit note here
    # For example, check if there are existing debit notes
    debit_notes_exist = True  # Replace this with your actual logic

    context = {
        'usr': request.user,
        'debit_notes_exist': debit_notes_exist,
    }

    return render(request, 'firstdebitnote.html', context)

def createdebitnote(request):
    parties = Party.objects.all()  # Fetch all parties from the database
    bill=PurchaseBill.objects.all()
    context = {'usr': request.user, 'parties': parties,'bill':bill}
    
    if request.method == 'POST':
        # Assuming company_id and user_id are available in the session
        company_id = request.session.get('company_id')
        user_id = request.session.get('user_id')
    
        if company_id is None or user_id is None:
            # Handle the case where company_id or user_id is not available
            return JsonResponse({'status': 'error', 'message': 'Company ID or User ID not available'})
        
        party_id = request.POST.get('party')
        selected_party = Party.objects.get(id=party_id)
        
        # Process the form data for creating a debit note
        # Modify the following lines based on your debit note form data and model
        # debit_note_number = request.POST.get('debit_note_number')
        # amount = request.POST.get('amount')
        # # ... other debit note fields ...

        # Optionally, return the selected party data along with the success status
        return render(request, 'createdebitnote.html', {'usr': request.user, 'parties': parties, 'selected_party': selected_party})
    
    else:
        return render(request, 'createdebitnote.html', context)
    
def create_party(request):
    if request.method == 'POST':
      
        company_id = request.session.get('company')

        user_id = request.session.get('user')
        

      

        
        party_name = request.POST.get('partyname')
        trn_no = request.POST.get('trn_no')
        contact = request.POST.get('contact')
        trn_type = request.POST.get('trn_type')
        state = request.POST.get('state')
        address = request.POST.get('address')
        email = request.POST.get('email')
        openingbalance = request.POST.get('balance')
        payment = request.POST.get('paymentType')
        current_date = request.POST.get('currentdate')
        
       
        
        additionalfield1 = request.POST.get('additionalfield1')
        additionalfield2 = request.POST.get('additionalfield2')
        additionalfield3 = request.POST.get('additionalfield3')

      
        new_party = Party(
            company_id=company_id,
            user_id=user_id,
            party_name=party_name,
            trn_no=trn_no,
            contact=contact,
            trn_type=trn_type,
            state=state,
            address=address,
            email=email,
            openingbalance=openingbalance,
            payment=payment,
           
            current_date=current_date,
            
            additionalfield1=additionalfield1,
            additionalfield2=additionalfield2,
            additionalfield3=additionalfield3,
        )
        new_party.save()

       
        parties = Party.objects.filter(company_id=company_id, user_id=user_id)

        return render(request, 'createdebitnote.html', {'status': 'success', 'message': 'Party created successfully', 'parties': parties})
    else:
      
        return JsonResponse({'status': 'error'})