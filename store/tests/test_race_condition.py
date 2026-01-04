from django.test import TestCase
from django.contrib.auth.models import User
from store.models import UserCoin, CoinTransaction
from django.db.models import F
import threading
from django.db import transaction

class UserCoinRaceConditionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcoinuser', password='password')
        self.user_coin = UserCoin.objects.create(user=self.user, balance=100)

    def test_spend_coins_race_condition(self):
        """
        Test that spend_coins correctly handles atomic updates.
        We simulate a scenario where one thread tries to spend coins but another has already modified it.
        Or simply verify that the logic is correct even with stale objects.
        """

        # Create two references to the same object (simulating two threads/requests)
        coin_ref1 = UserCoin.objects.get(id=self.user_coin.id)
        coin_ref2 = UserCoin.objects.get(id=self.user_coin.id)

        # Initial balance 100

        # Ref1 spends 50
        coin_ref1.spend_coins(50)
        # DB should be 50. Ref1 object is refreshed.
        self.assertEqual(coin_ref1.balance, 50)

        # Ref2 still has stale balance 100 in memory
        self.assertEqual(coin_ref2.balance, 100)

        # Ref2 tries to spend 50.
        # With unsafe implementation (balance -= 50), it would set balance to 50 (100 - 50).
        # With safe implementation (F('balance') - 50), it executes UPDATE ... SET balance = balance - 50.
        # So DB balance (50) - 50 = 0.

        coin_ref2.spend_coins(50)

        # Ref2 should reflect the new DB state after refresh
        self.assertEqual(coin_ref2.balance, 0)

        self.user_coin.refresh_from_db()
        self.assertEqual(self.user_coin.balance, 0, "Atomic update failed: Balance should be 0")

    def test_add_coins_race_condition(self):
        """
        Test that add_coins correctly handles atomic updates.
        """
        coin_ref1 = UserCoin.objects.get(id=self.user_coin.id)
        coin_ref2 = UserCoin.objects.get(id=self.user_coin.id)

        # Initial 100

        # Ref1 adds 50 -> DB: 150
        coin_ref1.add_coins(50)
        self.assertEqual(coin_ref1.balance, 150)

        # Ref2 stale memory: 100
        # Ref2 adds 50.
        # Unsafe: 100 + 50 = 150.
        # Safe: DB(150) + 50 = 200.
        coin_ref2.add_coins(50)

        self.assertEqual(coin_ref2.balance, 200)

        self.user_coin.refresh_from_db()
        self.assertEqual(self.user_coin.balance, 200, "Atomic update failed: Balance should be 200")

    def test_insufficient_funds_race(self):
        """
        Test insufficient funds with stale object.
        """
        coin_ref1 = UserCoin.objects.get(id=self.user_coin.id) # 100

        # Spend 90 elsewhere
        UserCoin.objects.filter(id=self.user_coin.id).update(balance=10)

        # Ref1 thinks it has 100, tries to spend 20.
        # Should fail because DB has 10.

        with self.assertRaises(ValueError):
            coin_ref1.spend_coins(20)

        coin_ref1.refresh_from_db()
        self.assertEqual(coin_ref1.balance, 10)
