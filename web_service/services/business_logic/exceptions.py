class FileVerificationException(ValueError):
    def __init__(self, message: str = 'File verification - FAILED'):
        self.message = message
        super().__init__(self.message)
