from rest_framework import serializers
from .models import  Category,Productview,Review,cart,Order, Orderitem,ProductReaction,ProductViewCount,Topproduct,Profile
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password",
        ]
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "image",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        try:
            image = obj.profile.image

            if image:
                if request:
                    return request.build_absolute_uri(image.url)
                return image.url

        except Exception:
            pass

        return None

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
class TopproductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topproduct
        fields = "__all__"
class ProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productview
        fields = "__all__"
class ProductViewCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductViewCount
        fields = '__all__'
class ProductReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReaction
        fields = '__all__'
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "reviewid",
            "user",
            "product",
            "rating",
            "review",
            "created_at",
            "image",
            "size",
            "color",
            "country",
        ]

    def get_user(self, obj):
        return UserSerializer(
            obj.user,
            context=self.context
        ).data if obj.user else None
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = cart
        fields = "__all__"
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orderitem
        fields = "__all__"