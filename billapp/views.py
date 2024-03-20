from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.models import auth
from django.utils.crypto import get_random_string
import random
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.http.response import JsonResponse
from billapp.models import Company,Employee,Party,Item,Unit,ItemTransactions,ItemTransactionsHistory,DebitNote
import logging
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.template.loader import render_to_string
import json
import base64
from django.core.mail import EmailMessage
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt




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
            log_user = auth.authenticate(username=usr.username, password=cpass)

            if log_user is not None:
                if usr.is_company == 1:
                    # For company user, set company_id in the session
                    request.session['company'] = usr.id
                else:
                    try:
                        emp = Employee.objects.get(user=usr)
                        if emp.is_approved == 0:
                            messages.info(request, 'Employee is not Approved !!')
                            return redirect('login')
                        else:
                            # For employee user, set company_id in the session
                            request.session['company'] = emp.company.id if emp.company else None
                    except Employee.DoesNotExist:
                        # Handle the case where the user is not an employee
                        request.session['company'] = None

                # Set user_id in the session
                request.session['user'] = usr.id

                auth.login(request, log_user)
                return redirect('dashboard')

            messages.info(request, 'Invalid Login Details !!')
            return redirect('login')

        except CustomUser.DoesNotExist:
            messages.info(request, 'User does not exist !!')
            return redirect('login')

    return render(request, 'login.html')











#####SECOND ONE CHANGED ON 18/01/2024#####
# def user_login(request):
#   if request.method == 'POST':
#     email = request.POST['email']
#     cpass = request.POST['pass']

#     try:
#       usr = CustomUser.objects.get(email=email)
#       log_user = auth.authenticate(username = usr.username, password = cpass)
#       if log_user is not None:
#         if usr.is_company == 1:
#           auth.login(request, log_user)
#           return redirect('dashboard')
#         else:
#           emp = Employee.objects.get(user=usr)
#           if emp.is_approved == 0:
#             messages.info(request,'Employee is not Approved !!')
#             return redirect('login')
#           else:
#             auth.login(request, log_user)
#             return redirect('dashboard')
#       messages.info(request,'Invalid Login Details !!')
#       return redirect('login')
    
#     except:
#         messages.info(request,'Employee do not exist !!')
#         return redirect('login')
    
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


logger = logging.getLogger(__name__)

def debit_note_redirect(request):
    # Check if any debit notes exist for the logged-in user or company
    debit_notes_exist = DebitNote.objects.filter(user=request.user).exists() or \
                        DebitNote.objects.filter(company=request.user.company).exists()

    if debit_notes_exist:
        # Debit notes exist, redirect to the page displaying the debit notes
        return redirect('debitnote2')  # Adjust the URL name as per your project

    else:
        # No debit notes exist, redirect to the page for creating the first debit note
        return redirect('firstdebitnote') 
    
def createdebitnote(request):
    
    # Fetch the company based on the user's role
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company

    parties = Party.objects.filter(company=cmp)
    bills = PurchaseBill.objects.filter(company=cmp)
    unit = Unit.objects.filter(company=cmp)

    items = Item.objects.filter(company=cmp)

    context = {
        'usr': request.user,
        'parties': parties,
        'bills': bills,
        'items': items,
        'units': unit,
        'company_id': cmp.id,  # Pass company_id to the template
    }

    if request.method == 'POST':
        user_id = request.session.get('user')

        if user_id is None:
            return JsonResponse({'status': 'error', 'message': 'User ID not available'})

        try:
            party_id = request.POST.get('party')
            bill_id = request.POST.get('bill')
            
            # Assuming that a Party has a ForeignKey to PurchaseBill
            selected_party = get_object_or_404(Party, id=party_id)
            selected_bill = get_object_or_404(PurchaseBill, id=bill_id)
            
            # Assuming that PurchaseBill has a ForeignKey to Item
            # Assuming Party has a ForeignKey to PurchaseBill
            selected_item = selected_party.purchasebill_set.first().item  # Adjust this line based on your model structure

            # Create a DebitNote instance
            debit_note = DebitNote.objects.create(party=selected_party, bill=selected_bill, user=request.user, company=cmp)

            # Retrieve the created DebitNote instance based on its ID
            debit_note_instance = get_object_or_404(DebitNote, id=debit_note.id)

            # Now you can get the tax rate from the Item instance using the get_vat_integer method
            taxRate = selected_item.get_vat_integer()

            return render(request, 'createdebitnote.html', {
                'usr': request.user,
                'parties': parties,
                'bills': bills,
                'selected_party': selected_party,
                'selected_bill': selected_bill,
                'selected_item': selected_item,  # Pass the selected Item instance
                'items': items,
                'company_id': cmp.id,
                'debit_note_instance': debit_note_instance,
                'taxRate': taxRate,
            })

        except Exception as e:
            # Log the exception
            logger.error(f"Error in createdebitnote view: {str(e)}")

            # Return an error response
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing the request'})

    return render(request, 'createdebitnote.html', context)

@csrf_exempt
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
        request.session.save()

        parties = Party.objects.filter(company_id=company_id, user_id=user_id)
        data={'name': new_party.party_name, 'id':new_party.id}
        # messages.success(request, 'Party created successfully')
        # response_data = {'success': True, 'message': 'Party created successfully!'}
        # return render(request, 'createdebitnote.html',response_data)
        return JsonResponse({'status': 'success','parties':data})
    else:
        return render(request, 'createdebitnote.html')

def extract_percentage(vat_string):
    # Split the string by space
    parts = vat_string.split()

    # Check if there are at least two parts (e.g., "VAT 5%")
    if len(parts) >= 2:
        # Get the second part and remove the percentage sign
        percentage = parts[1].replace('%', '')

        # Return the numeric value
        return int(percentage)

    # Return None if the string doesn't match the expected format
    return None

def item_create(request):
    if request.method == 'POST':
        
        itm_type = request.POST.get('itm_type')
        itm_name = request.POST.get('name')
        itm_hsn = request.POST.get('hsn')
        itm_unit = request.POST.get('unit')
        itm_taxable = request.POST.get('taxable_result')
        
        print(request.POST.get('vat'))
        itm_vat = extract_percentage(request.POST.get('vat'))
        
        itm_sale_price = request.POST.get('sale_price')
        itm_purchase_price = request.POST.get('purchase_price')
        itm_stock_in_hand = request.POST.get('stock_in_hand')
        itm_at_price = request.POST.get('at_price')
        itm_date = request.POST.get('itm_date')

        item = Item(
            user=request.user,
            company=request.user.company,
            itm_type=itm_type,
            itm_name=itm_name,
            itm_hsn=itm_hsn,
            itm_unit=itm_unit,
            itm_taxable=itm_taxable,
            itm_vat=itm_vat,
            itm_sale_price=itm_sale_price,
            itm_purchase_price=itm_purchase_price,
            itm_stock_in_hand=itm_stock_in_hand,
            itm_at_price=itm_at_price,
            itm_date=itm_date
        )
        item.save()
        response_data = {'success': True, 'message': 'Item created successfully!'}
        return render(request, 'createdebitnote.html',response_data)


    return render(request, 'createdebitnote.html')



def create_unit(request):
    if request.method == 'POST':
        unit_name = request.POST.get('unit_name', '')
        company_id = request.user.company.id
        print(f"Company ID: {company_id}")

        
        company = Company.objects.get(id=request.user.company.id)

        # Create a new Unit instance
        unit = Unit.objects.create(
            company=company,
            unit_name=unit_name
        )
        messages.success(request, 'Unit created successfully')
        context = {'success': True,'message': 'Unit created successfully!', 'unit_name': unit.unit_name}
        print("Context:", context)

        return render(request, 'createdebitnote.html', context)

    # Handle other HTTP methods if needed
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def save_debit_note(request):
    company_id = request.session.get('company')
    user_id = request.session.get('user')

    if request.method == 'POST':
        party_id = request.POST.get('party')
        return_no = request.POST.get('return_no')
        current_date = request.POST.get('current-date1') 
        subtotal = request.POST.get('subtotal')
        tax_amount = request.POST.get('taxAmount')
        adjustment = request.POST.get('adjustment')
        grand_total = request.POST.get('grandTotal')

        selected_party = Party.objects.get(id=party_id)

        debit_note = DebitNote.objects.create(
            user=request.user,
            company_id=company_id, 
            party=selected_party,
            returnno=return_no,
            created_at=current_date
        )

        # Save to DebitNoteHistory
        DebitNoteHistory.objects.create(
            user=request.user,
            company_id=company_id,
            debit_note=debit_note,
            date=timezone.now(),  # Use current timestamp
            action='C'  # 'C' for created
        )

        items = request.POST.getlist("selected_item[]")
        quantities = request.POST.getlist("item_quantity[]")
        discounts = request.POST.getlist("item_discount[]")
        total_amounts = request.POST.getlist("item_total_amount[]")

        for item, qty, discount, total_amount in zip(items, quantities, discounts, total_amounts):
            itm = Item.objects.get(id=item)
            DebitNoteItem.objects.create(
                user=request.user,
                company_id=company_id,  
                debitnote=debit_note,
                items=itm,
                qty=qty,
                discount=discount,
                total=total_amount
            )

        debit_note.subtotal = subtotal
        debit_note.taxamount = tax_amount
        debit_note.adjustment = adjustment
        debit_note.grandtotal = grand_total
        debit_note.save()

        return redirect('debitnote2')  

    parties = Party.objects.filter(company_id=company_id)  
    items = Item.objects.filter(company_id=company_id)  
    debits = DebitNote.objects.filter(user=request.user).prefetch_related('debitnotehistory_set')
    
    # Pass necessary data to the template context
    context = {
        'parties': parties,
        'items': items,
        'debits': debits,
        'company_id': company_id,
        'user_id': user_id,
        'usr': request.user  # Pass the user object to the template
    }
    return render(request, 'debitnote2.html', context)



def debitnote2(request):
    company_id = request.session.get('company')
    user_id = request.session.get('user')

    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company

    parties = Party.objects.filter(company=cmp)
    items = Item.objects.filter(company=cmp)
    debits = DebitNote.objects.filter(user=request.user).prefetch_related('debitnotehistory_set')

    # Pass necessary data to the template context
    context = {
        'parties': parties,
        'items': items,
        'debits': debits,
        'company_id': company_id,
        'user_id': user_id,
        'usr': request.user  # Pass the user object to the template
    }
    return render(request, 'debitnote2.html', context)


def delete_debit_note(request, debitnote_id):
    if request.method == 'POST':
        try:
            # Retrieve the DebitNote object to be deleted
            debit_note = get_object_or_404(DebitNote, id=debitnote_id)
            
            # Delete related DebitNoteItem objects
            debit_note.debitnoteitem_set.all().delete()

            # Delete the DebitNote object
            debit_note.delete()

            # Return a success response
            return JsonResponse({'status': 'success'})

        except Exception as e:
            # If any error occurs, return an error response
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        # If the request method is not POST, return a method not allowed response
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
  
def search_debitnotes(request):
    if request.method == 'GET':
        fromDate_str = request.GET.get('fromDate')
        toDate_str = request.GET.get('toDate')

       
        fromDate = timezone.make_aware(datetime.strptime(fromDate_str, '%Y-%m-%d'))
        toDate = timezone.make_aware(datetime.strptime(toDate_str, '%Y-%m-%d'))

 
        debitnotes = DebitNote.objects.filter(created_at__range=[fromDate, toDate])

        
        debitnotes_list = list(debitnotes.values())

        
        return JsonResponse(debitnotes_list, safe=False)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    


def delete_debit_note_item(request, debitnote_id):
    debit_note_item = get_object_or_404(DebitNote, pk=debitnote_id)
    debit_note_item.delete()
    return JsonResponse({'message': 'Debit note item deleted successfully'})




def edit_debit_note(request, debit_id):
    company_id = request.session.get('company')
    user_id = request.session.get('user')

    debitnote = get_object_or_404(DebitNote, id=debit_id)

    if request.method == 'POST':
        party_id = request.POST.get('party')
        return_no = request.POST.get('return_no')
        current_date = request.POST.get('current-date') 
        subtotal = request.POST.get('subtotal')
        tax_amount = request.POST.get('taxAmount')
        adjustment = request.POST.get('adjustment')
        grand_total = request.POST.get('grandTotal')

        selected_party = Party.objects.get(id=party_id)

        # Update debit note fields
        debitnote.party = selected_party
        debitnote.returnno = return_no
        debitnote.created_at = current_date
        debitnote.subtotal = subtotal
        debitnote.taxamount = tax_amount
        debitnote.adjustment = adjustment
        debitnote.grandtotal = grand_total
        debitnote.save()

        # Update debit note items
        items = request.POST.getlist("selected_item[]")
        quantities = request.POST.getlist("item_quantity[]")
        discounts = request.POST.getlist("item_discount[]")
        total_amounts = request.POST.getlist("item_total_amount[]")

        # Clear existing debit note items
        debitnote.debitnoteitem_set.all().delete()

        for item, qty, discount, total_amount in zip(items, quantities, discounts, total_amounts):
            itm = Item.objects.get(id=item)
            DebitNoteItem.objects.create(
                user=request.user,
                company_id=company_id,  
                debitnote=debitnote,
                items=itm,
                qty=qty,
                discount=discount,
                total=total_amount,
                
            )

        # Log the update action
        DebitNoteHistory.objects.create(
            user=request.user,
            company_id=company_id,
            debit_note=debitnote,
            date=timezone.now(),  # Use current timestamp
            action='Updated'
        )

        return redirect('debitnote2')  # Redirect to debit note list page or any other desired page

    else:  # Handling GET request
        parties = Party.objects.filter(company_id=company_id)  
        items = Item.objects.filter(company_id=company_id)  
        debits = DebitNote.objects.filter(user=request.user).prefetch_related('debitnotehistory_set') 
        current_date = debitnote.created_at.strftime('%Y-%m-%d') if debitnote.created_at else timezone.now().strftime('%Y-%m-%d')

        # Get selected items for the debit note
        selected_item = [{
            'id': item.items.id,
            'name': item.items.itm_name,
            'itm_hsn': item.items.itm_hsn,
            'purchaseprice': item.items.itm_purchase_price,
            'vat': item.items.itm_vat,
            'qty': item.qty,
            'discount': item.discount,
            'total_amount': item.total
        } for item in debitnote.debitnoteitem_set.all()]

        associated_bill = PurchaseBill.objects.filter(party=debitnote.party).first()

        context = {
            'debitnote': debitnote,
            'parties': parties,
            'items': items,
            'debits': debits,
            'company_id': company_id,
            'user_id': user_id,
            'usr': request.user,
            'selected_party': debitnote.party.id if debitnote.party else None,
            'return_no': debitnote.returnno,
            'current_date':current_date,
            'subtotal': debitnote.subtotal,
            'taxAmount': debitnote.taxamount,
            'adjustment': debitnote.adjustment,
            'grandTotal': debitnote.grandtotal,
            'selected_party_address': debitnote.party.address if debitnote.party else None,
            'selected_party_contact': debitnote.party.contact if debitnote.party else None,
            'selected_party_balance': debitnote.party.openingbalance if debitnote.party else None,
            'billno': associated_bill.billno if associated_bill else None,
            'billdate': associated_bill.billdate if associated_bill else None,
            'selected_item': selected_item,
        }

        return render(request, 'editdebitnote.html', context)

def get_debit_note_history(request, debitnote_id):
    # Query the database for history data associated with the given debitnote_id
    history_data = DebitNoteHistory.objects.filter(debit_note__id=debitnote_id).select_related('debit_note__user').values('debit_note__returnno', 'date', 'user__first_name', 'user__last_name', 'action')

    # Convert queryset to list of dictionaries
    history_data_list = list(history_data)

    # Return the history data as JSON response
    return JsonResponse(history_data_list, safe=False)







def generate_pdf(request, debit_note_id):
    debit_note = DebitNote.objects.get(id=debit_note_id)
    # Fetch related data
    party = debit_note.party
    debit_note_items = debit_note.debitnoteitem_set.all()  # Assuming you have related_name set for ForeignKey
    # Render PDF template with fetched data
    context = {
        'debit_note': debit_note,
        'party': party,
        'debit_note_items': debit_note_items,
    }
    pdf_content = render_to_string('debit_note_pdf_template.html', context)

    # Generate PDF using a library like WeasyPrint or ReportLab (not implemented here)
    # For demonstration purposes, let's assume pdf_content contains the PDF data

    # Return PDF as HttpResponse
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="debit_note_report.pdf"'
    return response



def get_debit_note_details(request, debit_id):
    try:
   
        company_id = request.session.get('company')
        user_id = request.session.get('user')

        if not company_id or not user_id:
            return HttpResponse("Company or User details not found in session.")

        
        if request.user.is_company:
            company = request.user.company
        else:
            company = request.user.employee.company

        debit_note = DebitNote.objects.get(id=debit_id)
        debit_note_items = DebitNoteItem.objects.filter(debitnote=debit_note)

       
        parties = Party.objects.filter(company=company)
        items = Item.objects.filter(company=company)

       
        context = {
            'debit_id': debit_id,
            'company_id': company_id,
            'user_id': user_id,
            'usr': request.user, 
            'company': company,
            'party': debit_note.party,
            'debit_note': debit_note,
            'debit_note_items': debit_note_items,
            'parties': parties,
            'items': items,
        }

     
        return render(request, 'showtemplates.html', context)

    except (DebitNote.DoesNotExist, ValueError):
        # Return a JSON response with an error message if the debit note does not exist or if there's a value error
        return JsonResponse({'error': 'Invalid DebitNote ID'}, status=404)
    
# def share_debit_note_via_email(request, debit_note_id):
    # if request.method == 'POST':
    #     try:
            # Retrieve data from the POST request
            # email = request.POST.get('email')
            # message = request.POST.get('message')
            # pdf_data = request.POST.get('attachment')

            # Check if all required data is provided
            # if not all([email, message, pdf_data]):
            #     return JsonResponse({'status': 'error', 'message': 'Missing required data'}, status=400)

            # Decode the attachment data if needed
            # pdf_data_decoded = base64.b64decode(pdf_data.split(',')[1])

            # Retrieve the debit note object
            # debit_note = DebitNote.objects.get(id=debit_note_id)
            # company = debit_note.company

            # Render HTML template for the debit note
            # context = {
            #     'debit_note': debit_note,
            #     'company': company,
            #     'message': message,
            # }
            # html_content = render_to_string('debit_note_template.html', context)

            # # Create EmailMessage object
            # subject = "Debit Note"
            # from_email = settings.EMAIL_HOST_USER
            # email_message = EmailMessage(
            #     subject,
            #     message,
            #     from_email=from_email,
            #     to=[email]
            # )
            # Attach the PDF file
            # email_message.attach("debit_note.pdf", pdf_data_decoded, 'application/pdf')

            # Send the email
    #         email_message.send(fail_silently=False)

    #         return JsonResponse({'status': 'success', 'message': 'Email sent successfully'})
    #     except DebitNote.DoesNotExist:
    #         return JsonResponse({'status': 'error', 'message': 'Debit note does not exist'}, status=404)
    #     except Exception as e:
    #         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
def share_debit_note_via_email(request, debit_note_id):
    if request.method == 'POST':
        try:
            # Retrieve data from the POST request
            email = request.POST.get('email')
            message = request.POST.get('message')

            # Check if all required data is provided
            if not all([email, message]):
                return JsonResponse({'status': 'error', 'message': 'Missing required data'}, status=400)

            # Retrieve the debit note object
            debit_note = DebitNote.objects.get(id=debit_note_id)
            company = debit_note.company

            # Render HTML template for the debit note
            context = {
                'debit_note': debit_note,
                'company': company,
                'message': message,
            }
            html_content = render_to_string('debit_note_template.html', context)

            # Create EmailMessage object
            subject = "Debit Note"
            from_email = settings.EMAIL_HOST_USER
            email_message = EmailMessage(
                subject,
                message,
                from_email=from_email,
                to=[email]
            )

            # Attach HTML content as alternative content (no PDF attachment)
            email_message.attach_alternative(html_content, 'text/html')

            # Send the email
            email_message.send(fail_silently=False)

            return JsonResponse({'status': 'success', 'message': 'Email sent successfully'})
        except DebitNote.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Debit note does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)