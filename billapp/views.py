#MultuserbillingVAT
from logging import Logger
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
from datetime import date
from django.db.models import F
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.views.generic import View
from io import BytesIO
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.views import View
import base64
from django.http import JsonResponse
from datetime import datetime,date, timedelta
# from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.db import IntegrityError
import pymysql
from billapp.models import Company,Employee,Party,Item,Unit,ItemTransactions,ItemTransactionsHistory,DebitNote,DebitNoteHistory,DebitNoteItem

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

def item_list_first(request):
  if request.user.is_company:
    itm_list = Item.objects.filter(company = request.user.company)
  else:
    itm_list = Item.objects.filter(company = request.user.employee.company)
  
  if itm_list:
    itm = itm_list[0]
    trans = ItemTransactions.objects.filter(item = itm)
    context = {'itm_list':itm_list, 'usr':request.user, 'itm':itm, 'trans':trans}
  else:
    context = {'itm_list':itm_list, 'usr':request.user}
  return render(request,'item_list.html',context)

def item_list(request,id):
  if request.user.is_company:
    itm_list = Item.objects.filter(company = request.user.company)
  else:
    itm_list = Item.objects.filter(company = request.user.employee.company)
  
  itm = Item.objects.get(id=id)
  trans = ItemTransactions.objects.filter(item=itm.id)
  context = {'itm_list':itm_list, 'usr':request.user, 'itm':itm, 'trans':trans}
  return render(request,'item_list.html',context) 

def load_item_create(request):
  tod = timezone.now().date().strftime("%Y-%m-%d")
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  unit = Unit.objects.filter(company=cmp)
  return render(request,'item_create.html',{'tod':tod, 'usr':request.user, 'unit':unit})

def item_create(request):
  if request.method=='POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company
  
    itm_type = request.POST.get('itm_type')
    itm_name = request.POST.get('name')
    itm_hsn = request.POST.get('hsn')

    if Item.objects.filter(company=cmp,itm_name=itm_name).exists():
      messages.info(request,'Item already registered')
      return redirect('load_item_create')

    if Item.objects.filter(company=cmp,itm_hsn=itm_hsn).exists():
      messages.info(request,'Item with this HSN already registered')
      return redirect('load_item_create')

    itm_unit = request.POST.get('unit')
    itm_vat = request.POST.get('vat')
    taxable_result = request.POST.get('taxable_result')
    itm_sale_price = request.POST.get('sale_price')
    itm_purchase_price = request.POST.get('purchase_price')
    stock_in_hand = request.POST.get('stock_in_hand')
    if stock_in_hand == '' or None :
      stock_in_hand = 0
    itm_at_price = request.POST.get('at_price')
    if itm_at_price == '' or None:
      itm_at_price = 0
    itm_date = request.POST.get('itm_date')
    
    item = Item(user = request.user,
                itm_type = itm_type,
                itm_name = itm_name,
                itm_hsn = itm_hsn,
                itm_unit = itm_unit,
                itm_vat = itm_vat,
                itm_taxable = taxable_result,
                itm_sale_price = itm_sale_price,
                itm_purchase_price = itm_purchase_price,
                itm_stock_in_hand = stock_in_hand,
                itm_at_price = itm_at_price,
                itm_date = itm_date)
    item.save()

    trans = ItemTransactions(user = request.user, item = item, trans_type = 'Stock Open', trans_date = itm_date, trans_qty = stock_in_hand, 
                             trans_current_qty = stock_in_hand, trans_adjusted_qty = stock_in_hand, trans_price = itm_at_price)

    if request.user.is_company:
      item.company = request.user.company
      trans.company = request.user.company

    else:
      item.company = request.user.employee.company
      trans.company = request.user.employee.company
 
    item.save()
    trans.save()

    trhis = ItemTransactionsHistory(user = request.user, transaction = trans, hist_trans_qty = 0, hist_trans_current_qty = stock_in_hand, action = 'Created',
                                    hist_trans_adjusted_qty = stock_in_hand, hist_trans_type = trans.trans_type)
    trhis.save()

    if request.POST.get('save_and_next'):
      return redirect('load_item_create')
    elif request.POST.get('save'):
      return redirect('item_list_first')
    
def adjust_stock(request,id):
  if request.method=='POST':
    itm = Item.objects.get(id=id)
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company

    trans_type = request.POST.get('trans_type')
    if trans_type == 'on':
      trans_type = 'Stock Reduction'
      trans_qty = request.POST.get('reduced_qty')
    else:
      trans_type = 'Stock Addition'
      trans_qty = request.POST.get('added_qty')
    trans_date = request.POST.get('trans_date')

    adjusted_qty= request.POST.get('adjusted_qty')
    current_qty = request.POST.get('item_qty')
    itm.itm_stock_in_hand = adjusted_qty
    itm.save()
    trans = ItemTransactions(user=request.user,
                          company=cmp,
                          item=itm,
                          trans_type=trans_type,
                          trans_date=trans_date,
                          trans_qty=trans_qty,
                          trans_current_qty=current_qty,
                          trans_adjusted_qty=adjusted_qty)
    trans.save()

    trhis = ItemTransactionsHistory(user = request.user, transaction = trans, hist_trans_qty = trans_qty, hist_trans_current_qty = current_qty, action = 'Created',
                                    hist_trans_adjusted_qty = adjusted_qty, hist_trans_type = trans.trans_type)
    trhis.save()

  return redirect('item_list',id)

@csrf_exempt
def create_unit(request):
  if request.method == 'POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company  
    unit_name = request.POST.get('unit_name')
    new_unit = Unit.objects.create(company=cmp,unit_name=unit_name)
    response_data = {'unit_name': new_unit.unit_name, 'unit_id': new_unit.id}
    return JsonResponse(response_data)
  else:
    return JsonResponse({'error': 'Invalid method'}, status=400)
  
def load_item_edit(request,id):
  itm = Item.objects.get(id=id)
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  unit = Unit.objects.filter(company=cmp)
  context = {'usr':request.user, 'itm':itm, 'unit':unit}
  return render(request,'item_edit.html',context)
  
def item_edit(request,id):
  if request.method == 'POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company

    itm = Item.objects.get(id=id)
    itm.itm_type = request.POST.get('itm_type')
    itm.itm_name = request.POST.get('name')
    itm.itm_hsn = request.POST.get('hsn')

    itm_name = request.POST.get('name')
    itm_hsn = request.POST.get('hsn')
    
    if Item.objects.filter(company=cmp,itm_name=itm_name).exclude(itm_name = itm.itm_name).exists():
      messages.info(request,'Item already registered')
      return redirect('load_item_create')

    if Item.objects.filter(company=cmp,itm_hsn=itm_hsn).exclude(itm_hsn = itm.itm_hsn).exists():
      messages.info(request,'Item with this HSN already registered')
      return redirect('load_item_create')

    itm.itm_unit = request.POST.get('unit')
    itm.itm_vat = request.POST.get('vat')
    itm.itm_taxable = request.POST.get('taxable_result')
    itm.itm_sale_price = request.POST.get('sale_price')
    itm.itm_purchase_price = request.POST.get('purchase_price')

    stock_in_hand = request.POST.get('stock_in_hand')
    if stock_in_hand == '' or None :
      stock_in_hand = 0
    itm.itm_stock_in_hand = stock_in_hand

    itm_at_price = request.POST.get('at_price')
    if itm_at_price == '' or None:
      itm_at_price = 0
    itm.itm_at_price = itm_at_price

    itm.itm_date = request.POST.get('itm_date')
    itm.save()

    etrans = ItemTransactions.objects.filter(item=itm)
    new_stock_in_hand = stock_in_hand
    for e in etrans:
      e.trans_current_qty = new_stock_in_hand
      if e.trans_type == 'Stock Open':
        stock_val = int(new_stock_in_hand) + 0
      elif e.trans_type == 'Stock Addition':
        stock_val = int(e.trans_qty) + int(new_stock_in_hand)
      else:
        stock_val = int(new_stock_in_hand) - int(e.trans_qty)

      e.trans_adjusted_qty = stock_val
      e.save()
      
      trhis = ItemTransactionsHistory(user = request.user, transaction = e, hist_trans_current_qty = new_stock_in_hand, action = 'Updated',
                                        hist_trans_adjusted_qty = stock_val, hist_trans_type = e.trans_type)
      
      if e.trans_type == 'Stock Open':
        trhis.hist_trans_qty = 0
      else:
        trhis.hist_trans_qty = e.trans_qty
      trhis.save()
      new_stock_in_hand = stock_val

    itm.itm_stock_in_hand = new_stock_in_hand
    itm.save()

    if request.POST.get('save_and_next'):
      return redirect('load_item_create')
    elif request.POST.get('save'):
      return redirect('item_list',id)
    
  
def load_first_trans_edit(request,id):
  trans = ItemTransactions.objects.get(id=id)
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  unit = Unit.objects.filter(company=cmp)
  context = {'usr':request.user, 'trans':trans, 'unit':unit}
  return render(request,'item_first_trans_edit.html',context)
  
def first_trans_edit(request,id):
  if request.method == 'POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company

    itm = Item.objects.get(id=id)
    itm.itm_type = request.POST.get('itm_type')
    itm.itm_name = request.POST.get('name')
    itm.itm_hsn = request.POST.get('hsn')

    itm_name = request.POST.get('name')
    itm_hsn = request.POST.get('hsn')
    
    if Item.objects.filter(company=cmp,itm_name=itm_name).exclude(itm_name = itm.itm_name).exists():
      messages.info(request,'Item already registered')
      return redirect('load_item_create')

    if Item.objects.filter(company=cmp,itm_hsn=itm_hsn).exclude(itm_hsn = itm.itm_hsn).exists():
      messages.info(request,'Item with this HSN already registered')
      return redirect('load_item_create')

    itm.itm_unit = request.POST.get('unit')
    itm.itm_vat = request.POST.get('vat')
    itm.itm_taxable = request.POST.get('taxable_result')
    itm.itm_sale_price = request.POST.get('sale_price')
    itm.itm_purchase_price = request.POST.get('purchase_price')

    stock_in_hand = request.POST.get('stock_in_hand')
    if stock_in_hand == '' or None :
      stock_in_hand = 0
    itm.itm_stock_in_hand = stock_in_hand

    itm_at_price = request.POST.get('at_price')
    if itm_at_price == '' or None:
      itm_at_price = 0
    itm.itm_at_price = itm_at_price

    itm.itm_date = request.POST.get('itm_date')
    itm.save()

    etrans = ItemTransactions.objects.filter(item=itm)
    new_stock_in_hand = stock_in_hand
    for e in etrans:
      e.trans_current_qty = new_stock_in_hand
      if e.trans_type == 'Stock Open':
        stock_val = int(new_stock_in_hand) + 0
      elif e.trans_type == 'Stock Addition':
        stock_val = int(e.trans_qty) + int(new_stock_in_hand)
      else:
        stock_val = int(new_stock_in_hand) - int(e.trans_qty)

      e.trans_adjusted_qty = stock_val
      e.save()
      
      trhis = ItemTransactionsHistory(user = request.user, transaction = e, hist_trans_current_qty = new_stock_in_hand, action = 'Updated',
                                        hist_trans_adjusted_qty = stock_val, hist_trans_type = e.trans_type)
      
      if e.trans_type == 'Stock Open':
        trhis.hist_trans_qty = 0
      else:
        trhis.hist_trans_qty = e.trans_qty
      trhis.save()
      new_stock_in_hand = stock_val

    itm.itm_stock_in_hand = new_stock_in_hand
    itm.save()

    if request.POST.get('save_and_next'):
      return redirect('load_item_create')
    elif request.POST.get('save'):
      return redirect('item_list',id)
    
def load_trans_details(request):
  id = request.POST.get('id')
  trans = ItemTransactions.objects.get(id=id)
  trans_id = trans.id
  name = trans.item.itm_name
  date = trans.trans_date.strftime("%Y-%m-%d")
  current_qty = trans.trans_current_qty
  qty = trans.trans_qty
  adj_qty = trans.trans_adjusted_qty
  trans_type = trans.trans_type
  return JsonResponse({'message': 'success',
                       'trans_id':trans_id,
                       'name':name, 
                       'date':date,
                       'current_qty':current_qty, 
                       'qty':qty, 
                       'adj_qty':adj_qty, 
                       'trans_type':trans_type})

def edit_transactions(request):
  if request.method=='POST':
    id = request.POST.get('id')
    trans_stock_change = request.POST.get('trans_stock_change')
    trans_itm_date = request.POST.get('trans_itm_date')
    trans_item_quantity = request.POST.get('trans_item_quantity')
    stock_value = request.POST.get('stock_value')
    trans_adj_quantity = request.POST.get('trans_adj_quantity')

    trans = ItemTransactions.objects.get(id=id)
    trans.trans_type = trans_stock_change
    trans.trans_date = trans_itm_date
    trans.trans_qty = stock_value 
    trans.trans_current_qty = trans_item_quantity
    trans.trans_adjusted_qty = trans_adj_quantity
    trans.save()

    trhis = ItemTransactionsHistory(user = request.user, transaction = trans, hist_trans_qty = stock_value, hist_trans_current_qty = trans_item_quantity, 
                                    action = 'Updated',hist_trans_adjusted_qty = trans_adj_quantity, hist_trans_type = trans.trans_type)
    trhis.save()

    etrans = ItemTransactions.objects.filter(item = trans.item,id__gt=id)
    new_stock_in_hand = trans_adj_quantity
    for e in etrans:
      e.trans_current_qty = new_stock_in_hand
      if e.trans_type == 'Stock Open':
        stock_val = int(new_stock_in_hand) + 0
      elif e.trans_type == 'Stock Addition':
        stock_val = int(e.trans_qty) + int(new_stock_in_hand)
      else:
        stock_val = int(new_stock_in_hand) - int(e.trans_qty)

      e.trans_adjusted_qty = stock_val
      e.save()
      
      trhis = ItemTransactionsHistory(user = request.user, transaction = e, hist_trans_current_qty = new_stock_in_hand, action = 'Updated',
                                        hist_trans_adjusted_qty = stock_val, hist_trans_type = e.trans_type)
      
      if e.trans_type == 'Stock Open':
        trhis.hist_trans_qty = 0
      else:
        trhis.hist_trans_qty = e.trans_qty
      trhis.save()
      new_stock_in_hand = stock_val

    trans.item.itm_stock_in_hand = new_stock_in_hand
    trans.item.save()

    return JsonResponse({'message': 'success', 'id':trans.item.id})

def delete_item(request,id):
  Item.objects.get(id=id).delete()
  messages.info(request,'Item Deleted Successfully !!')
  return redirect('item_list_first')

def delete_transaction(request,id):
  dtrans = ItemTransactions.objects.get(id=id)
  itm = dtrans.item
  dtrans.delete()

  trans = ItemTransactions.objects.filter(item=itm)
  cstock = trans[0].trans_adjusted_qty
  for t in range(1,len(trans)):
    trans[t].trans_current_qty = cstock
    if trans[t].trans_type == 'Stock Addition':
      trans[t].trans_adjusted_qty = trans[t].trans_qty + cstock
      fstock = trans[t].trans_qty + cstock
    else:
      trans[t].trans_adjusted_qty = cstock - trans[t].trans_qty
      fstock = cstock - trans[t].trans_qty
    trans[t].save()

    if trans[t].id > id:
      trhis = ItemTransactionsHistory(user = request.user, transaction = trans[t], hist_trans_qty = trans[t].trans_qty, hist_trans_current_qty = cstock, 
                                      action = 'Updated', hist_trans_adjusted_qty = fstock, hist_trans_type = trans[t].trans_type)
      trhis.save()
    cstock = fstock

  itm.itm_stock_in_hand = cstock
  itm.save()

  messages.info(request,'Item Transaction Deleted Successfully !!')
  return redirect('item_list_first')

def load_itm_trans_history(request,id):
  trans = ItemTransactions.objects.get(id=id)
  trhis = ItemTransactionsHistory.objects.filter(transaction=trans)
  context = {'usr':request.user, 'trans':trans, 'trhis':trhis}
  return render(request,'item_transaction_history.html',context)
  
  
def allbill(request):
    if request.user.is_company:
          cmp = request.user.company
    else:
          cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user) 
   
    itm=PurchaseBill.objects.filter(company=cmp)
    pbill = PurchaseBill.objects.filter(company=cmp).values()
    pbills = PurchaseBill.objects.filter(company=cmp)

    for i in pbill:
      p_history= PurchaseBillTransactionHistory.objects.filter(purchasebill=i['id'],company=cmp).last()
      i['action']=p_history.action
      i['name']=p_history.staff.first_name+" "+p_history.staff.last_name
      i['party']=p_history.purchasebill.party.party_name
    return render(request, 'all_billdetils.html',{'itm':itm,'pbill':pbill,'pbills':pbills,'usr':request.user})
    
def purchasebill(request):
    if request.user.is_company:
          cmp = request.user.company
    else:
          cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user) 
    party=Party.objects.filter(company=cmp)
    item=Item.objects.filter(company=cmp)
    unit=Unit.objects.filter(company=cmp)
    last_bill = PurchaseBill.objects.filter(company=cmp).order_by('-billno').first()
    if last_bill:
        bill_no = last_bill.billno + 1
    else:
        bill_no = 1
    # print (bill_no)
    context = {
        'bill_no': bill_no,
        'party':party,
        'item':item,
        'unit':unit,
        'usr':request.user
        # Add other context variables as needed
    }
    return render(request, 'createpurchasebill.html',context)
    
def itemdetails(request):
  itmid = request.GET['id']
  itm = Item.objects.get(id=itmid)
  hsn = itm.itm_hsn
  vat = itm.itm_vat
  price = itm.itm_purchase_price
  qty = 0
  print(qty)
  return JsonResponse({'hsn':hsn, 'vat':vat,  'price':price, 'qty':qty})
  
def item_dropdown(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company
  options = {}
  option_objects = Item.objects.filter(company=cmp)
  for option in option_objects:
      options[option.id] = [option.id, option.itm_name]
  return JsonResponse(options)

def cust_dropdown(request):
    if request.user.is_company:
          cmp = request.user.company
    else:
          cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user) 
    party=Party.objects.filter(company=cmp,user=usr)

    id_list = []
    party_list = []
    for p in party:
      id_list.append(p.id)
      party_list.append(p.party_name)

    return JsonResponse({'id_list':id_list, 'party_list':party_list })


def custdata(request):
  cid = request.POST['id']
  part = Party.objects.get(id=cid)
  phno = part.contact
  address = part.address
  pay = part.payment
  bal = part.openingbalance
  return JsonResponse({'phno':phno, 'address':address, 'pay':pay, 'bal':bal})
  
def createbill(request):
    if request.method == 'POST': 
        if request.user.is_company:
            cmp = request.user.company
        else:
            cmp = request.user.employee.company  
        usr = CustomUser.objects.get(username=request.user)  
        part = Party.objects.get(id=request.POST.get('customername'))
        pbill = PurchaseBill(party=part, 
                             billno=request.POST.get('bill_no'),
                             billdate=request.POST.get('billdate'),
                             subtotal=float(request.POST.get('subtotal')),
                             adjust = request.POST.get("adj"),
                             taxamount = request.POST.get("taxamount"),
                             grandtotal=request.POST.get('grandtotal'),
                             company=cmp,
                             staff=usr
                             )
        pbill.save()
        
        product = tuple(request.POST.getlist("product[]"))
        qty =  tuple(request.POST.getlist("qty[]"))
        discount =  tuple(request.POST.getlist("discount[]"))
        tax =  tuple(request.POST.getlist("vat[]"))
        total =  tuple(request.POST.getlist("total[]"))
        billno = PurchaseBill.objects.get(billno=pbill.billno,company=cmp)
        # print(billno)
        if len(product)==len(qty)==len(tax)==len(discount)==len(total):
            mapped=zip(product,qty,tax,discount,total)
            mapped=list(mapped)
            for ele in mapped:
                itm = Item.objects.get(id=ele[0])
                PurchaseBillItem.objects.create(product = itm,qty=ele[1], VAT=ele[2],discount=ele[3],total=ele[4],purchasebill=billno,company=cmp)

        PurchaseBill.objects.filter(company=cmp,staff=usr).update(tot_bill_no=F('tot_bill_no') + 1)
        
        pbill.tot_bill_no = pbill.billno
        print(pbill.tot_bill_no)
        pbill.save()

        PurchaseBillTransactionHistory.objects.create(purchasebill=pbill,action='Created',company=cmp,staff=usr)

        if 'Next' in request.POST:
            return redirect('purchasebill')
        if "Save" in request.POST:
            return redirect('allbill') 
    else:
        return redirect('purchasebill')
     
def billhistory(request):
  pid = request.POST['id']
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  usr = CustomUser.objects.get(username=request.user) 
  pbill = PurchaseBill.objects.get(billno=pid,company=cmp,staff=usr)
  hst = PurchaseBillTransactionHistory.objects.filter(purchasebill=pbill,company=cmp).last()
  name = hst.staff.first_name + ' ' + hst.staff.last_name 
  action = hst.action
  return JsonResponse({'name':name,'action':action,'pid':pid,'usr':request.user})


def delete_purchasebill(request,id):
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  usr = CustomUser.objects.get(username=request.user) 
  pbill = PurchaseBill.objects.get(id=id)
  PurchaseBillItem.objects.filter(purchasebill=pbill,company=cmp).delete()
  pbill.delete()
  
  return redirect('allbill')



def details_purchasebill(request,id):
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  usr = CustomUser.objects.get(username=request.user) 
  pbill = PurchaseBill.objects.get(id=id,company=cmp)
  pitm = PurchaseBillItem.objects.filter(purchasebill=pbill,company=cmp)
  dis = 0
  for itm in pitm:
    dis += int(itm.discount)
  itm_len = len(pitm)

  context={'pbill':pbill,'pitm':pitm,'itm_len':itm_len,'dis':dis,'usr':request.user}
  return render(request,'vatbilldetils.html',context)
  
def history_purchasebill(request,id):
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company 
  usr = CustomUser.objects.get(username=request.user) 
  pbill = PurchaseBill.objects.get(id=id)
  hst= PurchaseBillTransactionHistory.objects.filter(purchasebill=pbill,company=cmp)

  context = {'hst':hst,'pbill':pbill,'usr':request.user}
  return render(request,'purchasebillhistory.html',context)
  
def edit_purchasebill(request,id):
  toda = date.today()
  tod = toda.strftime("%Y-%m-%d")
  
  if request.user.is_company:
    cmp = request.user.company
  else:
    cmp = request.user.employee.company
  usr = CustomUser.objects.get(username=request.user) 
  cust = Party.objects.filter(company=cmp)
  item = Item.objects.filter(company=cmp)
  item_units = Unit.objects.filter(company=cmp)

  pbill = PurchaseBill.objects.get(id=id,company=cmp)
  billprd = PurchaseBillItem.objects.filter(purchasebill=pbill,company=cmp)
  bdate = pbill.billdate.strftime("%Y-%m-%d")
  context = { 'pbill':pbill, 'billprd':billprd,'tod':tod,
             'cust':cust, 'item':item, 'item_units':item_units, 'bdate':bdate,'usr':request.user}
  return render(request,'purchasebilledit.html',context)
  
def save_purchasebill(request,id):
  if request.method =='POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company  

    usr = CustomUser.objects.get(username=request.user) 
    print('haiii')
    print (request.POST.get('customername'))
    part = Party.objects.get(id=request.POST.get('customername'))
    print(part)
    pbill = PurchaseBill.objects.get(id=id, company=cmp)
    print(pbill)

        # Access the related PurchaseBill instance through the ForeignKey


    pbill.party = part
    pbill.billdate = request.POST.get('billdate')
    pbill.subtotal =float(request.POST.get('subtotal'))
    pbill.grandtotal = request.POST.get('grandtotal')
    pbill.taxamount = request.POST.get("taxamount")
    pbill.adjust = request.POST.get("adj")
    pbill.company=cmp
    pbill.save()

    product = tuple(request.POST.getlist("product[]"))
    qty = tuple(request.POST.getlist("qty[]"))
    tax =  tuple(request.POST.getlist("vat[]"))
    total = tuple(request.POST.getlist("total[]"))
    discount = tuple(request.POST.getlist("discount[]"))

    PurchaseBillItem.objects.filter(purchasebill=pbill).delete()
    if len(total)==len(discount)==len(qty)==len(tax):
      mapped=zip(product,qty,tax,discount,total)
      mapped=list(mapped)
      for ele in mapped:
        itm = Item.objects.get(id=ele[0])
        PurchaseBillItem.objects.create(product =itm,qty=ele[1], VAT=ele[2],discount=ele[3],total=ele[4],purchasebill=pbill,company=cmp)

    PurchaseBillTransactionHistory.objects.create(purchasebill=pbill,action='Updated',company=cmp,staff=usr)
    return redirect('allbill')

  return redirect('allbill')

def save_unit(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user) 

    if request.method == 'POST':
      unit_name = request.POST.get('name')
      if unit_name == 'NUMBERS' or unit_name == 'BOX' or unit_name == 'PACKETS' or unit_name == 'numbers' or unit_name == 'box'  or unit_name == 'packets':
        return JsonResponse({'success': False})
      if Unit.objects.filter(unit_name=unit_name,company=cmp).exists():
         return JsonResponse({'success': False})
      itm = Unit(
          company=cmp,
          unit_name=unit_name,
       
      )
      itm.save()

      return JsonResponse({'success': True})
    return JsonResponse({'success': False})
    
def save_item(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user) 

    if request.method == 'POST':
      itm_type = request.POST.get('itm_type')
      name = request.POST.get('name')
      itm_hsn = request.POST.get('hsn')
      itm_unit = request.POST.get('unit')
      itm_taxable = request.POST.get('taxref')
      itm_vat = request.POST.get('vat')
      itm_sale_price = request.POST.get('sell_price')
      itm_purchase_price = request.POST.get('cost_price')
      itm_stock_in_hand = request.POST.get('stock ', 0)  # Default to 0 if not provided
      itm_at_price = request.POST.get('itmprice ', 0)  # Default to 0 if not provided
      itm_date = request.POST.get('itmdate')

      # Check if the HSN number already exists in the database
      if Item.objects.filter(itm_hsn=itm_hsn,company=cmp).exists():
          # Send a message indicating that the HSN number already exists
          return JsonResponse({'success': False})

      itm = Item(
          user=usr,
          company=cmp,
          itm_type=itm_type,
          itm_name=name,
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
      itm.save()

      return JsonResponse({'success': True})
    return JsonResponse({'success': False})
        
def save_party1(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user)

    if request.method == 'POST':
        partyname = request.POST.get('partyname')
        trn_no = request.POST.get('trn_no')
        contact = request.POST.get('contact')
        trn_type = request.POST.get('trn_type')
        address = request.POST.get('address')
        email = request.POST.get('email')
        balance = request.POST.get('balance')
        paymentType = request.POST.get('paymentType')
        currentdate = request.POST.get('currentdate')
        additionalfield1 = request.POST.get('additionalfield1')
        additionalfield2 = request.POST.get('additionalfield2')
        additionalfield3 = request.POST.get('additionalfield3')
        # print(trn_no)
        # print(partyname)

        # Check if the contact number already exists in the database
        if Party.objects.filter(contact=contact,company=cmp).exists():
            # Send a message indicating that the contact number already exists

            return redirect('createbill')

        # Check if the transaction number already exists in the database
        if trn_type == "Unregistered/Consumers":
            Party.objects.create(    user=usr,
            company=cmp,
            party_name=partyname,
            trn_no=trn_no,
            contact=contact,
            trn_type=trn_type,
            address=address,
            email=email,
            openingbalance=balance,
            payment=paymentType,
            current_date=currentdate,
            additionalfield1=additionalfield1,
            additionalfield2=additionalfield2,
            additionalfield3=additionalfield3)
            # Optionally, you can send a success message here

            return redirect('createbill')
        else:
             if Party.objects.filter(trn_no=trn_no, company=cmp).exists():
                # Send a message indicating that the transaction number already exists

                return redirect('createbill')
        Party.objects.create(
            user=usr,
            company=cmp,
            party_name=partyname,
            trn_no=trn_no,
            contact=contact,
            trn_type=trn_type,
            address=address,
            email=email,
            openingbalance=balance,
            payment=paymentType,
            current_date=currentdate,
            additionalfield1=additionalfield1,
            additionalfield2=additionalfield2,
            additionalfield3=additionalfield3
        )
        return redirect('createbill')
        
def sharepdftomail(request,id):
 if request.user:
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']
                

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                email_message = request.POST['email_message']
                if request.user.is_company:
                  cmp = request.user.company
                else:
                  cmp = request.user.employee.company  
                usr = CustomUser.objects.get(username=request.user)
                # print(emails_list)
                pbill = PurchaseBill.objects.get(id=id,company=cmp)
                pitm = PurchaseBillItem.objects.filter(purchasebill=pbill)
                dis = 0
                for itm in pitm:
                  dis += int(itm.discount)
                itm_len = len(pitm)
                context={'pbill':pbill,'pitm':pitm,'itm_len':itm_len,'dis':dis}
                template_path = 'vatpdf.html'
                template = get_template(template_path)

                html  = template.render(context)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
                pdf = result.getvalue()
                filename = f'Purchase bill - {pbill.billno}.pdf'
                subject = f"Purchase bill - {pbill.billno}"
                email = EmailMessage(subject, f"Hi,\nPlease find the Purchase bill- Bill-{pbill.billno}. \n{email_message}\n\n--\nRegards,\n{pbill.company.company_name}\n{pbill.company.address}\n - {pbill.company.city}\n{pbill.company.contact}", from_email=settings.EMAIL_HOST_USER,to=emails_list)
                email.attach(filename, pdf, "application/pdf")
                email.send(fail_silently=False)

                msg = messages.success(request, 'purchase bill has been shared via email successfully..!')
                return redirect(details_purchasebill,id)
        except Exception as e:
            print(e)
            messages.error(request, f'{e}')
            return redirect(details_purchasebill, id)
            
def save_party2(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user)

    if request.method == 'POST':
        pbillhide=request.POST.get('pbillhid')
        partyname = request.POST.get('partyname')
        trn_no = request.POST.get('trn_no')
        contact = request.POST.get('contact')
        trn_type = request.POST.get('trn_type')
        address = request.POST.get('address')
        email = request.POST.get('email')
        balance = request.POST.get('balance')
        paymentType = request.POST.get('paymentType')
        currentdate = request.POST.get('currentdate')
        additionalfield1 = request.POST.get('additionalfield1')
        additionalfield2 = request.POST.get('additionalfield2')
        additionalfield3 = request.POST.get('additionalfield3')
        # print(trn_no)
        # print(partyname)

        # Check if the contact number already exists in the database
        if Party.objects.filter(contact=contact,company=cmp).exists():
            # Send a message indicating that the contact number already exists

            return redirect('edit_purchasebill', pbillhide)

        # Check if the transaction number already exists in the database
        if trn_type == "Unregistered/Consumers":
            prtobj = Party.objects.create(    user=usr,
            company=cmp,
            party_name=partyname,
            trn_no=trn_no,
            contact=contact,
            trn_type=trn_type,
            address=address,
            email=email,
            openingbalance=balance,
            payment=paymentType,
            current_date=currentdate,
            additionalfield1=additionalfield1,
            additionalfield2=additionalfield2,
            additionalfield3=additionalfield3)
            prtobj.save()
            # Optionally, you can send a success message here

            return redirect('edit_purchasebill', pbillhide)
        else:
             if Party.objects.filter(trn_no=trn_no, company=cmp).exists():
                # Send a message indicating that the transaction number already exists

                return redirect('edit_purchasebill', pbillhide)
        prtobj = Party.objects.create(
            user=usr,
            company=cmp,
            party_name=partyname,
            trn_no=trn_no,
            contact=contact,
            trn_type=trn_type,
            address=address,
            email=email,
            openingbalance=balance,
            payment=paymentType,
            current_date=currentdate,
            additionalfield1=additionalfield1,
            additionalfield2=additionalfield2,
            additionalfield3=additionalfield3
        )
        prtobj.save()
        return redirect('edit_purchasebill', pbillhide)
        
def check_trn_no_exists(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user) 
    trn_no = request.GET.get('trn_no')
    trn_type = request.POST.get('trn_type')
    print(trn_type)
    if trn_type != "Unregistered/Consumers":
      if Party.objects.filter(trn_no=trn_no,company=cmp).exists():
          return JsonResponse({'exists': True})
      return JsonResponse({'exists': False})

def check_phone_number_exists(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user)
    phone_number = request.GET.get('phone_number')
    if Party.objects.filter(contact=phone_number,company=cmp).exists():
        return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})
    
def check_hsn_number_exists(request):
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    usr = CustomUser.objects.get(username=request.user)
    hsn = request.GET.get('hsn1')
    if Item.objects.filter(itm_hsn=hsn,company=cmp).exists():
        return JsonResponse({'exists': True})
    return JsonResponse({'exists': False})
    
    
def unit_reload_modal(request):
    if request.user.is_authenticated:
        if request.user.is_company:
            cmp = request.user.company
        else :
            cmp = request.user.employee.company
        units = Unit.objects.filter(company=cmp)
        
        units_list = [{'name': unlist.unit_name} for unlist in units]
        success = True
        data = {'unitsobj': units_list,'success': success}
        return JsonResponse(data,safe=False)
       
    else:
        # Handle the case when the user is not authenticated
        return JsonResponse({'error': 'User is not authenticated'},status=401)
        
        
#Aami Jafer MultiUser Billing  softwareVAT
def creditNote(request):
  if request.user.is_company:
        cmp = request.user.company
  else:
        cmp = request.user.employee.company
  creditnotes=CreditNote.objects.filter(company=cmp)
  if not creditnotes:
    return render(request,'CreditNote.html',{'usr':request.user})
  else:
    return redirect('SalesReturn') 

def SalesReturn(request):

    if request.user.is_company:

        cmp = request.user.company

    else:

        cmp = request.user.employee.company

    parties = Party.objects.filter(company=cmp)

    items = Item.objects.filter(company=cmp)

    unit = Unit.objects.filter(company=cmp)

    

    try:

        latest_reference = CreditNoteReference.objects.filter(company=cmp).latest('id')

        reference_number = int(latest_reference.reference_no) + 1

    except ObjectDoesNotExist:

        reference_number = 1

    context = {'usr':request.user, 'parties':parties, 'items':items,'unit':unit,'cmp':cmp,'reference_number': reference_number}

    

    return render(request, 'SalesReturn.html', context)

def saveParty(request):
    if request.user.is_authenticated:
      if request.method == "POST":
          if request.user.is_company:
            cmp = request.user.company
          else:
            cmp = request.user.employee.company  
          print(cmp)
          usr = CustomUser.objects.get(username=request.user)
          party_name = request.POST['party_name']
          gst_no = request.POST['gst_no']
          mob = request.POST['mob']
          gsttype = request.POST['gsttype']
          state = request.POST['state']
          email = request.POST['email']
          addr = request.POST['addr']
          opbal = request.POST['opbal']
          payment = request.POST.get('paymentType','')
          date = request.POST['date']
          add1 = request.POST['add1']
          add2 = request.POST['add2']
          add3 = request.POST['add3']

          try:
            # Check if a party with the same trn_no already exists
            if Party.objects.filter(trn_no=gst_no, company=cmp).exists() and not(gsttype == 'Unregistered/Consumers'):
                error_message = 'TRN number already exists!!!'
            elif gst_no == '' and (gsttype == 'Registered Business - Regular' or gsttype == 'Registered Business - Composition'):
                error_message = 'TRN number required.'
            elif Party.objects.filter(email=email, company=cmp).exists():
                error_message = 'Email already exists!!!'
            elif Party.objects.filter(contact=mob,company=cmp).exists():
                error_message = 'Mobile number already exists!!!'
            else:
          
              user = request.user  
              party = Party(
                  user=user,
                  company=cmp,
                  party_name=party_name,
                  trn_no=gst_no,
                  contact=mob,
                  trn_type=gsttype,
                  state=state,
                  address=addr,
                  email=email,
                  openingbalance=opbal,
                  payment=payment,
                  current_date=date,
                  additionalfield1=add1,
                  additionalfield2=add2,
                  additionalfield3=add3
              )
              party.save()
              print('Party created succefully ')
              trans = Transactions_party(user=request.user,company=cmp, trans_type='Opening Balance', trans_number=gst_no,
                                           trans_date=date, total=opbal, balance=opbal, party=party)
              trans.save()
              tr_history = PartyTransactionHistory(party=party, Transactions_party=trans, action="CREATED")
              tr_history.save()
              return JsonResponse({'success': True})
          except IntegrityError:
            # Specific error message for duplicate TRN number
            error_message = 'An error occurred while processing your request. Please try again.'
          return JsonResponse( {'error_message': error_message})
      
def party_dropdown(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company  
  options={}
  option_objects=Party.objects.filter(company=cmp)
  for option in option_objects:
    options[option.id]=option.party_name
  return JsonResponse(options)

def get_partydetails(request):
  if request.method == 'POST':
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company  
    party_id= request.POST.get('id').split(" ")[0]
    party=Party.objects.get(company=cmp,id=party_id)
    print(party.party_name)
    sales_invoice = SalesInvoice.objects.filter(party=party).first()

    balance=party.openingbalance
    phone=party.contact
    payment = party.payment
    if party.address:
      address=party.address
    if sales_invoice:
      invoiceno = sales_invoice.invoice_no
      print(invoiceno)
      invoicedate = sales_invoice.date
      placeofsupply = sales_invoice.address
    else:
      invoiceno = None
      invoicedate = None
      placeofsupply = None

    return JsonResponse({'address':address,'balance':balance,'phone':phone,'invoiceno':invoiceno,'invoicedate':invoicedate,'placeofsupply':placeofsupply,'payment':payment})


def saveItem(request):
  if request.method == 'POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company  
    print(cmp)
    usr = CustomUser.objects.get(username=request.user)
    item_type=request.POST['item_type']
    item_name=request.POST['item_name']
    item_hsn=request.POST['item_hsn']
    item_unit=request.POST['item_unit']
    itm_taxable=request.POST['itm_taxable']
    itm_vat=request.POST['itm_vat']
    itm_sale_price=request.POST['itm_sale_price']
    itm_purchase_price=request.POST['itm_purchase_price']
    itm_stock_in_hand=request.POST['itm_stock_in_hand']
    itm_at_price=request.POST['itm_at_price']
    itm_date=request.POST['itm_date']
    if Item.objects.filter(company=cmp,itm_name=item_name).exists():
      error_message = 'Item already registered!!!'
      return JsonResponse({'error_message': error_message})
    if Item.objects.filter(company=cmp,itm_hsn=item_hsn).exists():
      error_message = 'Item with this HSN already registered!!!'
      return JsonResponse({'error_message': error_message})
    item = Item(
                user=usr,
                company=cmp,
                itm_type=item_type,
                itm_name=item_name,
                itm_hsn=item_hsn,
                itm_unit=item_unit,
                itm_taxable=itm_taxable,
                itm_vat=itm_vat,
                itm_sale_price=itm_sale_price,
                itm_purchase_price=itm_purchase_price,
                itm_stock_in_hand=itm_stock_in_hand,
                itm_at_price=itm_at_price,
                itm_date=itm_date
            )
    item.save()
    print("Item saved")
    return HttpResponse({"message": "success"})
  
    
def get_itemdetails(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company  
  item_id = request.POST.get('id').split(" ")[0]
  item=Item.objects.get(company=cmp,pk=item_id)
  hsn=item.itm_hsn
  price=item.itm_sale_price
  tax=item.itm_vat
  return JsonResponse({'hsn':hsn,'price':price,'tax':tax})

def fetch_item_details(request):
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company
    item_id = request.POST.get('id')
    item = Item.objects.get(pk=item_id,company=cmp)
    data = {
                'hsn': item.itm_hsn,
                'price': item.itm_sale_price,
                'tax': item.itm_vat
            }
    return JsonResponse(data)

def get_item_dropdown(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company  
  options={}
  option_objects=Item.objects.filter(company=cmp)
  for option in option_objects:
    options[option.id]=[option.id, option.itm_name]
  return JsonResponse(options)

def saveCreditnote(request):
  if request.method == 'POST':
    if request.user.is_company:
      cmp = request.user.company
    else:
      cmp = request.user.employee.company
    usr = CustomUser.objects.get(username=request.user)
    return_date=request.POST['returndate']
    reference_no=request.POST['refnum']
    subtotal=request.POST['subtotal']
    vat=request.POST['disvatper']
    adjustment=request.POST['adjustment']
    grandtotal=request.POST['grandTotal']
    party_status = request.POST.get('partystatus')
    print("Partystatus: ",party_status)
    creditnote = CreditNote.objects.create(user=usr, company=cmp,partystatus=party_status,returndate=return_date, subtotal=subtotal, vat=vat, adjustment=adjustment, grandtotal=grandtotal)
    CreditNoteReference.objects.create(user=usr, company=cmp, credit_note=creditnote, reference_no=reference_no)
    if party_status=='partyon':
      party_details = request.POST.get('party_details')
      party_id = party_details.split()[0]
      party = Party.objects.get(pk=party_id)
      
      print(party.party_name)
      creditnote.party=party
      try:
        salesinvoice = SalesInvoice.objects.get(company=cmp, party=party)
        creditnote.salesinvoice = salesinvoice
      except SalesInvoice.DoesNotExist:
        # Handle the case where SalesInvoice does not exist
        pass
      creditnote.save()
    CreditNoteHistory.objects.create(user=usr,company=cmp,credit_note_history=creditnote,action='Created')
    # item_names = request.POST.getlist('item_name')
    # for item_name in item_names:
    #   print(item_name)
    # for item_data in item_names:

    #   item_data_parts = item_data.split()

    #     # Extract individual values
    #   itemid = item_data_parts[0]
    #   itmhsn = item_data_parts[1]
    #   itmsale_price = item_data_parts[2]
    #   itmvat = item_data_parts[3]

    #   print("Item ID:", itemid)
    #   print("Item HSN:", itmhsn)
    #   print("Item Sale Price:", itmsale_price)
    #   print("Item VAT:", itmvat)

    item_name = request.POST.getlist('item_name')
    quantity = request.POST.getlist('qty')
    price = request.POST.getlist('price')
    tax = request.POST.getlist('tax')
    discount = request.POST.getlist('discount')
    hsn = request.POST.getlist('hsn')
    total = request.POST.getlist('total')
    if len(item_name) == len(quantity) == len(price) == len(tax) == len(discount) == len(hsn) == len(total) and item_name and quantity and price and tax and discount and hsn and total:
      mapped=zip(item_name,quantity,price,tax,discount,hsn,total)
      mapped=list(mapped)
      for ele in mapped:
        item_name_parts = ele[0].split()
        
        item_id = item_name_parts[0]
        items = Item.objects.get(pk=item_id)
        it=Item.objects.get(company=cmp, id = item_id).itm_name
        print("item_name:", it)

        creditnoteitem=CreditNoteItem.objects.create(
                  user=usr,
                  credit_note=creditnote,
                  company=cmp,
                  items=items,
                  item=it,
                  hsn=ele[5],
                  quantity=ele[1],
                  tax=ele[3],
                  price=ele[2],
                  discount=ele[4],
                  total=ele[6])
      if 'save_new' in request.POST:
        return redirect('SalesReturn')
      else:
        return redirect('listout_page')
    
  else:  
    return redirect('SalesReturn')
  
def listout_page(request):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company 
  creditnotes=CreditNote.objects.filter(company=cmp)
  context = {'usr':request.user,'creditnotes':creditnotes}
  return render(request,'listout.html',context)
  
def edit_creditnote(request,pk):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company
  parties = Party.objects.filter(company=cmp)
  items = Item.objects.filter(company=cmp)
  unit = Unit.objects.filter(company=cmp)
  creditnote_curr=CreditNote.objects.get(id=pk)
  reference=CreditNoteReference.objects.get(credit_note=creditnote_curr)
  creditnote_items=CreditNoteItem.objects.filter(credit_note=creditnote_curr)
  for item in creditnote_items:
    print(f"Item ID: {item.id}")
    print(f"Credit Note: {item.item}")
  context={'usr':request.user,
           'creditnoteitem_curr':creditnote_items,
           'credit_note':creditnote_curr,
           'parties':parties,
           'reference':reference,
           'items':items,'unit':unit
          }
  return render(request,'edit_creditnote.html',context)

def delete_creditnote(request,pk):
  creditnote=CreditNote.objects.get(id=pk)
  creditnote.delete()
  return redirect('listout_page')

def updateCreditnote(request,pk):
  if request.method=="POST":
    if request.user.is_company:
      cmp = request.user.company
      
    else:
      cmp = request.user.employee.company
      
    usr = CustomUser.objects.get(username=request.user)
    creditnote=CreditNote.objects.get(id=pk)
    reference=CreditNoteReference.objects.get(credit_note=creditnote)
    creditnote.user=request.user
    creditnote.company=cmp
    creditnote.returndate=request.POST['returndate']
    reference.reference_no=request.POST['refnum']
    creditnote.subtotal=request.POST['subtotal']
    creditnote.vat=request.POST['disvatper']
    creditnote.adjustment=request.POST['adjustment']
    creditnote.grandtotal=request.POST['grandTotal']
    creditnote.partystatus = request.POST.get('partystatus')
    creditnote.save()
    reference.save()
    if creditnote.partystatus=='partyon':
      party_details = request.POST.get('party_details')
      party_id = party_details.split()[0]
      party = Party.objects.get(pk=party_id)
      party.contact=request.POST.get('party_phone')
      party.payment=request.POST.get('paymethod')
      party.save()
      print(party.party_name)
      creditnote.party=party
      try:
        salesinvoice = SalesInvoice.objects.get(company=cmp, party=party)
        creditnote.salesinvoice = salesinvoice
      except SalesInvoice.DoesNotExist:
        # Handle the case where SalesInvoice does not exist
        pass
      creditnote.save()
    else:
      creditnote.party = None
      creditnote.save()
    CreditNoteHistory.objects.create(user=usr,company=cmp,credit_note_history=creditnote,action='Updated')


    item_name = request.POST.getlist('item_name')
    quantity = request.POST.getlist('qty')
    price = request.POST.getlist('price')
    tax = request.POST.getlist('tax')
    discount = request.POST.getlist('discount')
    hsn = request.POST.getlist('hsn')
    total = request.POST.getlist('total')
    if len(item_name) == len(quantity) == len(price) == len(tax) == len(discount) == len(hsn) == len(total) and item_name and quantity and price and tax and discount and hsn and total:
      mapped=zip(item_name,quantity,price,tax,discount,hsn,total)
      mapped=list(mapped)
      credit_note_items = CreditNoteItem.objects.filter(credit_note=creditnote)

      item_ids=[]
      for ele in mapped:
        item_name_parts = ele[0].split()
        
        item_id = item_name_parts[0]
        item_ids.append(item_id)
        items = Item.objects.get(company=cmp,pk=item_id)
        it=Item.objects.get(company=cmp, id = item_id).itm_name
        print("item_name:", it)
        existing_credit_note_item = credit_note_items.filter(items=items).first()
        
        if existing_credit_note_item:
          existing_credit_note_item.quantity = ele[1]
          existing_credit_note_item.price = ele[2]
          existing_credit_note_item.tax = ele[3]
          existing_credit_note_item.discount = ele[4]
          existing_credit_note_item.hsn = ele[5]
          existing_credit_note_item.total = ele[6]
          existing_credit_note_item.save()
        else:
          CreditNoteItem.objects.create(
                user=usr,
                credit_note=creditnote,
                company=cmp,
                items=items,
                item=it,
                hsn=ele[5],
                quantity=ele[1],
                tax=ele[3],
                price=ele[2],
                discount=ele[4],
                total=ele[6]
            )
      existing_item_ids = [int(id.split('_')[-1]) for id in item_ids]
      items_to_delete = credit_note_items.exclude(items__id__in=existing_item_ids)
      items_to_delete.delete()
      return redirect('listout_page')
    
def credit_templates(request,pk):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company 
  creditnote_curr=CreditNote.objects.get(id=pk)
  reference=CreditNoteReference.objects.get(credit_note=creditnote_curr)
  creditnote_items=CreditNoteItem.objects.filter(credit_note=creditnote_curr)
  context = {'usr':request.user,'company':cmp,'creditnoteitem_curr':creditnote_items,
           'creditnote':creditnote_curr,'reference':reference}
  return render(request,'creditnote_temp.html',context)

def sharebill(request,id):
    print("sharebill")
    if request.user:
        try:
            if request.method == 'POST':
                emails_string = request.POST['email_ids']

                # Split the string by commas and remove any leading or trailing whitespace
                emails_list = [email.strip() for email in emails_string.split(',')]
                print("ekamisl",emails_list)
                email_message = request.POST['email_message']
                # print(emails_list)
                template_format = request.POST.get('template_format')
                
                print("template_format : ",template_format)
                if template_format == '1':
                    print("Format1")
                    template_path = 'creditnote_temp_format1.html'
                elif template_format == '2':
                    print("Format2")
                    template_path = 'creditnote_temp_format2.html'
                elif template_format == '3':
                    print("Format3")
                    template_path = 'creditnote_temp_format3.html'
                else:
                    print("else")
                    template_path = 'creditnote_temp_format1.html'
                if request.user.is_company:
                    cmp = request.user.company
                else:
                    cmp = request.user.employee.company 
                parties = Party.objects.filter(company=cmp)
                items = Item.objects.filter(company=cmp)
                unit = Unit.objects.filter(company=cmp)
                creditnote_curr=CreditNote.objects.get(id=id)
                reference=CreditNoteReference.objects.get(credit_note=creditnote_curr)
                creditnote_items=CreditNoteItem.objects.filter(company=cmp,credit_note=creditnote_curr)
                context={'usr':request.user,
                        'company':cmp,
                        'creditnoteitem_curr':creditnote_items,
                        'creditnote':creditnote_curr,
                        'parties':parties,
                        'reference':reference,
                        'items':items,'unit':unit
                        }
                html = render_to_string(template_path, context)
                pdf = render_to_pdf(html)
                if pdf:
                  subject = f"CreditNote - {cmp.company_name}"
                  body = f"Hi,\nPlease find the attached Statement. \n{email_message}\n\n--\nRegards,\n{cmp.company_name}\n{cmp.address}\n{cmp.city} - {cmp.state}\n{cmp.contact}"
                  email = EmailMessage(subject, body, from_email=settings.EMAIL_HOST_USER, to=emails_list)
                  email.attach(f'Creditnote_{reference.reference_no}.pdf', pdf, 'application/pdf')
                  email.send(fail_silently=False)

                  messages.success(request, 'Statement has been shared via email successfully..!')
                else:
                  messages.error(request, 'Failed to generate PDF.')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('credit_templates', id)

def render_to_pdf(html):
    # Generate PDF from HTML content
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return result.getvalue()
    return None

def history_page(request,pk):
  if request.user.is_company:
      cmp = request.user.company
  else:
      cmp = request.user.employee.company
  creditnote=CreditNote.objects.get(id=pk)
  reference=CreditNoteReference.objects.get(credit_note=creditnote)
  credit_hist=CreditNoteHistory.objects.filter(credit_note_history=pk) 
  context={'c_usr':request.user,'c_comp':cmp,'creditnote':creditnote,'credit_hist':credit_hist,'reference':reference}
  return render(request,'historyPage.html',context)

#Aami Jafer MultiUser Billing  softwareVAT





def firstdebitnote(request):
    # You may need to fetch data or perform any logic related to the first debit note here
    # For example, check if there are existing debit notes
    debit_notes_exist = DebitNote.objects.filter(user=request.user).exists()

    context = {
        'usr': request.user,
        'debit_notes_exist': debit_notes_exist,
    }

    return render(request, 'firstdebitnote.html', context)


def debit_note_redirect(request):
    # Check if any debit notes exist for the logged-in user
    debit_notes_exist = DebitNote.objects.filter(user=request.user).exists()

    if debit_notes_exist:
        # Debit notes exist, redirect to the page displaying the debit notes
        return redirect('debitnote2')  # Adjust the URL name as per your project

    else:
        # No debit notes exist, redirect to the page for creating the first debit note
        return redirect('firstdebitnote')



@csrf_exempt
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
    print("Bills:", bills)

    # Determine the next return number
    last_debit_note = DebitNote.objects.filter(company=cmp).order_by('-returnno').first()
    if last_debit_note:
        next_return_no = int(last_debit_note.returnno) + 1
    else:
        next_return_no = 1

    context = {
        'usr': request.user,
        'parties': parties,
        'bills': bills,
        'items': items,
        'units': unit,
        'company_id': cmp.id,  # Pass company_id to the template
        'count': next_return_no,  # Pass the next return number to the template
    }

    if request.method == 'POST':
        user_id = request.session.get('user')

        if user_id is None:
            return JsonResponse({'status': 'error', 'message': 'User ID not available'})

        try:
            party_id = request.POST.get('party')
            bill_id = request.POST.get('bill')

            selected_party = get_object_or_404(Party, id=party_id)
            selected_bill = get_object_or_404(PurchaseBill, id=bill_id)
            selected_item = selected_party.purchasebill_set.first().item

            last_debit_note = DebitNote.objects.filter(company=cmp).order_by('-returnno').first()

            try:
                return_no = request.POST.get('return_no')

                if return_no and return_no.strip():
                    next_return_no = int(return_no) + 1
                else:
                    next_return_no = 1
            except ValueError:
                next_return_no = 1

            context['count'] = next_return_no
            
            # Create a DebitNote instance with the next return number
            debit_note = DebitNote.objects.create(
                party=selected_party,
                bill=selected_bill,
                user=request.user,
                company=cmp,
                returnno=next_return_no
            )

            # Retrieve the created DebitNote instance based on its ID
            debit_note_instance = get_object_or_404(DebitNote, id=debit_note.id)

            # Now you can get the tax rate from the Item instance using the get_vat_integer method
            taxRate = selected_item.get_vat_integer()

            # Fetching bills associated with the party
            bills = PurchaseBill.objects.filter(party=selected_party)

            # Formatting data for response
            data = {
                'name': selected_party.party_name,
                'id': selected_party.id,
                'bills': list(bills.values('billno', 'billdate'))
            }
         
            return render(request, 'createdebitnote.html', {
                'usr': request.user,
                'parties': parties,
                'bills': bills,
                'selected_party': selected_party,
                'selected_bill': selected_bill,
                'selected_item': selected_item,  
                'items': items,
                'company_id': cmp.id,
                'debit_note_instance': debit_note_instance,
                'taxRate': taxRate,
                'count': next_return_no, 
                'new_party_data': data  
            })

        except Exception as e:
            Logger.error(f"Error in createdebitnote view: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'An error occurred while processing the request'})

    return render(request, 'createdebitnote.html', context)



@csrf_exempt

def create_party(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.user.is_company:
                company_id = request.user.company.id
            else:
                company_id = request.user.employee.company.id
            user_id = request.user.id  # or request.user.pk

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
            data = {'name': new_party.party_name, 'id': new_party.id}
            return JsonResponse({'status': 'success', 'parties': data})
        else:
            return render(request, 'createdebitnote.html')
    else:
        return JsonResponse({'status': 'error', 'message': 'User is not authenticated'})

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
        print('Request received')

        # Retrieve each variable from the request
        itm_type = request.POST.get('itm_type')
        print('Item Type:', itm_type)

        itm_name = request.POST.get('itemName')
        print('Item Name:', itm_name)
        if Item.objects.filter(itm_name=itm_name).exists():
          response_data = {'success': False, 'message': 'Item name already exists!'}
          return JsonResponse(response_data)


        itm_hsn = request.POST.get('itemHSN')
        print('HSN:', itm_hsn)

        if Item.objects.filter(itm_hsn=itm_hsn).exists():
            response_data = {'success': False, 'message': 'HSN already exists!'}
            return JsonResponse(response_data)

        itm_unit = request.POST.get('unit')
        print('Unit:', itm_unit)

        itm_taxable = request.POST.get('taxable_result')
        print('Taxable:', itm_taxable)

        itm_vat = extract_percentage(request.POST.get('vat1'))
        print('VAT:', itm_vat)

        itm_sale_price = request.POST.get('sal_price')
        print('Sales Price:', itm_sale_price)

        itm_purchase_price = request.POST.get('pur_price')
        print('Purchase Price:', itm_purchase_price)

        itm_stock_in_hand = request.POST.get('opn_stock_')
        print('Stock In Hand:', itm_stock_in_hand)

        itm_at_price = request.POST.get('at_price')
        print('AT Price:', itm_at_price)

        itm_date = request.POST.get('date')
        print('Date:', itm_date)

        # Create item object and save
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

       
        response_data = {'success': True, 'message': 'Item created successfully!', 'item_id': item.id, 'itemName': item.itm_name}
        return JsonResponse(response_data)

    # Render a response if not a POST request
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
        
        # Prepare the JSON response data
        response_data = {
            'success': True,
            'message': 'Unit created successfully!',
            'unit_name': unit.unit_name,
            'unit_id': unit.id
        }
        print("Response Data:", response_data)

        return JsonResponse(response_data)

    # Handle other HTTP methods if needed
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def save_debit_note(request):
    company_id = request.session.get('company')
    user_id = request.session.get('user')

    if request.method == 'POST':
        party_id = request.POST.get('party')
        return_no = request.POST.get('return_no')  # Retrieve return_no from the form
        current_date = request.POST.get('current-date1') 
        subtotal = request.POST.get('subtotal')
        tax_amount = request.POST.get('taxAmount')
        adjustment = request.POST.get('adjustment')
        grand_total = request.POST.get('grandTotal')

        selected_party = Party.objects.get(id=party_id)

        # Create the debit note with the return number from the form
        debit_note = DebitNote.objects.create(
            user=request.user,
            company_id=company_id, 
            party=selected_party,
            returnno=return_no,  # Use the return number from the form
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

    # Fetch the company based on the user's role
    if request.user.is_company:
        cmp = request.user.company
    else:
        cmp = request.user.employee.company

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
                company_id=cmp,
                debitnote=debitnote,
                items=itm,
                qty=qty,
                discount=discount,
                total=total_amount,
            )

        # Log the update action
        DebitNoteHistory.objects.create(
            user=request.user,
            company_id=cmp,
            debit_note=debitnote,
            date=timezone.now(),  # Use current timestamp
            action='Updated'
        )

        return redirect('debitnote2')  # Redirect to debit note list page or any other desired page

    else:  # Handling GET request
        parties = Party.objects.filter(company_id=cmp)
        items = Item.objects.filter(company_id=cmp)
        debits = DebitNote.objects.filter(user=request.user).prefetch_related('debitnotehistory_set')
        current_date = debitnote.created_at.strftime('%Y-%m-%d') if debitnote.created_at else timezone.now().strftime('%Y-%m-%d')
        bills = PurchaseBill.objects.filter(party=debitnote.party)
        user_id = request.session.get('user')

        # Get selected items for the debit note
        selected_items = debitnote.debitnoteitem_set.all()
        selected_item = []
        for item in selected_items:
            selected_item.append({
                'id': item.items.id,
                'name': item.items.itm_name,
                'itm_hsn': item.items.itm_hsn,
                'purchaseprice': item.items.itm_purchase_price,
                'vat': item.items.itm_vat,
                'qty': item.qty,
                'discount': item.discount,
                'total_amount': item.total
            })
        print(selected_items)
        associated_bill = PurchaseBill.objects.filter(party=debitnote.party).first()

        context = {
            'debitnote': debitnote,
            'parties': parties,
            'items': items,
            'debits': debits,
            'company_id': cmp.id,
            'user_id': user_id,
            'usr': request.user,
            'selected_party': debitnote.party.id if debitnote.party else None,
            'return_no': debitnote.returnno,
            'current_date': current_date,
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
            'bills': bills,
            # Include additional context variables here
            'partyname': debitnote.party.party_name if debitnote.party else None,
            'balance': debitnote.party.openingbalance if debitnote.party else None,
            'contactnumber': debitnote.party.contact if debitnote.party else None,
            'bills': PurchaseBill.objects.filter(party=debitnote.party) if debitnote.party else None,
        }

        return render(request, 'editdebitnote.html', context)

def get_debit_note_history(request, debitnote_id):
    # Query the database for history data associated with the given debitnote_id
    history_data = DebitNoteHistory.objects.filter(debit_note__id=debitnote_id).select_related('debit_note__user').values('debit_note__returnno', 'date', 'user__first_name', 'user__last_name', 'action')

    # Convert queryset to list of dictionaries
    history_data_list = list(history_data)
    print("History data:", list(history_data))

    # Return the history data as JSON response
    return JsonResponse(history_data_list, safe=False)







# def generate_pdf(request, debit_note_id):
#     debit_note = DebitNote.objects.get(id=debit_note_id)
#     # Fetch related data
#     party = debit_note.party
#     debit_note_items = debit_note.debitnoteitem_set.all()  # Assuming you have related_name set for ForeignKey
#     # Render PDF template with fetched data
#     context = {
#         'debit_note': debit_note,
#         'party': party,
#         'debit_note_items': debit_note_items,
#     }
#     pdf_content = render_to_string('debit_note_pdf_template.html', context)

#     # Generate PDF using a library like WeasyPrint or ReportLab (not implemented here)
#     # For demonstration purposes, let's assume pdf_content contains the PDF data

#     # Return PDF as HttpResponse
#     response = HttpResponse(pdf_content, content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="debit_note_report.pdf"'
#     return response

def get_debit_note_details(request, debit_id):
    try:
        # Retrieve company based on user role
        if request.user.is_company:
            company = request.user.company
        else:
            company = request.user.employee.company

        # Retrieve debit note and related items
        debit_note = DebitNote.objects.get(id=debit_id)
        debit_note_items = DebitNoteItem.objects.filter(debitnote=debit_note)

        # Retrieve parties and items related to the company
        parties = Party.objects.filter(company=company)
        items = Item.objects.filter(company=company)

        # Prepare context data
        context = {
            'debit_id': debit_id,
            'usr': request.user,
            'company': company,
            'party': debit_note.party,
            'debit_note': debit_note,
            'debit_note_items': debit_note_items,
            'parties': parties,
            'items': items,
        }

        # Render template with context data
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
@csrf_exempt  
def share_debit_note_via_email(request, debit_note_id):
    if request.method == 'POST':
        try:
            # Retrieve data from the POST request
            email = request.POST.get('email')
            message = request.POST.get('message')
            template_content = request.POST.get('template_content')  # Retrieve the template content

            # Check if all required data is provided
            if not all([email, message, template_content]):
                return JsonResponse({'status': 'error', 'message': 'Missing required data'}, status=400)

            # Retrieve the debit note object
            debit_note = DebitNote.objects.get(id=debit_note_id)
            company = debit_note.company

            # Render HTML template for the debit note
            html_content = template_content

            # Generate PDF from HTML content
            pdf = render_to_pdf(html_content)

            # Create EmailMessage object with PDF attachment
            subject = "Debit Note"
            from_email = settings.EMAIL_HOST_USER
            email_message = EmailMessage(
                subject,
                message,
                from_email=from_email,
                to=[email]
            )
            email_message.attach('debit_note.pdf', pdf, 'application/pdf')

            # Send the email
            email_message.send(fail_silently=False)

            return JsonResponse({'status': 'success', 'message': 'Email sent successfully'})
        except DebitNote.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Debit note does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


def render_to_pdf(html):
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return result.getvalue()
    return None