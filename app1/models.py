from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/',null=True,blank=True,default='default.jpg')
    def __str__(self):
        return self.user.username
class Category(models.Model):
    categoryid = models.AutoField(primary_key=True)
    categoryname = models.CharField(max_length=100)
    def __str__(self):
        return self.categoryname
class Productview(models.Model):
    productviewid = models.AutoField(primary_key=True)
    category_id = models.ForeignKey(Category,on_delete=models.CASCADE)
    productimage1 = models.URLField(blank=True, null=True)
    productimage2 = models.URLField(blank=True, null=True)
    productimage3 = models.URLField(blank=True, null=True)
    productimage4 = models.URLField(blank=True, null=True)
    productimage5 = models.URLField(blank=True, null=True)
    productimage6 = models.URLField(blank=True, null=True)
    productimage7 = models.URLField(blank=True, null=True)
    productimage8 = models.URLField(blank=True, null=True)
    productimage9 = models.URLField(blank=True, null=True)
    productimage10 = models.URLField(blank=True, null=True)
    productname = models.CharField(max_length=100)
    producttitle = models.TextField()
    productprice = models.BigIntegerField()
    productmrpprice = models.IntegerField()
    productdiscountrate = models.CharField(max_length=20)
    productsize = models.CharField(max_length=100)
    productsize1 = models.CharField(max_length=100)
    productsize2 = models.CharField(max_length=100)
    productsize3 = models.CharField(max_length=100)
    productcolor1 = models.CharField(max_length=20, blank=True, null=True)
    productcolor2 = models.CharField(max_length=20, blank=True, null=True)
    productcolor3 = models.CharField(max_length=20, blank=True, null=True)
    productcolor4 = models.CharField(max_length=20, blank=True, null=True)
    productcolor5 = models.CharField(max_length=20, blank=True, null=True)
    productrating = models.DecimalField(max_digits=2,decimal_places=1,default=4.0)
    producttophighlights1 = models.CharField(max_length=100)
    producttophighlights2 = models.CharField(max_length=100)
    producttophighlights3 = models.CharField(max_length=100)
    producttophighlights4 = models.CharField(max_length=100)
    producttophighlights5 = models.CharField(max_length=100)
    producttophighlights6 = models.CharField(max_length=100)
    productaboutitem1 = models.CharField(max_length=150)
    productaboutitem2 = models.CharField(max_length=150)
    productaboutitem3 = models.CharField(max_length=150)
    productaboutitem4 = models.CharField(max_length=150)
    productaboutitem5 = models.CharField(max_length=150)
    productitemdetail1 = models.CharField(max_length=100)
    productitemdetail2 = models.CharField(max_length=100)
    productitemdetail3 = models.CharField(max_length=100)
    productitemdetail4 = models.CharField(max_length=100)
    def __str__(self):
        return self.producttitle
class ProductViewCount(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    product = models.ForeignKey(Productview, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_product_user'
            ),
            models.UniqueConstraint(
                fields=['product', 'session_key'],
                name='unique_product_session'
            ),
        ]
class ProductReaction(models.Model):
    REACTION_CHOICES = (
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    )
    product = models.ForeignKey(Productview, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_product_user_reaction'
            ),
            models.UniqueConstraint(
                fields=['product', 'session_key'],
                name='unique_product_session_reaction'
            ),
        ]
class Topproduct(models.Model):
    topproductid = models.AutoField(primary_key=True)
    product_viewid = models.ForeignKey(Productview,on_delete=models.CASCADE)
    productimage1 = models.URLField(blank=True, null=True)
    producttitle = models.TextField()
    def __str__(self):
        return self.producttitle
class cart(models.Model):
    cartid = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Productview,on_delete=models.CASCADE)
    userid = models.ForeignKey(User,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    def __str__(self):
        return self.userid.username
    def subtotal(self):
        return self.product_id.productprice * self.quantity
class Otracker(models.Model):
    otrackerid = models.AutoField(primary_key=True)
    status = models.CharField(max_length=100)
    def __str__(self):
        return self.status
class Order(models.Model):
    orderid = models.AutoField(primary_key=True)
    otracker_id = models.ForeignKey(Otracker,on_delete=models.CASCADE)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=15)
    username = models.CharField(max_length=40)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    country = models.CharField(max_length=40)
    subtotal = models.IntegerField()
    deliverycharges = models.IntegerField()
    total = models.IntegerField()
    paymentmethod = models.CharField(max_length=40)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user_id.username
class Orderitem(models.Model):
    orderitemid = models.AutoField(primary_key=True)
    productview_id = models.ForeignKey(Productview,on_delete=models.CASCADE)
    order_id = models.ForeignKey(Order,on_delete=models.CASCADE)
    quantity = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return f"{self.productview_id.producttitle} - {self.order_id.user_id.username}"
class Review(models.Model):
    reviewid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Productview,on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)
    size = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.user.username