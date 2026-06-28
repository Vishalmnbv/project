from django.urls import path
from . import api_views

urlpatterns = [
    path("index/", api_views.index, name="index-api"),
    path("register/",api_views.register,name="register-api",),
    path('login/', api_views.login_api, name='login_api'),
    path("logout/",api_views.logout,name="logout-api",),
    path("forgetpassword/",api_views.forgetpassword,name="forgetpassword-api",),
    path("editprofile/",api_views.editprofile,name="editprofile-api",),
    path("collection/<int:categoryid>/",api_views.collection,name="collection-api",),
    path("productview/<int:categoryid>/<int:productviewid>/",api_views.productview,name="product-detail-api",),
    path('api/product/reaction/<int:productviewid>/',api_views.product_reaction,name='product_reaction'),
    path("delete_review/<int:reviewid>/",api_views.delete_review,name="delete-review-api",),
    path("profile/<int:user_id>/",api_views.profile,name="profile-api",),
    path("addtocart/<int:id>/",api_views.addtocart,name="addtocart-api",),
    path("cart/",api_views.cart_view,name="cart-api",),
    path("remove/<int:cartid>/",api_views.remove,name="remove-cart-api",),
    path("minus/<int:cartid>/",api_views.minus,name="minus-api",),
    path("plus/<int:cartid>/",api_views.plus,name="plus-api",),
    path("checkout/",api_views.checkout,name="checkout-api",),
    path("thankyou/<int:orderid>/",api_views.thankyou,name="thankyou-api",),
    path("conformorder/<int:orderid>/",api_views.conformorder,name="conformorder-api",),
    path("myorder/",api_views.myorder,name="myorder-api",),
    path("customerreview/<int:categoryid>/<int:productviewid>/",api_views.customerreview,name="customerreview-api",),
    path("search_product/",api_views.search_product,name="search-product-api",),
]
