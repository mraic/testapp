class Status:
    def __init__(self, error_code=None, message=None):
        self.errorCode = error_code
        self.message = message

    def tuple_response(self):
        return self.errorCode, self.message

    @classmethod
    def custom_status(cls, msg):
        return cls(400, msg)

    @classmethod
    def something_went_wrong(cls):
        return cls(400, 'Something went wrong')

    @classmethod
    def successfully_processed(cls):
        return cls(200, 'Successfully processed')

    @classmethod
    def account_number_exists(cls):
        return cls(400, "Card number exists")

    @classmethod
    def user_does_not_exists(cls):
        return cls(400, "User does not exists")

    @classmethod
    def user_has_max_accounts(cls):
        return cls(400, "User has 3 accounts")

    @classmethod
    def account_does_not_exists(cls):
        return cls(400, "Account does not exists")

    @classmethod
    def account_did_not_expire(cls):
        return cls(400, "Account did not expire")

    @classmethod
    def user_is_deactivated_already(cls):
        return cls(400, "User is deactivated already")

    @classmethod
    def account_is_not_active(cls):
        return cls(400, "Account is not active")

    @classmethod
    def category_does_not_exists(cls):
        return cls(400, "Category does not exists")

    @classmethod
    def account_expired(cls):
        return cls(400, "Account expired")

    @classmethod
    def wrong_credentials(cls):
        return cls(400, "Wrong credentials. Try again!")

    @classmethod
    def insufficient_funds(cls):
        return cls(400, "Insufficient funds")

    @classmethod
    def amount_must_positive(cls):
        return cls(400, "Amount must be positive")

    @classmethod
    def account_already_exists(cls):
        return cls(400, "Account already exists")

    @classmethod
    def accounts_must_have_same_owner(cls):
        return cls(400, "Accounts must have same owner")

    @classmethod
    def user_with_email_exists(cls):
        return cls(400, "User with this email already exists")

    @classmethod
    def account_is_already_activated(cls):
        return cls(400, "Account is already activated")

    @classmethod
    def cvv_must_contain_3_digits(cls):
        return cls(400, "Cvv must contain 3 digits")
