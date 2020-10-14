from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator

import json
import datetime

from .filters import ItemFilter
from .form import CreateUserForm, CustomerForm
from .models import *
from .decorators import unauthenticated_user
from .utils import cookieCart, cartData, questOrder


# Create your views here.

def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'accounts/login.html', context)

def About(request):
    data = cartData(request)
    cartItems = data['cartItems']
    context = {'cartItems':cartItems}
    return render(request,'store_app/about.html',context)

def logoutUser(request):
    logout(request)
    return redirect('store')


def customer(request, pk):
    data = cartData(request)
    cartItems = data['cartItems']
    user = request.user
    form = CustomerForm(instance=user)
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    order_count = orders.count()

    context = {'customer': customer, 'orders': orders, 'order_count': order_count, 'form':form,'cartItems':cartItems}
    return render(request, 'accounts/customer.html', context)


def adminPanel(request):
    orders = Order.objects.all()
    customers = User.objects.all()
    total_cutomers = customers.count()
    total_order = orders.count()

    context = {'orders': orders, 'customers': customers, 'total_order': total_order, 'total_cutomers': total_cutomers}

    return render(request, 'accounts/adminpanel.html', context)


def product_view(request, pk):
    data = cartData(request)
    product = get_object_or_404(Product, id=pk)
    cartItems = data['cartItems']

    context = {'product': product,'cartItems':cartItems}

    return render(request, 'store_app/detail.html', context)

# def category_page(request):
#
#     return render(request, context)


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    object_list = Category.objects.filter(parent=None)
    products = Product.objects.all()



    myFilter = ItemFilter(request.GET, queryset=products)
    products = myFilter.qs

    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    context = {"products": products, 'cartItems': cartItems, 'paginator': paginator, 'object_list': object_list,'myFilter':myFilter}
    return render(request, 'store_app/store.html', context)


# def product_list(request):
#    filter = ItemFilter(request.GET, queryset=Product.objects.all())
#    return render(request, 'store_app/store.html', {'filter': filter})

def userPage(request):
    orders = request.user.customer.order_set.all()
    total_order = orders.count()
    print('Orders:', orders)
    context = {'orders': orders, 'total_order': total_order, }
    return render(request, 'accounts/user.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {"items": items, "order": order, 'cartItems': cartItems}
    return render(request, 'store_app/cart.html', context)


# @allowed_users(allowed_roles=['customer'])
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {"items": items, "order": order, 'cartItems': cartItems}
    return render(request, 'store_app/checkout.html', context)


# @allowed_users(allowed_roles=['customer'])
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)


    else:
        customer, order = questOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment complete!', safe=False)
