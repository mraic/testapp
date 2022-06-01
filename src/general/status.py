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
