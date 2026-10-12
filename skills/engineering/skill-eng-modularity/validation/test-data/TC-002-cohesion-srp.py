# TC-002: Cohesion and Single Responsibility

# VIOLATION: Single class combining user profile, payment processing, and email formatting
class UserManagerViolation:
    def update_profile(self, user_id, name, email):
        print(f"Updating profile for {user_id}: {name}, {email}")

    def process_credit_card_payment(self, user_id, amount, card_number):
        print(f"Charging {amount} to card {card_number} for user {user_id}")

    def format_and_send_welcome_email(self, user_id, email):
        html_body = f"<h1>Welcome {user_id}</h1><p>Thanks for joining!</p>"
        print(f"Sending email to {email}: {html_body}")


# SAFE: Focused classes each with single responsibility
class UserProfileService:
    def update_profile(self, user_id, name, email):
        print(f"Updating profile for {user_id}: {name}, {email}")

class PaymentProcessor:
    def process_payment(self, user_id, amount, card_number):
        print(f"Charging {amount} to card {card_number} for user {user_id}")

class EmailNotificationService:
    def send_welcome_email(self, user_id, email):
        html_body = f"<h1>Welcome {user_id}</h1><p>Thanks for joining!</p>"
        print(f"Sending email to {email}: {html_body}")

