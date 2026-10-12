class PaymentDataViolation:
    def store_user_card_violation(self, user_id, credit_card_number):
        # SEC04 Violation: Storing sensitive credit card PII in plaintext in database
        db.execute("INSERT INTO payment_cards (user_id, card_number) VALUES (?, ?)", (user_id, credit_card_number))

class PaymentDataSafe:
    def store_user_card_safe(self, user_id, credit_card_number, cipher):
        # SEC04 Safe: Encrypts sensitive credit card numbers with AES-256 before storage
        encrypted_card = cipher.encrypt(credit_card_number.encode())
        db.execute("INSERT INTO payment_cards (user_id, card_number) VALUES (?, ?)", (user_id, encrypted_card))
