from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from ..models import Profile,Category,Productview,Review,cart,Order, Orderitem, Otracker,ProductReaction,ProductViewCount,Topproduct
from ..serializers import CategorySerializer, ReviewSerializer, CartSerializer, OrderSerializer, OrderItemSerializer,TopproductSerializer
from ..serializers import CategorySerializer, TopproductSerializer,ProductViewSerializer
from django.shortcuts import get_object_or_404
from django.contrib import auth
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from django.core.paginator import Paginator
import math


def index(request):
    category = Category.objects.all()
    topproduct = Topproduct.objects.all()
    product_ids = request.session.get("recently_viewed", [])
    products = list(
        Productview.objects.filter(productviewid__in=product_ids)
    )
    products.sort(key=lambda x: product_ids.index(x.productviewid))
    category_serializer = CategorySerializer(category, many=True)
    topproduct_serializer = TopproductSerializer(topproduct, many=True)
    product_serializer = ProductViewSerializer(products, many=True)

    return Response({
        "status": True,
        "category": category_serializer.data,
        "topproduct": topproduct_serializer.data,
        "recently_viewed": product_serializer.data,
    })
@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def register(request):
    firstname = request.data.get('firstname')
    lastname = request.data.get('lastname')
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    conformpassword = request.data.get('conformpassword')
    image = request.FILES.get('image')
    if password != conformpassword:
        return Response({
            "status": False,
            "message": "Passwords do not match"
        })
    if len(password) < 8:
        return Response({
            "status": False,
            "message": "Password must be at least 8 characters"
        })
    if User.objects.filter(username=username).exists():
        return Response({
            "status": False,
            "message": "Username already taken"
        })
    if User.objects.filter(email=email).exists():
        return Response({
            "status": False,
            "message": "Email already taken"
        })
    user = User.objects.create_user(
        first_name=firstname,
        last_name=lastname,
        username=username,
        email=email,
        password=password,
    )
    Profile.objects.create(
        user=user,
        image=image,
    )
    return Response({
        "status": True,
        "message": "Account created successfully"
    })
@api_view(['POST'])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({
            "status": True,
            "message": "Login Successful",
            "username": user.username
        }, status=status.HTTP_200_OK)
    return Response({
        "status": False,
        "message": "Invalid Username or Password"
    }, status=status.HTTP_401_UNAUTHORIZED)
def logout(request):
    username = getattr(request.user, 'username', 'User')
    auth.logout(request)
    return Response({
        "status": True,
        "message": f"Successfully logged out, {username}"
    })
@api_view(['POST'])
def forgetpassword(request):
    email = request.data.get('email')
    newpassword = request.data.get('newpassword')
    confirmpassword = request.data.get('confirmpassword')
    if newpassword != confirmpassword:
        return Response({
            "status": False,
            "message": "Passwords do not match!"
        })
    if len(newpassword) < 8:
        return Response({
            "status": False,
            "message": "Password must be at least 8 characters."
        })
    user = User.objects.filter(email=email).first()
    if user:
        user.set_password(newpassword)
        user.save()
        return Response({
            "status": True,
            "message": "Password reset successful! Please login."
        })
    return Response({
        "status": False,
        "message": "No account found with this email."
    }, status=404)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def editprofile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    user.first_name = request.data.get('firstname')
    user.last_name = request.data.get('lastname')
    user.username = request.data.get('username')
    user.email = request.data.get('email')
    uploaded_image = request.FILES.get('profile_image')
    try:
        user.save()
        if uploaded_image:
            profile.image = uploaded_image
        profile.save()
        return Response({
            "status": True,
            "message": "Profile updated successfully!",
            "user": {
                "id": user.id,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "username": user.username,
                "email": user.email,
                "image": profile.image.url if profile.image else None
            }
        })
    except Exception:
        return Response({
            "status": False,
            "message": "Username or Email already exists"
        }, status=400)
@api_view(['GET'])
def collection(request, categoryid):
    try:
        categories = Category.objects.get(categoryid=categoryid)
    except Category.DoesNotExist:
        return Response({
            "status": False,
            "message": "Category not found"
        }, status=404)
    products = Productview.objects.filter(
        category_id=categoryid
    ).order_by('-productviewid')
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    ratings_map = {
        "Majestic Man Men Classic Slim Fit Pure Cotton Casual Shirt": 4.0,
        "Majestic Man Comfort Slim Fit Pure Cotton Checked Casual Shirt": 4.1,
        "Majestic Man Men’s Pure Cotton Striped Half Sleeve Regular Fit Shirt": 4.3,
        "Lux Cozi Men’s Polo T-Shirt  Comfortable Cotton Blend, Band Collar, Regular Fit  Stylish & Premium All Day Wear": 5.0,
        "Louis Philippe Men's Slim Fit Single-Tuck Pique Stylized Sleeve Print and Contrast Tipping Half Sleeve Solid Polo Tshirt": 4.0,
        "Kavora Men’s Solid Polo T-Shirt  Short Sleeve  Regular Fit Soft Breathable Fabric  Casual & Smart Wear  Button Placket Collar Top": 3.4,
        "KAJARU Men's Polyster Blend Regular Fit T-Shirt with Half Sleeve Chain Polo Collar V-Neck Standard Length and Classic Style": 4.1,
        "Bacca Bucci Men Lace Up Basketball Shoe": 4.2,
        "Bacca Bucci Men Lace Up Sneaker Shoes": 4.2,
        "Bacca Bucci Men Lace Up Running Shoes": 3.8,
        "Bacca Bucci Men Lace Up Athletic Shoes": 3.9,
    }
    product_data = []
    for product in page_obj:
        serializer = ProductViewSerializer(product)
        data = serializer.data
        rating = ratings_map.get(product.producttitle.strip(), 5.0)
        if (
            product.productmrpprice
            and product.productprice
            and product.productmrpprice > product.productprice
        ):
            discount = int(
                ((product.productmrpprice - product.productprice)
                 / product.productmrpprice) * 100
            )
        else:
            discount = 0
        data["rating"] = rating
        data["discount"] = discount
        product_data.append(data)
    return Response({
        "status": True,
        "category": CategorySerializer(categories).data,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_products": paginator.count,
        "products": product_data,
    })
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def productview(request, categoryid, productviewid):
    try:
        category = Category.objects.get(categoryid=categoryid)
        product = Productview.objects.get(productviewid=productviewid)
    except (Category.DoesNotExist, Productview.DoesNotExist):
        return Response({
            "status": False,
            "message": "Product not found"
        }, status=404)
    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key
    if request.user.is_authenticated:
        ProductViewCount.objects.get_or_create(
            product=product,
            user=request.user
        )
    else:
        ProductViewCount.objects.get_or_create(
            product=product,
            user=None,
            session_key=session_key
        )
    view_count = ProductViewCount.objects.filter(product=product).count()
    likes = ProductReaction.objects.filter(product=product, reaction='like').count()
    dislikes = ProductReaction.objects.filter(product=product, reaction='dislike').count()
    recently_viewed = request.session.get("recently_viewed", [])
    if productviewid in recently_viewed:
        recently_viewed.remove(productviewid)
    recently_viewed.insert(0, productviewid)
    request.session["recently_viewed"] = recently_viewed[:8]
    request.session.modified = True

    ratings_map = {
        "Majestic Man Men Classic Slim Fit Pure Cotton Casual Shirt": 4.0,
        "Majestic Man Comfort Slim Fit Pure Cotton Checked Casual Shirt": 4.1,
        "Majestic Man Men’s Pure Cotton Striped Half Sleeve Regular Fit Shirt": 4.3,
        "Lux Cozi Men’s Polo T-Shirt": 5.0,
        "Louis Philippe Men's Slim Fit Single-Tuck Pique Stylized Sleeve Print": 4.0,
        "Kavora Men’s Solid Polo T-Shirt": 3.4,
        "KAJARU Men's Polyster Blend Regular Fit T-Shirt": 4.1,
        "Bacca Bucci Men Lace Up Basketball Shoe": 4.2,
        "Bacca Bucci Men Lace Up Sneaker Shoes": 4.2,
        "Bacca Bucci Men Lace Up Running Shoes": 3.8,
        "Bacca Bucci Men Lace Up Athletic Shoes": 3.9,
    }
    rating = ratings_map.get(product.producttitle.strip(), 5.0)

    if product.productmrpprice and product.productprice and product.productmrpprice > product.productprice:
        discount = int(((product.productmrpprice - product.productprice) / product.productmrpprice) * 100)
    else:
        discount = 0
    if request.method == "POST":
        Review.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product=product,
            rating=request.data.get("rating"),
            review=request.data.get("review"),
            image=request.FILES.get("image"),
            size=request.data.get("size"),
            color=request.data.get("color"),
            country=request.data.get("country"),
        )
        return Response({
            "status": True,
            "message": "Review added successfully"
        })
    variants = Productview.objects.filter(
        producttitle=product.producttitle
    ).order_by("-productviewid")
    paginator = Paginator(variants, 10)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    reviews = Review.objects.filter(product=product).order_by("-created_at")[:7]
    return Response({
        "status": True,
        "category": CategorySerializer(category).data,
        "product": ProductViewSerializer(product).data,
        "view_count": view_count,
        "likes": likes,
        "dislikes": dislikes,
        "rating": rating,
        "discount": discount,
        "variants": ProductViewSerializer(page_obj, many=True).data,
        "reviews": ReviewSerializer(reviews, many=True).data,
        "all_reviews_count": Review.objects.filter(product=product).count(),
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
    })
@api_view(['POST'])
def product_reaction(request, productviewid):
    product = Productview.objects.get(productviewid=productviewid)
    reaction = request.data.get("reaction")
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    if reaction not in ['like', 'dislike']:
        return Response({"status": False, "message": "Invalid reaction"}, status=400)
    if request.user.is_authenticated:
        ProductReaction.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={"reaction": reaction}
        )
    else:
        ProductReaction.objects.update_or_create(
            product=product,
            session_key=session_key,
            defaults={"reaction": reaction}
        )
    return Response({
        "status": True,
        "message": f"You {reaction}d this product"
    })
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, reviewid):
    try:
        review = Review.objects.get(reviewid=reviewid)
        if review.user != request.user:
            return Response({
                "status": False,
                "message": "You are not authorized to delete this review."
            }, status=403)
        review.delete()
        return Response({
            "status": True,
            "message": "Review deleted successfully."
        })
    except Review.DoesNotExist:
        return Response({
            "status": False,
            "message": "Review not found."
        }, status=404)
@api_view(['GET'])
def profile(request, user_id):
    try:
        profile_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({
            "status": False,
            "message": "User not found"
        }, status=404)
    reviews = Review.objects.filter(
        user=profile_user
    ).select_related(
        'user', 'product'
    ).order_by('-created_at')
    product_views = Productview.objects.none()
    if request.user.is_authenticated:
        product_views = Productview.objects.filter(
            productviewid__in=Review.objects.filter(
                user=profile_user
            ).values_list('product_id', flat=True)
        )
    return Response({
        "status": True,
        "profile_user": {
            "id": profile_user.id,
            "username": profile_user.username,
            "first_name": profile_user.first_name,
            "last_name": profile_user.last_name,
            "email": profile_user.email,
        },
        "reviews": ReviewSerializer(reviews, many=True).data,
        "product_views": ProductViewSerializer(product_views, many=True).data,
    })
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def addtocart(request, id):
    try:
        product = Productview.objects.get(productviewid=id)
    except Productview.DoesNotExist:
        return Response({
            "status": False,
            "message": "Product not found."
        }, status=404)

    cartdata = cart.objects.filter(
        userid=request.user,
        product_id=product
    )

    if cartdata.exists():
        return Response({
            "status": False,
            "message": "Product already added to cart."
        })

    cart_item = cart.objects.create(
        product_id=product,
        userid=request.user,
        quantity=1,
    )

    return Response({
        "status": True,
        "message": "Product added to cart successfully.",
        "cartid": cart_item.cartid,
        "quantity": cart_item.quantity,
        "product": product.producttitle,
        "category": product.category_id.categoryname,
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cartdata = cart.objects.filter(
        userid=request.user
    ).order_by('-cartid')
    serializer = CartSerializer(cartdata, many=True)
    last_item = cartdata.first()
    if last_item:
        category_id = last_item.product_id.category_id.categoryid
        category_name = last_item.product_id.category_id.categoryname
        producttitle = last_item.product_id.producttitle
    else:
        category_id = None
        category_name = None
        producttitle = None
    return Response({
        "status": True,
        "cart": serializer.data,
        "category_id": category_id,
        "category_name": category_name,
        "producttitle": producttitle,
    })
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove(request, cartid):
    try:
        cart_item = cart.objects.get(
            userid=request.user,
            cartid=cartid
        )
        cart_item.delete()
        return Response({
            "status": True,
            "message": "Product removed from cart successfully."
        })
    except cart.DoesNotExist:
        return Response({
            "status": False,
            "message": "Cart item not found."
        }, status=404)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def minus(request, cartid):
    try:
        cartdata = cart.objects.get(
            userid=request.user,
            cartid=cartid
        )
        if cartdata.quantity > 1:
            cartdata.quantity -= 1
            cartdata.save()
        return Response({
            "status": True,
            "message": "Quantity decreased successfully.",
            "quantity": cartdata.quantity
        })
    except cart.DoesNotExist:
        return Response({
            "status": False,
            "message": "Cart item not found."
        }, status=404)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def plus(request, cartid):
    try:
        cartdata = cart.objects.get(
            userid=request.user,
            cartid=cartid
        )
        cartdata.quantity += 1
        cartdata.save()
        return Response({
            "status": True,
            "message": "Quantity increased successfully.",
            "quantity": cartdata.quantity
        })
    except cart.DoesNotExist:
        return Response({
            "status": False,
            "message": "Cart item not found."
        }, status=404)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    cartdata = cart.objects.filter(userid=request.user).order_by('-cartid')
    if request.method == "GET":
        data = []
        for item in cartdata:
            data.append({
                "cartid": item.cartid,
                "product": item.product_id.producttitle,
                "price": item.product_id.productprice,
                "quantity": item.quantity,
                "total": item.product_id.productprice * item.quantity,
            })
        return Response({
            "status": True,
            "cart": data
        })
    firstname = request.data.get("firstname")
    lastname = request.data.get("lastname")
    email = request.data.get("email")
    number = request.data.get("number")
    address = request.data.get("address")
    city = request.data.get("city")
    pincode = request.data.get("pincode")
    state = request.data.get("state")
    country = request.data.get("country")
    subtotal = request.data.get("subtotal")
    deliverycharges = request.data.get("deliverycharges")
    total = request.data.get("total")
    paymentmethod = request.data.get("paymentmethod")

    order = Order.objects.create(
        firstname=firstname,
        lastname=lastname,
        email=email,
        number=number,
        username=request.user.username,
        address=address,
        city=city,
        pincode=pincode,
        state=state,
        country=country,
        subtotal=subtotal,
        deliverycharges=deliverycharges,
        total=total,
        paymentmethod=paymentmethod,
        user_id=request.user,
        otracker_id=Otracker.objects.get(otrackerid=1)
    )

    for item in cartdata:
        Orderitem.objects.create(
            productview_id=item.product_id,
            order_id=order,
            quantity=item.quantity
        )

    cartdata.delete()
    return Response({
        "status": True,
        "message": "Order placed successfully.",
        "orderid": order.orderid
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def thankyou(request, orderid):
    try:
        order = Order.objects.get(orderid=orderid, user_id=request.user)
    except Order.DoesNotExist:
        return Response({
            "status": False,
            "message": "Order not found."
        }, status=404)
    return Response({
        "status": True,
        "message": "Order placed successfully.",
        "username": request.user.username,
        "order": {
            "orderid": order.orderid,
            "firstname": order.firstname,
            "lastname": order.lastname,
            "email": order.email,
            "number": order.number,
            "address": order.address,
            "city": order.city,
            "pincode": order.pincode,
            "state": order.state,
            "country": order.country,
            "subtotal": order.subtotal,
            "deliverycharges": order.deliverycharges,
            "total": order.total,
            "paymentmethod": order.paymentmethod,
        }
    })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def conformorder(request, orderid):
    order = get_object_or_404(
        Order,
        orderid=orderid,
        user_id=request.user
    )
    orderitems = Orderitem.objects.filter(
        order_id=order
    ).select_related("productview_id")
    user_order_no = Order.objects.filter(
        user_id=request.user,
        orderid__lte=order.orderid
    ).count()
    amazon_order_id = f"ORD{user_order_no:06d}"
    return Response({
        "status": True,
        "username": request.user.username,
        "user_order_no": user_order_no,
        "amazon_order_id": amazon_order_id,
        "order": OrderSerializer(order).data,
        "orderitems": OrderItemSerializer(orderitems, many=True).data,
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def myorder(request):
    orders = Order.objects.filter(
        user_id=request.user
    ).order_by('-orderid')
    order_list = []
    for order in orders:
        user_order_no = Order.objects.filter(
            user_id=request.user,
            orderid__lte=order.orderid
        ).count()
        amazon_order_id = f"ORD{user_order_no:06d}"
        order_data = OrderSerializer(order).data
        order_data["user_order_no"] = user_order_no
        order_data["amazon_order_id"] = amazon_order_id
        order_list.append(order_data)
    return Response({
        "status": True,
        "username": request.user.username,
        "orders": order_list
    })
@api_view(['GET'])
def customerreview(request, categoryid, productviewid):
    try:
        category = Category.objects.get(categoryid=categoryid)
        productview = Productview.objects.get(productviewid=productviewid)
    except (Category.DoesNotExist, Productview.DoesNotExist):
        return Response({
            "status": False,
            "message": "Category or Product not found."
        }, status=404)
    reviews = Review.objects.filter(
        product=productview
    ).select_related("user").order_by("-created_at")
    return Response({
        "status": True,
        "category": CategorySerializer(category).data,
        "product": ProductViewSerializer(productview).data,
        "reviews": ReviewSerializer(reviews, many=True).data,
        "total_reviews": reviews.count(),
    })
@api_view(['GET'])
def search_product(request):
    query = request.GET.get("q", "").strip()
    products = Productview.objects.all()
    if query:
        search_text = query.lower().replace(" ", "")
        matched_products = []
        for product in products:
            title = (product.producttitle or "").lower().replace(" ", "")
            name = (product.productname or "").lower().replace(" ", "")
            cat = (product.category_id.categoryname or "").lower().replace(" ", "")
            if (
                search_text in title
                or search_text in name
                or search_text in cat
            ):
                matched_products.append(product)
        products = matched_products
    paginator = Paginator(products, 25)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    ratings_map = {
        "majestic man men classic slim fit pure cotton casual shirt": 4.0,
        "majestic man comfort slim fit pure cotton checked casual shirt": 4.1,
        "majestic man men’s pure cotton striped half sleeve regular fit shirt": 4.3,
        "lux cozi men’s polo t-shirt comfortable cotton blend, band collar, regular fit stylish & premium all day wear": 5.0,
        "louis philippe men's slim fit single-tuck pique stylized sleeve print and contrast tipping half sleeve solid polo tshirt": 4.0,
        "kavora men’s solid polo t-shirt short sleeve regular fit soft breathable fabric casual & smart wear button placket collar top": 3.4,
        "kajaru men's polyster blend regular fit t-shirt with half sleeve chain polo collar v-neck standard length and classic style": 4.1,
        "bacca bucci men lace up basketball shoe": 4.2,
        "bacca bucci men lace up sneaker shoes": 4.2,
        "bacca bucci men lace up running shoes": 3.8,
        "bacca bucci men lace up athletic shoes": 3.9,
    }
    product_list = []
    for product in page_obj:
        title = (product.producttitle or "").strip().lower()
        rating = ratings_map.get(title, 5.0)
        if (
            product.productmrpprice
            and product.productprice
            and product.productmrpprice > product.productprice
        ):
            discount = int(
                (
                    (product.productmrpprice - product.productprice)
                    / product.productmrpprice
                ) * 100
            )
        else:
            discount = 0
        data = ProductViewSerializer(product).data
        data["rating"] = rating
        data["discount"] = discount
        product_list.append(data)
    selected_category = None
    if products:
        first_product = (
            products[0]
            if isinstance(products, list)
            else products.first()
        )
        if first_product:
            selected_category = CategorySerializer(
                first_product.category_id
            ).data
    return Response({
        "status": True,
        "query": query,
        "selected_category": selected_category,
        "products": product_list,
        "current_page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_results": paginator.count,
    })