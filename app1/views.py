from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger 
from django.db.models import Q
from .models import *
import math
from django.core.management import call_command
from django.http import HttpResponse
# Create your views here.
def index(request):
    category = Category.objects.all()
    topproduct = Topproduct.objects.all()
    product_ids = request.session.get('recently_viewed', [])
    products = list(Productview.objects.filter(productviewid__in=product_ids))
    products.sort(key=lambda x: product_ids.index(x.productviewid))
    return render(request,'index.html',{'category':category,'products':products,'topproduct':topproduct})
def register(request):
    category = Category.objects.all()
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        conformpassword = request.POST.get('conformpassword')
        image = request.FILES.get('image')
        if password!=conformpassword:
            messages.error(request,'Passwords do not match')
            return redirect('/register/')
        elif len(password)<8:
            messages.error(request,'Password must be 8 Character length')
            return redirect('/register/')
        elif User.objects.filter(username=username).exists():
            messages.error(request,'Username already taken')
            return redirect('/register/')
        elif User.objects.filter(email=email).exists():
            messages.warning(request,'Email already taken')
            return redirect('/register/')
        user = User.objects.create_user(
            first_name = firstname,
            last_name = lastname,
            username = username,
            email = email,
            password = password,
        )
        Profile.objects.create(
            user = user,
            image = image,
        )
        messages.success(request,'Account created successfully')
        return redirect('/login/')
    return render(request,'register.html',{'category':category})
def login(request):
    category = Category.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request,f'Login successful,{username}')
            return redirect('/')
        else:
            messages.error(request,'Invalid username or password')
            return redirect('/login/')
    return render(request,'login.html',{'category':category})
def logout(request):
    username = getattr(request.user,'username','User')
    auth.logout(request)
    messages.success(request,f'Successfully logged out,{username}')
    return redirect('/login/')
def forgetpassword(request):
    category = Category.objects.all()
    if request.method == 'POST':
        email = request.POST.get('email')
        newpassword = request.POST.get('newpassword')
        confirmpassword = request.POST.get('confirmpassword')
        if newpassword != confirmpassword:
            messages.error(request, "Passwords do not match!")
            return render(request, 'forgetpassword.html',{'email_val': email})
        elif len(newpassword)<8:
            messages.error(request,'Password must be 8 Character length')
            return redirect('/forgetpassword/')
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(newpassword)
            user.save()
            messages.success(request, "Password reset successful! Please login.")
            return redirect('/login/')
        else:
            messages.error(request,"No account found with this email.")
            return redirect('/forgetpassword/')
    return render(request,'forgetpassword.html',{'category':category})
def editprofile(request):
    category = Category.objects.all()
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == "POST":
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        uploaded_image = request.FILES.get('profile_image')
        try:
            user.save()
            if uploaded_image:  
                profile.image = uploaded_image
            profile.save()
            messages.success(request,'Profile updated successfully!')
            return redirect('/')
        except Exception as e:
            messages.error(request,'Username or Email already exists')
            return redirect('/editprofile/')
    return render(request,'editprofile.html',{'category':category})
def collection(request,categoryid):
    category = Category.objects.all()
    categories = Category.objects.get(categoryid=categoryid)
    productview = Productview.objects.filter(category_id=categoryid).order_by('-productviewid')
    paginator = Paginator(productview,25)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    ratings_map = {
        "Majestic Man Men Classic Slim Fit Pure Cotton Casual Shirt": 4.0,
        "Majestic Man Comfort Slim Fit Pure Cotton Checked Casual Shirt": 4.1,
        "Majestic Man Men’s Pure Cotton Striped Half Sleeve Regular Fit Shirt": 4.3,
        "Lux Cozi Men’s Polo T‑Shirt  Comfortable Cotton Blend, Band Collar, Regular Fit  Stylish & Premium All Day Wear": 5.0,
        "Louis Philippe Men's Slim Fit Single-Tuck Pique Stylized Sleeve Print and Contrast Tipping Half Sleeve Solid Polo Tshirt": 4.0,
        "Kavora Men’s Solid Polo T-Shirt  Short Sleeve  Regular Fit Soft Breathable Fabric  Casual & Smart Wear  Button Placket Collar Top": 3.4,
        "KAJARU Men's Polyster Blend Regular Fit T-Shirt with Half Sleeve Chain Polo Collar V-Neck Standard Length and Classic Style": 4.1,
        "Bacca Bucci Men Lace Up Basketball Shoe": 4.2,
        "Bacca Bucci Men Lace Up Sneaker Shoes": 4.2,
        "Bacca Bucci Men Lace Up Running Shoes": 3.8,
        "Bacca Bucci Men Lace Up Athletic Shoes": 3.9,
    }
    for product in page_obj:
        raw_rating = ratings_map.get(product.producttitle.strip(), 5.0)
        product.rating = raw_rating
        full_stars = math.floor(raw_rating)
        has_half_star = 1 if (0.3 <= (raw_rating - full_stars) <= 0.7) else 0
        if (raw_rating - full_stars) >= 0.8:
            full_stars += 1
            has_half_star = 0
        empty_stars = 5 - full_stars - has_half_star
        product.full_stars_range = range(full_stars)
        product.half_stars_range = range(has_half_star)
        product.empty_stars_range = range(max(0, empty_stars))
        if product.productmrpprice and product.productprice and product.productmrpprice > product.productprice:
            discount = ((product.productmrpprice - product.productprice) / product.productmrpprice) * 100
            product.productdiscountrate = str(int(discount)) 
        else:
            product.productdiscountrate = "0"
    return render(request,'collection.html',{'category':category,'categories':categories,'page_obj':page_obj})
def productview(request,categoryid,productviewid):
    category = Category.objects.all()
    categories = Category.objects.get(categoryid=categoryid)
    productview = Productview.objects.get(productviewid=productviewid)
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key
    if request.user.is_authenticated:
        ProductViewCount.objects.get_or_create(
            product=productview,
            user=request.user,
        )
    else:
        ProductViewCount.objects.get_or_create(
            product=productview,
            user=None,
            session_key=session_key,
        )
    view_count = ProductViewCount.objects.filter(product=productview).count()
    likes = ProductReaction.objects.filter(product=productview,reaction='like').count()
    dislikes = ProductReaction.objects.filter(product=productview,reaction='dislike').count()
    recently_viewed = request.session.get('recently_viewed', [])
    if productviewid in recently_viewed:
        recently_viewed.remove(productviewid)
    recently_viewed.insert(0, productviewid)
    recently_viewed = recently_viewed[:8]
    request.session['recently_viewed'] = recently_viewed
    request.session.modified = True
    product_variant = Productview.objects.filter(producttitle=productview.producttitle).order_by('-productviewid')
    paginator = Paginator(product_variant,10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    ratings_map = {
        "Majestic Man Men Classic Slim Fit Pure Cotton Casual Shirt": 4.0,
        "Majestic Man Comfort Slim Fit Pure Cotton Checked Casual Shirt": 4.1,
        "Majestic Man Men’s Pure Cotton Striped Half Sleeve Regular Fit Shirt": 4.3,
        "Lux Cozi Men’s Polo T‑Shirt  Comfortable Cotton Blend, Band Collar, Regular Fit  Stylish & Premium All Day Wear": 5.0,
        "Louis Philippe Men's Slim Fit Single-Tuck Pique Stylized Sleeve Print and Contrast Tipping Half Sleeve Solid Polo Tshirt": 4.0,
        "Kavora Men’s Solid Polo T-Shirt  Short Sleeve  Regular Fit Soft Breathable Fabric  Casual & Smart Wear  Button Placket Collar Top": 3.4,
        "KAJARU Men's Polyster Blend Regular Fit T-Shirt with Half Sleeve Chain Polo Collar V-Neck Standard Length and Classic Style": 4.1,
        "Bacca Bucci Men Lace Up Basketball Shoe": 4.2,
        "Bacca Bucci Men Lace Up Sneaker Shoes": 4.2,
        "Bacca Bucci Men Lace Up Running Shoes": 3.8,
        "Bacca Bucci Men Lace Up Athletic Shoes": 3.9,
    }
    raw_rating = ratings_map.get(productview.producttitle.strip(), 5.0)
    productview.rating = raw_rating
    full_stars = math.floor(raw_rating)
    has_half_star = 1 if (0.3 <= (raw_rating - full_stars) <= 0.7) else 0
    if (raw_rating - full_stars) >= 0.8:
        full_stars += 1
        has_half_star = 0
    empty_stars = 5 - full_stars - has_half_star
    productview.full_stars_range = range(full_stars)
    productview.half_stars_range = range(has_half_star)
    productview.empty_stars_range = range(max(0, empty_stars))
    if productview.productmrpprice and productview.productprice and productview.productmrpprice > productview.productprice:
            discount = ((productview.productmrpprice - productview.productprice) / productview.productmrpprice) * 100
            productview.productdiscountrate = str(int(discount)) 
    else:
            productview.productdiscountrate = "0"
    if request.method == "POST":
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')
        image = request.FILES.get('image')
        size = request.POST.get('size')
        color = request.POST.get('color')
        country = request.POST.get('country')
        Review.objects.create(
            user=request.user,
            product=productview,
            rating=rating,
            review=review_text,
            image=image,
            size=size,
            color=color,
            country=country,
        )
        messages.success(request, f'Review added successfully by {request.user.username}')
        return redirect(request.path)
    reviews = Review.objects.filter(product=productview).order_by("-created_at")[:7]
    all_reviews_count = Review.objects.filter(product=productview).count()
    return render(request,'productview.html',{'category':category,'categories':categories,'productview':productview,'page_obj':page_obj,'reviews':reviews,'all_reviews_count':all_reviews_count,'view_count':view_count,'likes':likes,'dislikes':dislikes})
def product_reaction(request, productviewid, reaction):
    product = get_object_or_404(Productview, productviewid=productviewid)
    if not request.session.session_key:
        request.session.save()
    if request.user.is_authenticated:
        ProductReaction.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'reaction': reaction}
        )
    else:
        ProductReaction.objects.update_or_create(
            product=product,
            session_key=request.session.session_key,
            defaults={'reaction': reaction}
        )
    if reaction == "like":
        messages.success(request, "You liked this product.")
    elif reaction == "dislike":
        messages.warning(request, "You disliked this product.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def delete_review(request, reviewid):
    review = Review.objects.get(reviewid=reviewid)
    review.delete()
    messages.success(request, f'Review deleted successfully by {request.user.username}')
    return redirect(request.META.get('HTTP_REFERER'))
def profile(request,user_id):
    category = Category.objects.all()
    profile_user = User.objects.get(id=user_id)
    reviews = (
        Review.objects.filter(user=profile_user).select_related('user', 'product').order_by('-created_at'))
    product_views = Productview.objects.none()
    if request.user.is_authenticated:
        product_views = (
            Review.objects.values('image').order_by('-reviewid'))
    context = {
        'reviews': reviews,
        'category': category,
        'product_views': product_views,
        'profile_user': profile_user,
    }
    return render(request, 'profile.html', context)
@login_required(login_url='register')
def Cart(request):
    category = Category.objects.all()
    cartdata = cart.objects.filter(userid=request.user).order_by('-cartid')
    last_item = cartdata.first()
    if last_item:
        category_id = last_item.product_id.category_id.categoryid
        category_name = last_item.product_id.category_id.categoryname
        producttitle = last_item.product_id.producttitle
    else:
        category_id = None
        category_name = None
        producttitle = None
    return render(request,'cart.html',{'category':category,'cartdata':cartdata,'category_id':category_id,'category_name':category_name,'producttitle':producttitle})
def remove(request,cartid):
    cartdata = cart.objects.filter(userid=request.user,cartid=cartid)
    cartdata.delete()
    return redirect('/cart/')
def minus(request,cartid):
    cartdata = cart.objects.get(userid=request.user,cartid=cartid)
    cartdata.quantity-=1
    cartdata.save()
    return redirect('/cart/')
def plus(request,cartid):
    cartdata = cart.objects.get(userid=request.user,cartid=cartid)
    cartdata.quantity+=1
    cartdata.save()
    return redirect('/cart/')
@login_required(login_url='register')
def addtocart(request, id):
    cartdata = cart.objects.filter(userid=request.user,product_id=id)
    productdata = Productview.objects.get(productviewid=id)
    if cartdata.exists():
        messages.warning(request,'Product already added')
        return redirect('/cart/')
    cart.objects.create(
        product_id=productdata,
        userid=request.user,
        quantity=1,
    )
    request.session['show_cart_breadcrumb'] = True
    request.session['cart_category_id'] = productdata.category_id.categoryid
    request.session['cart_category_name'] = productdata.category_id.categoryname
    request.session['cart_producttitle'] = productdata.producttitle
    return redirect('/cart/')
def checkout(request):
    category = Category.objects.all()
    cartdata = cart.objects.filter(userid=request.user).order_by('-cartid')
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        number = request.POST['number']
        address = request.POST['address']
        city = request.POST['city']
        pincode = request.POST['pincode']
        state = request.POST['state']
        country = request.POST['country']
        subtotal = request.POST['subtotal']
        deliverycharges = request.POST['deliverycharges']
        total = request.POST['total']
        paymentmethod = request.POST['paymentmethod']
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
        return redirect('/thankyou/' + str(order.orderid) + '/')
    return render(request,'checkout.html',{'category':category,'cartdata':cartdata})
def thankyou(request,orderid):
    try:
        order = Order.objects.get(orderid=orderid)
    except Order.DoesNotExist:
        return redirect('/')
    return render(request,'thankyou.html',{'order':order,'username': request.user.username})
def conformorder(request,orderid):
    category = Category.objects.all()
    order = get_object_or_404(Order,orderid=orderid,user_id=request.user)
    orderitems = Orderitem.objects.filter(order_id=order).select_related('productview_id')
    user_order_no = Order.objects.filter(user_id=request.user,orderid__lte=order.orderid).count()
    amazon_order_id = f"ORD{user_order_no:06d}"
    return render(request,"conformorder.html",{"order":order,"orderitems":orderitems,"username":request.user.username,"category":category,"user_order_no":user_order_no,"amazon_order_id":amazon_order_id})
@login_required(login_url='register')
def myorder(request):
    category = Category.objects.all()
    orders = Order.objects.filter(user_id=request.user).order_by('-orderid')
    for order in orders:
        order.user_order_no = Order.objects.filter(user_id=request.user,orderid__lte=order.orderid).count()
        order.amazon_order_id = f"ORD{order.user_order_no:06d}"
    return render(request,'myorder.html',{"orders":orders,"username":request.user.username,"category":category})
def customerreview(request,categoryid,productviewid):
    category = Category.objects.all()
    categories = Category.objects.get(categoryid=categoryid)
    productview = Productview.objects.get(productviewid=productviewid)
    reviews = Review.objects.filter(product=productview).select_related('user').order_by('-created_at')
    return render(request,'customerreview.html',{'category':category,'reviews':reviews,'productview':productview,'categories':categories})
def search_product(request):
    category = Category.objects.all()
    query = request.GET.get('q', '').strip()
    products = Productview.objects.all()
    if query:
        search_text = query.lower().replace(" ", "")
        matched_products = []
        for product in products:
            title = (product.producttitle or "").lower().replace(" ", "")
            name = (product.productname or "").lower().replace(" ", "")
            cat = (product.category_id.categoryname or "").lower().replace(" ", "")
            if (
                search_text in title or
                search_text in name or
                search_text in cat
            ):
                matched_products.append(product)
        products = matched_products
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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
    for product in page_obj:
        prod_title_lower = (
            product.producttitle.strip().lower()
            if product.producttitle else ""
        )
        raw_rating = ratings_map.get(prod_title_lower, 5.0)
        product.rating = raw_rating
        full_stars = math.floor(raw_rating)
        has_half_star = 1 if (0.3 <= (raw_rating - full_stars) <= 0.7) else 0
        if (raw_rating - full_stars) >= 0.8:
            full_stars += 1
            has_half_star = 0
        empty_stars = 5 - full_stars - has_half_star
        product.full_stars_range = range(full_stars)
        product.half_stars_range = range(has_half_star)
        product.empty_stars_range = range(max(0, empty_stars))
        if (
            product.productmrpprice
            and product.productprice
            and product.productmrpprice > product.productprice
        ):
            discount = (
                (product.productmrpprice - product.productprice)
                / product.productmrpprice
            ) * 100
            product.productdiscountrate = str(int(discount))
        else:
            product.productdiscountrate = "0"
    selected_category = None
    if products:
        first_product = products[0] if isinstance(products, list) else products.first()
        if first_product:
            selected_category = first_product.category_id  
    return render(request, 'search.html', {'query': query,'page_obj': page_obj,'category': category,'selected_category': selected_category})
def load_my_data(request):
    try:
        call_command('loaddata', 'db_backup.json')
        return HttpResponse("<h1>Mubarak ho! Data successfully load ho gaya hai.</h1>")
    except Exception as e:
        return HttpResponse(f"<h1>Error: {e}</h1>")