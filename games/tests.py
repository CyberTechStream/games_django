from django.test import TestCase
from .models import *
# Create your tests here.

class GameModelTest(TestCase):

    def setUp(self):
        self.game = Game.objects.create(
            title="Test game",
            description="test123",
            genre="test",
            release_year=2025,
            price=100,
            discount=20
        )
    def test_str_method(self):
        self.assertEqual(str(self.game), "Test game")

    def test_sell_price_with_discount(self):
        self.assertEqual(self.game.sell_price, 80)

    def test_sell_price_without_discount(self):
        self.game.discount = 0
        self.assertEqual(self.game.sell_price, 100)

from django.contrib.auth.models import User

class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test321",
            password="123456",
        )

    def test_profile_created(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())


from django.urls import reverse
class GameListModelTest(TestCase):

    def setUp(self):
        self.game = Game.objects.create(
            title="Test game",
            description="test123",
            genre="test",
            release_year=2025,
            price=100,
            discount=20
        )

    def test_game_list_status_code(self):
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 200)

    def test_game_list_contains_game(self):
        response = self.client.get(reverse("game_list"))
        self.assertContains(response, "Test game")

class LoginTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="test321",
            password="123456",
        )
    
    def test_login(self):
        response = self.client.post(reverse('login'), {
            "username": "test321",
            "password": "123456"
        })
        self.assertEqual(response.status_code, 302)

class CartTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            title="Test game",
            description="test123",
            genre="test",
            release_year=2025,
            price=100,
            discount=20
        )
    
    def test_add_to_cart(self):
        response = self.client.get(reverse("add_to_cart"), args=[self.game.id])

        session = self.client.session
        self.assertIn(str(self.game.id), session["cart"])
