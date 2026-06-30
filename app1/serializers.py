from rest_framework import serializers
from .models import  Category,Productview,Review,cart,Order, Orderitem,ProductReaction,ProductViewCount,Topproduct
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
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
        ]
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
    username = serializers.CharField(source="user.username", read_only=True)
    profile_image = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = [
            "id",
            "username",
            "profile_image",
            "rating",
            "review",
            "image",
            "size",
            "color",
            "country",
            "created_at",
        ]

    def get_profile_image(self, obj):
        request = self.context.get("request")

        if obj.user and hasattr(obj.user, "profile") and obj.user.profile.image:
            return request.build_absolute_uri(obj.user.profile.image.url)

        return None
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