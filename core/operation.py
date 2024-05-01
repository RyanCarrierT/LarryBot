class Operation:
    """
    This class is intended to model a planned operation.

    Class Attributes:
        ...

    Instance Attributes:
        ...

    Methods:
        ...
    """

    def __init__(self, operation_id: str, operation_type: str, currency: str, price: float, quantity: float):
        self.operation_id = operation_id
        self.operation_type = operation_type
        self.currency = currency
        self.price = price
        self.quantity = quantity
        self.realized = False