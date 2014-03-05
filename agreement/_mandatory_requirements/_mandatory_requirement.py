from handy.ice import Ice

class MandatoryRequirement(Ice):
    def __init__(self, updater):
        self.updater = updater
        self.errors = updater.errors
        self.messages = updater.messages
        self.agreement = updater.agreement

    def check(self):
        pass

    @property
    def total_quantities(self):
        return self.updater.total_quantities

    def add_mandatory_product(self, *args, **kwargs):
        return self.updater.add_mandatory_product(*args, **kwargs)

