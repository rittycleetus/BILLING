from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_company = models.BooleanField(default=0)
    

class Company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True,blank=True)
    company_code = models.CharField(max_length=100,null=True,blank=True)
    company_name = models.CharField(max_length=100,null=True,blank=True)
    address = models.CharField(max_length=100,null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    contact = models.CharField(max_length=100,null=True,blank=True)
    pincode = models.IntegerField(null=True,blank=True)
    pan_number = models.CharField(max_length=255,null=True,blank=True)
    gst_type = models.CharField(max_length=255,null=True,blank=True)
    gst_no = models.CharField(max_length=255,null=True,blank=True)
    profile_pic = models.ImageField(null=True,blank = True,upload_to = 'image/company')

class Employee(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,null=True, blank=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE, null=True, blank=True)
    contact = models.CharField(max_length=100,null=True,blank=True)
    is_approved = models.BooleanField(default=0)
    profile_pic = models.ImageField(null=True,blank = True,upload_to = 'image/employee')



class Item(models.Model):
    user =    models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    company =    models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    CHOICES = [
    ('Goods', 'Goods'),
    ('Service', 'Service'),
    ]
    itm_type = models.CharField(max_length=20, choices=CHOICES)
    itm_name = models.CharField(max_length=255)
    itm_hsn = models.IntegerField(null=True)
    itm_unit = models.CharField(max_length=255)
    itm_taxable = models.CharField(max_length=255)
    itm_vat = models.CharField(max_length=255,null=True)
    itm_sale_price = models.IntegerField()
    itm_purchase_price = models.IntegerField()
    itm_stock_in_hand = models.IntegerField(default=0)
    itm_at_price = models.IntegerField(default=0)
    itm_date = models.DateField()
   
    
class Party(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True,blank=True)
    
    party_name = models.CharField(max_length=100)
    trn_no = models.CharField(max_length=100,null=True,blank=True)
    contact = models.CharField(max_length=255,null=True,blank=True)
    trn_type = models.CharField(max_length=255,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    address = models.CharField(max_length=100,null=True,blank=True)

    email = models.EmailField(max_length=100,null=True,blank=True)
    openingbalance = models.CharField(max_length=100,default='0',null=True,blank=True)
    
    creditlimit = models.CharField(max_length=100,default='0',null=True,blank=True)
    current_date = models.DateField(max_length=255,null=True,blank=True)
    End_date = models.DateField(max_length=255,null=True,blank=True)
    additionalfield1 = models.CharField(max_length=100,null=True,blank=True)
    additionalfield2 = models.CharField(max_length=100,null=True,blank=True)
    additionalfield3 = models.CharField(max_length=100,null=True,blank=True)
    PAYMENT_CHOICES = [
        ('To Pay', 'To Pay'),
        ('To Receive', 'To Receive'),
    ]

    payment = models.CharField(max_length=100, choices=PAYMENT_CHOICES, null=True, blank=True)


class Unit(models.Model):
    company =    models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    unit_name = models.CharField(max_length=255)

class ItemTransactions(models.Model):
    user =    models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True)
    item = models.ForeignKey(Item,on_delete=models.CASCADE,null=True,blank=True)
    trans_type = models.CharField(max_length=255)
    trans_invoice = models.IntegerField(null=True,blank=True)
    trans_name = models.CharField(max_length=255)
    trans_date = models.DateTimeField()
    trans_qty = models.IntegerField(default=0)
    trans_current_qty = models.IntegerField(default=0)
    trans_adjusted_qty = models.IntegerField(default=0)
    trans_price = models.IntegerField(default=0)
    trans_status = models.CharField(max_length=255)

class ItemTransactionsHistory(models.Model):
    user =    models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    transaction =    models.ForeignKey(ItemTransactions,on_delete=models.CASCADE,null=True,blank=True)
    CHOICES = [
    ('Created', 'Created'),
    ('Updated', 'Updated'),
    ]
    action = models.CharField(max_length=20, choices=CHOICES)
    hist_trans_date = models.DateTimeField(auto_now_add=True)
    hist_trans_qty = models.IntegerField(default=0)
    hist_trans_current_qty = models.IntegerField(default=0)
    hist_trans_adjusted_qty = models.IntegerField(default=0)

class PurchaseBill(models.Model):
    billno = models.IntegerField(default=0,null=True,blank=True)
    staff = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    company = models.ForeignKey(Company,on_delete= models.CASCADE,null=True,blank=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    billdate = models.DateField()
    subtotal = models.IntegerField(default=0, null=True)
    VAT = models.CharField(max_length=100,default=0, null=True)
    taxamount = models.CharField(max_length=100,default=0, null=True)
    adjust = models.CharField(max_length=100,default=0, null=True)
    grandtotal = models.FloatField(default=0, null=True)
    advance=models.CharField(null=True,blank=True,max_length=255)
    balance=models.CharField(null=True,blank=True,max_length=255)
    
    

class PurchaseBillItem(models.Model):
    purchasebill = models.ForeignKey(PurchaseBill,on_delete=models.CASCADE)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    product = models.ForeignKey(Item,on_delete=models.CASCADE)
    qty = models.IntegerField(default=0, null=True)
    total = models.IntegerField(default=0, null=True)
    VAT = models.CharField(max_length=100)
    discount = models.CharField(max_length=100,default=0, null=True)
# class DebitNote(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
#     company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True,blank=True)
#     party= models.ForeignKey(Party, on_delete=models.CASCADE,null=True,blank=True)
#     returnno=models.IntegerField()
   

#     def __str__(self):
#         return f"Debit Note {self.id}"
class DebitNote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    # bill = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE)
    
    returnno = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    subtotal=models.DecimalField(max_digits=10, decimal_places=2,default=0,null=True)
    taxamount=models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    adjustment=models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
    grandtotal=models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)

    def __str__(self):
        return f"DebitNote {self.debit_note_number} - {self.party} - {self.bill}"

class DebitNoteItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    debitnote=models.ForeignKey(DebitNote,on_delete=models.CASCADE,null=True, blank=True)
    items = models.ForeignKey(Item,on_delete=models.CASCADE,null=True,blank=True)
    qty=models.IntegerField(default=0,null=True)
    discount=models.IntegerField(default=0,null=True)
    total=models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True)
   
