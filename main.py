"""
Questions:
 

    1. Complete the `MiniVenmo.create_user()` method to allow our application to create new users.

    2. Complete the `User.pay()` method to allow users to pay each other. Consider the following: if user A is paying user B, user's A balance should be used if there's enough balance to cover the whole payment, if not, user's A credit card should be charged instead.

    3. Venmo has the Feed functionality, that shows the payments that users have been doing in the app. If Bobby paid Carol $5, and then Carol paid Bobby $15, it should look something like this
   

    Bobby paid Carol $5.00 for Coffee
    Carol paid Bobby $15.00 for Lunch

    Implement the `User.retrieve_activity()` and `MiniVenmo.render_feed()` methods so the MiniVenmo application can render the feed.

    4. Now users should be able to add friends. Implement the `User.add_friend()` method to allow users to add friends.
    5. Now modify the methods involved in rendering the feed to also show when user's added each other as friends.
"""

"""
MiniVenmo! Imagine that your phone and wallet are trying to have a beautiful
baby. In order to make this happen, you must write a social payment app.
Implement a program that will feature users, credit cards, and payment feeds.
"""

import re
import unittest
import uuid


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Friendship:

    def __init__(self, actor, target):
        self.actor = actor
        self.target = target

    def __str__(self):
        return f'{self.actor.username} and {self.target.username} are now friends'


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note

    def __str__(self):
        return f'{self.actor.username} paid {self.target.username} ${self.amount:.2f} for {self.note}'


class User:

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0
        self.feed_history = []
        self.friends = set()

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')

    def add_to_feed(self, feed_item):
        self.feed_history.append(feed_item)

    def retrieve_feed(self):
        return self.feed_history

    def add_friend(self, new_friend):
        if new_friend in self.friends:
            return
        self.friends.add(new_friend)
        self.add_to_feed(Friendship(actor=self, target=new_friend))
        new_friend.add_friend(self)

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        if (self.balance >= amount):
            payment_with_balance = self.pay_with_balance(target=target, amount=amount, note=note)
            self.add_to_feed(payment_with_balance)
            target.add_to_feed(Payment(amount, self, target, note))
        elif (self.balance < amount and self.balance > 0):
            remaining_amount = amount - self.balance
            payment_with_balance = self.pay_with_balance(target=target, amount=self.balance, note=note)
            payment_with_card = self.pay_with_card(target=target, amount=remaining_amount, note=note)
            self.add_to_feed(payment_with_balance)
            self.add_to_feed(payment_with_card)
            target.add_to_feed(Payment(amount, self, target, note))
            target.add_to_feed(Payment(remaining_amount, self, target, note))
        else:
            payment_with_card = self.pay_with_card(target=target, amount=amount, note=note)
            self.add_to_feed(payment_with_card)
            target.add_to_feed(Payment(amount, self, target, note))

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.balance < amount:
            raise PaymentException('User has not enough balance for the payment')

        self.balance = self.balance - amount
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        user: User = User(username=username)
        user.add_credit_card(credit_card_number=credit_card_number)
        user.add_to_balance(amount=balance)
        return user

    def render_feed(self, feed):
        for feed_item in feed:
            print(feed_item)

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")

            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):

    def test_username_validation(self):
        with self.assertRaises(UsernameException):
            User(username='invalid username')

    def test_credit_card_validation(self):
        user = User(username='valid_username')
        with self.assertRaises(CreditCardException):
            user.add_credit_card(credit_card_number='1234567890123456')

    def test_payment_validation__self_payment(self):
        user1 = User(username='valid_username1')
        user1.add_credit_card(credit_card_number='4111111111111111')

        with self.assertRaises(PaymentException):
            user1.pay(user1, 10.00, "Invalid payment to self")

    def test_payment_validation__negative_amount(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')
        user1.add_credit_card(credit_card_number='4111111111111111')

        with self.assertRaises(PaymentException):
            user1.pay(user2, -10.00, "Invalid payment with negative amount")

    def test_payment_validation__no_credit_card(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')

        with self.assertRaises(PaymentException):
            user1.pay(user2, 10.00, "Invalid payment with no credit card")

    def test_payment_validation__not_enough_balance(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')
        user1.add_credit_card(credit_card_number='4111111111111111')
        user1.add_to_balance(5.00)

        with self.assertRaises(PaymentException):
            user1.pay(user2, 10.00, "Invalid payment with not enough balance")

    def test_payment_validation__valid_payment(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')
        user1.add_credit_card(credit_card_number='4111111111111111')
        user1.add_to_balance(5.00)

        try:
            user1.pay(user2, 10.00, "Valid payment")
        except PaymentException:
            self.fail("PaymentException raised unexpectedly!")

    def test_friendship_validation(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')

        user1.add_friend(user2)

        self.assertIn(user2, user1.friends)
        self.assertIn(user1, user2.friends)

    def test_friendship_validation__duplicate_friend(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')

        user1.add_friend(user2)
        user1.add_friend(user2)

        self.assertEqual(len(user1.friends), 1)
        self.assertEqual(len(user2.friends), 1)

    def test_feed_retrieval(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')
        user1.add_credit_card(credit_card_number='4111111111111111')

        user1.pay(user2, 10.00, "Test payment")

        feed = user1.retrieve_feed()

        self.assertEqual(len(feed), 1)
        self.assertIsInstance(feed[0], Payment)
        self.assertEqual(feed[0].amount, 10.00)
        self.assertEqual(feed[0].actor, user1)
        self.assertEqual(feed[0].target, user2)
        self.assertEqual(feed[0].note, "Test payment")

    def test_friendship_feed(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')

        user1.add_friend(user2)

        feed = user1.retrieve_feed()

        self.assertEqual(len(feed), 1)
        self.assertIsInstance(feed[0], Friendship)
        self.assertEqual(feed[0].actor, user1)
        self.assertEqual(feed[0].target, user2)

    def test_friendship_feed__duplicate_friend(self):
        user1 = User(username='valid_username1')
        user2 = User(username='valid_username2')

        user1.add_friend(user2)
        user1.add_friend(user2)

        feed = user1.retrieve_feed()

        self.assertEqual(len(feed), 1)
        self.assertIsInstance(feed[0], Friendship)
        self.assertEqual(feed[0].actor, user1)
        self.assertEqual(feed[0].target, user2)

    def test_credit_card_validation__duplicate_card(self):
        user = User(username='valid_username')
        user.add_credit_card(credit_card_number='4111111111111111')

        with self.assertRaises(CreditCardException):
            user.add_credit_card(credit_card_number='4242424242424242')

    def test_credit_card_validation__valid_card(self):
        user = User(username='valid_username')

        try:
            user.add_credit_card(credit_card_number='4111111111111111')
        except CreditCardException:
            self.fail("CreditCardException raised unexpectedly!")

    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()


if __name__ == '__main__':
    MiniVenmo.run()
    # unittest.main()
