class SequenceKeyGenerator:
    def create_key(self, sender, recipient):
        return f'{sender}_{recipient}'