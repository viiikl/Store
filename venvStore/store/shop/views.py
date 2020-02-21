from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db.models import Q

from store import settings
from .forms import CartItemForm
from .models import Product, Cart, CartItem, Order, Category


# https://ccbv.co.uk/projects/Django/2.2/django.views.generic.list/ListView/
# djbook.ru/rel1.9/
class ProductList(ListView):
    """Список всех продуктов"""
    model = Product
    template_name = "shop/list-product.html"


class ProductDetail(DetailView):
    """Карточка товара"""
    model = Product
    context_object_name = 'product'
    template_name = 'shop/product-detail.html'

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        contex['form'] = CartItemForm()
        return contex


class AddCartItem(View):
    """добавление товара в корзину"""

    def post(self, request, slug, pk):
        quantity = request.POST.get('quantity', None)
        print(quantity)
        if quantity is not None and int(quantity) > 0:
            try:
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(user=request.user)
            print(f'cart.user= {cart.user} product_id= {pk}')
            try:
                item = CartItem.objects.get(cart__user=request.user, product_id=pk)
                print(f'item = {item}')
                item.quantity += int(quantity)
            except CartItem.DoesNotExist:
                item = CartItem(
                    cart=Cart.objects.get(user=request.user, accepted=False),
                    product_id=pk,
                    quantity=int(quantity)
                )
            item.save()
            messages.add_message(request, settings.MY_INFO, "Товар добавлен")
            return redirect('/detail/{}/'.format(slug))
        else:
            messages.add_message(request, settings.MY_INFO, "Значение не может быть 0")
            return redirect('/detail/{}'.format(slug))


class CartItemList(ListView):
    """Товары в корзине пользователя"""
    template_name = 'shop/cart.html'

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user, cart__accepted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sum = 0
        for item in context['object_list']:
            sum += int(item.price_sum)
        context['sum'] = sum
        context["cart_id"] = Cart.objects.get(user=self.request.user, accepted=False).id
        return context


class EditCartItem(View):
    """редактирование товара в корзине"""

    def post(self, request, pk):
        quantity = request.POST.get('quantity', None)
        if quantity:
            item = CartItem.objects.get(cart__user=request.user, id=pk)
            item.quantity = int(quantity)
            item.save()
        return redirect('cart_item')


class RemoveCartItem(View):
    """удаления товара с корзины"""

    def get(self, request, pk):
        CartItem.objects.get(cart__user=request.user, id=pk).delete()
        messages.add_message(request, settings.MY_INFO, "Товар удален")
        return redirect('cart_item')


class Search(View):
    """Поиск товаров"""

    def get(self, request):
        search = request.GET.get("search", None)
        products = Product.objects.filter(Q(title__icontains=search) |
                                          Q(category__name__icontains=search))
        return render(request, "shop/list-product.html", {"object_list": products})


class AddOrder(View):
    """Создание заказа"""

    def post(self, request):
        cart = Cart.objects.get(id=request.POST.get("pk"), user=request.user)
        cart.accepted = True
        cart.save()
        Order.objects.create(cart=cart)
        Cart.objects.create(user=request.user)
        return redirect('orders')


class OrderList(ListView):
    """Список заказов пользователя"""
    template_name = "shop/order-list.html"

    def get_queryset(self):
        return Order.objects.filter(cart__user=self.request.user, accepted=False)

    def post(self, request):
        order = Order.objects.get(id=request.POST.get("pk"), cart__user=request.user, accepted=False)
        order.delete()
        return redirect("orders")


class CategoryProduct(ListView):
    """Список товаров из категории"""
    template_name = "shop/list-product.html"

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        node = Category.objects.get(slug=slug)
        if Product.objects.filter(category__slug=slug).exists():
            products = Product.objects.filter(category__slug=slug)
        else:
            products = Product.objects.filter(category__slug__in=[x.slug for x in node.get_family()])
        return products
