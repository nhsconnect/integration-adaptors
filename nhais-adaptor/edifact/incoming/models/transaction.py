class TransactionPatientDetails:
    """
    A representation of the incoming edifact patient details contained in a message
    """

    def __init__(self, nhs_number):
        """
        :param nhs_number: the nhs number of the patient from the incoming edifact message.
        number of the outgoing message
        """
        self.nhs_number = nhs_number


class TransactionRegistrationDetails:
    """
    A representation of the incoming edifact registration details contained in a message
    """

    def __init__(self, transaction_number):
        """
        :param transaction_number: the transaction number from the incoming edifact message. Should match transaction
        number of the outgoing message
        """
        self.transaction_number = transaction_number


class Transaction:
    """
    From the incoming edifact message hold each transaction within a message
    """

    def __init__(self, transaction_registration: TransactionRegistrationDetails,
                 transaction_patient: TransactionPatientDetails = None):
        """
        The required details of the transactions
        :param transaction_registration: the registration details
        :param transaction_patient: the optional patient details
        """
        self.transaction_registration = transaction_registration
        self.transaction_patient = transaction_patient


class Transactions(list):
    """
    A collection of all the transactions within a message
    """

    def __init__(self, transactions):
        """
        :param transactions: a collections of the incoming transactions
        """
        self.transactions = transactions
        super().__init__(transactions)