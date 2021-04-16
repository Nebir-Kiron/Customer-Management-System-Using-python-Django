from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# Create your views here.
from .models import Product 
from .models import Order 
from .models import Customer
from .forms import OrderForm,CreateUserForm,CustomerForm
from .filters import OrderFilter

from .decorators import unauthenticated_user , allowed_users,admin_only

@unauthenticated_user
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username = username , password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username Or Password is incorrect')
            return render(request, 'accounts/login.html')

    context = {}        
    return render(request, 'accounts/login.html',context)            
 
 
def logoutUser(request):
    logout(request)
    return redirect('login')
 

@unauthenticated_user
def register_page(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='Customer')
            user.groups.add(group)
            Customer.objects.create(
                user=user,
                name=user.username,
            )

            messages.success(request, 'Account Created For Successfully For ' + username )
            return redirect('login')

    context={
            'form' : form,
            }        
    return render(request, 'accounts/register.html',context)                





@login_required(login_url="login")
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_order = orders.count()
    total_customer = customers.count()
    order_delivered = orders.filter(status='Delevered').count()
    order_pending = orders.filter(status='pending').count()



    contex = {
        'orders':orders,
        'customers':customers,
        'total_order':total_order,
        'total_customer':total_customer,
        'order_delivered':order_delivered,
        'order_pending':order_pending,

    }

    return render(request,'accounts/dashboard.html',contex)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer','Admin'])
def user_page(request):
    orders = request.user.customer.order_set.all()
    total_order = orders.count()
    order_delivered = orders.filter(status='Delevered').count()
    order_pending = orders.filter(status='pending').count()
    context= {
        'orders'  : orders,
        'total_order':total_order,
        'order_delivered':order_delivered,
        'order_pending':order_pending,        
    }
    return render(request, 'accounts/user.html',context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['Customer','Admin'])
def accounts_settings(request):
    customer = request.user.customer 
    form = CustomerForm(instance=customer)

    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {'form':form}
    return render(request, 'accounts/accounts_settings.html',context)





@login_required(login_url='login')
def product(request):

    products = Product.objects.all()
     
    return render(request,'accounts/products.html',{'products':products})


@login_required(login_url="login")
@allowed_users(allowed_roles='Admin')
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET , queryset = orders)
    orders  =myFilter.qs
    context = {
        'customer':customer,
        'orders':orders,
        'order_count':order_count,
        'myFilter' : myFilter

    }
    return render(request,'accounts/customer.html',context)

@login_required(login_url="login")
@allowed_users(allowed_roles='Admin')
def create_order(request, pk_create):
    OrderFormSet = inlineformset_factory( Customer,Order, fields=('product','status'), extra=10)
    customer = Customer.objects.get(id = pk_create)
    formset = OrderFormSet(queryset = Order.objects.none(), instance=customer)
    #form = OrderForm(initial={'customer':customer})
    if request.method == 'POST' :
        #print('print post',request.POST)
        #form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST , instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
            
    context = {
        'formset':formset,

    }
    return render(request ,'accounts/order_form.html',context)



@login_required(login_url="login")
@allowed_users(allowed_roles='Admin')
def update_order(request,pk_order):
    order = Order.objects.get(id=pk_order)
    form = OrderForm(instance=order)
    if request.method == 'POST' :
        #print('print post',request.POST)
        form = OrderForm(request.POST ,instance=order)
        if form.is_valid():
            form.save()
            return redirect('/')
    

    context = {
        'form':form,

    }
    return render(request ,'accounts/order_form.html',context)

@login_required(login_url="login")
@allowed_users(allowed_roles='Admin')
def delete_order(request, pk_del):
    order = Order.objects.get(id=pk_del)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context = {
        'item':order,

    }
    return render(request, 'accounts/delete.html', context)