from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile ya {self.user.username}"

# Hizi 'signals' zinahakikisha mteja akijisajili tu, profile inatengenezwa hapo hapo
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    

# 1. Meza ya Aina za Matofali (Block Types)
class BlockType(models.Model):
    name = models.CharField(max_length=100) # mf. Nchi 6 ya Shimo, Nchi 4
    price_per_block = models.DecimalField(max_digits=10, decimal_places=2)
    strength_rating = models.CharField(max_length=50) # Hii ni innovation yetu
    image = models.ImageField(upload_to='blocks/')

    def __str__(self):
        return self.name

# 2. Meza ya Maeneo ya Dodoma na Gharama za Usafiri
class DeliveryZone(models.Model):
    zone_name = models.CharField(max_length=100) # mf. Nzuguni, Mtumba, Kisasa
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.zone_name

# 3. Meza ya Oda (The International Standard Order)
# 3. Meza ya Oda (The International Standard Order)
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'), # Tumeongeza PAID
        ('LOADING', 'Loading'),
        ('TRANSIT', 'On Transit'),
        ('DELIVERED', 'Delivered'),
    ]
    block_type = models.ForeignKey(BlockType, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    delivery_zone = models.ForeignKey(DeliveryZone, on_delete=models.SET_NULL, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Hizi ndizo field zilizokosekana kule kwenye views:
    customer_phone = models.CharField(max_length=10, null=True, blank=True) 
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_phone}"