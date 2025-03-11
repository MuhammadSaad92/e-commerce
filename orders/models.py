from django.db import models
from django.contrib.auth.models import User
from products.models import Product  # Assuming you have a Product model

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order_history")
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )

    def get_total_cost(self):
        return sum(item.quantity * item.price for item in self.items.all())

    def save(self, *args, **kwargs):
        if self.pk:
            self.total_price = self.get_total_cost()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        """Calculate the total price for this item."""
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        """Ensure price is set correctly when saving."""
        if not self.price:  
            self.price = self.product.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"