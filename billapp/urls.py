#MultiuserbillingVAT
from django.urls import re_path,path
from . import views
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

urlpatterns = [

    path('',views.home,name='home'),
    path('cmp_register/',views.cmp_register,name='cmp_register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('change_password/',views.change_password,name='change_password'),
    path('cmp_details/<int:id>/',views.cmp_details,name='cmp_details'),
    path('emp_register/',views.emp_register,name='emp_register'),
    path('dashboard/',views.dashboard,name='dashboard'),
     
    path('register_company/',views.register_company,name='register_company'),  
    path('register_company_details/<int:id>',views.register_company_details,name='register_company_details'),
    path('register_employee/',views.register_employee,name='register_employee'),  
    path('user_login/',views.user_login,name='user_login'),  
    path('cmp_profile/',views.cmp_profile,name='cmp_profile'),  
    path('load_edit_cmp_profile/',views.load_edit_cmp_profile,name='load_edit_cmp_profile'),  
    path('edit_cmp_profile',views.edit_cmp_profile,name='edit_cmp_profile'),  
    path('emp_profile/',views.emp_profile,name='emp_profile'),  
    path('load_edit_emp_profile/',views.load_edit_emp_profile,name='load_edit_emp_profile'),  
    path('edit_emp_profile',views.edit_emp_profile,name='edit_emp_profile'),  
    path('load_staff_request/',views.load_staff_request,name='load_staff_request'),  
    path('load_staff_list/',views.load_staff_list,name='load_staff_list'),  
    path('accept_staff/<int:id>',views.accept_staff,name='accept_staff'),  
    path('reject_staff/<int:id>',views.reject_staff,name='reject_staff'),  
    path('item_list_first/',views.item_list_first,name='item_list_first'),  
    path('item_list/<int:id>',views.item_list,name='item_list'),  
    path('load_item_create/',views.load_item_create,name='load_item_create'),  
    path('item_create',views.item_create,name='item_create'),  
    path('adjust_stock/<int:id>',views.adjust_stock,name='adjust_stock'),  
    path('create_unit',views.create_unit,name='create_unit'),  
    path('load_item_edit/<int:id>',views.load_item_edit,name='load_item_edit'),  
    path('item_edit/<int:id>',views.item_edit,name='item_edit'),  
    path('load_first_trans_edit/<int:id>',views.load_first_trans_edit,name='load_first_trans_edit'),  
    path('first_trans_edit/<int:id>',views.first_trans_edit,name='first_trans_edit'),  
    path('delete_item/<int:id>',views.delete_item,name='delete_item'),  
    path('load_trans_details',views.load_trans_details,name='load_trans_details'),  
    path('edit_transactions',views.edit_transactions,name='edit_transactions'),  
    path('delete_transaction/<int:id>',views.delete_transaction,name='delete_transaction'),  
    path('load_itm_trans_history/<int:id>',views.load_itm_trans_history,name='load_itm_trans_history'),  
    
    path('allbill',views.allbill,name='allbill'), 
    path('purchasebill',views.purchasebill,name='purchasebill'), 
    path('custdata',views.custdata,name='custdata'),
    path('cust_dropdown',views.cust_dropdown,name='cust_dropdown'),  
    path('itemdetails',views.itemdetails,name='itemdetails'), 
    path('item_dropdown',views.item_dropdown,name='item_dropdown'), 
    path('createbill',views.createbill,name='createbill'),
    path('billhistory',views.billhistory,name='billhistory'),
    path('delete_purchasebill/<int:id>',views.delete_purchasebill,name='delete_purchasebill'), 
    path('details_purchasebill/<int:id>',views.details_purchasebill,name='details_purchasebill'),
    path('history_purchasebill/<int:id>',views.history_purchasebill,name='history_purchasebill'),
    path('edit_purchasebill/<int:id>',views.edit_purchasebill,name='edit_purchasebill'),
    path('save_purchasebill/<int:id>',views.save_purchasebill,name='save_purchasebill'),
    path('save_item', views.save_item, name='save_item'),
    path('save_party1', views.save_party1, name='save_party1'),
    path('save_party2', views.save_party2, name='save_party2'),
    path('sharepdftomail/<int:id>',views.sharepdftomail, name='sharepdftomail'),
    path('check_trn_no_exists', views.check_trn_no_exists, name='check_trn_no_exists'),
    path('check_hsn_number_exists', views.check_hsn_number_exists, name='check_hsn_number_exists'),
    path('check_phone_number_exists', views.check_phone_number_exists, name='check_phone_number_exists'),
    path('unit_reload_modal', views.unit_reload_modal, name='unit_reload_modal'),
    path('save_unit', views.save_unit, name='save_unit'),
    
    #Mltiuser billing VAT AAMI JAFER
    path('creditNote/',views.creditNote,name="creditNote"),
    path('SalesReturn/',views.SalesReturn,name="SalesReturn"),
    path('saveParty',views.saveParty,name="saveParty"),
    path('party_dropdown',views.party_dropdown,name="party_dropdown"),
    path('get_partydetails',views.get_partydetails,name="get_partydetails"),
    path('saveItem',views.saveItem,name="saveItem"),
    path('get_itemdetails',views.get_itemdetails,name="get_itemdetails"),
    path('fetch_item_details',views.fetch_item_details,name="fetch_item_details"),
    path('get_item_dropdown',views.get_item_dropdown,name="get_item_dropdown"),
    path('create_unit',views.create_unit,name="create_unit"),
    path('saveCreditnote',views.saveCreditnote,name="saveCreditnote"),
    path('listout_page',views.listout_page,name="listout_page"),
    path('edit_creditnote/<int:pk>',views.edit_creditnote,name="edit_creditnote"),
    path('delete_creditnote/<int:pk>',views.delete_creditnote,name="delete_creditnote"),
    path('updateCreditnote/<int:pk>',views.updateCreditnote,name="updateCreditnote"),
    path('credit_templates/<int:pk>',views.credit_templates,name="credit_templates"),
    path('sharebill/<int:id>',views.sharebill,name="sharebill"),
    path('history_page/<int:pk>',views.history_page,name="history_page"),
    #Mltiuser billing VAT AAMI JAFER#Mltiuser billing VAT AAMI JAFER

    
    path('debit-note-redirect/', views.debit_note_redirect, name='debit_note_redirect'),
    path('firstdebitnote',views.firstdebitnote,name='firstdebitnote'),  
    path('createdebitnote',views.createdebitnote,name='createdebitnote'),
    path('create_party',views.create_party,name='create_party'), 
   
    path('item_create',views.item_create,name='item_create'),
    path('create_unit', views.create_unit, name='create_unit'),

    path('save_debit_note', views.save_debit_note, name='save_debit_note'),
    path('debitnote2', views.debitnote2, name='debitnote2'),
    path('delete_debit_note_item/<int:debitnote_id>/',views.delete_debit_note_item, name='delete_debit_note_item'),
   
    path('search-debitnotes/', views.search_debitnotes, name='search_debitnotes'),

    path('edit_debit_note/<int:debit_id>/',views.edit_debit_note,name='edit_debit_note'),
    path('get_debit_note_history/<int:debitnote_id>/',views.get_debit_note_history,name='get_debit_note_history'),
    
   
    path('get_debit_note_details/<int:debit_id>/', views.get_debit_note_details, name='get_debit_note_details'),
    path('share-debit-note-via-email/<int:debit_note_id>/', views.share_debit_note_via_email, name='share_debit_note_via_email'),
    
    
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)