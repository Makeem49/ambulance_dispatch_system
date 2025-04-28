class DataValidator:
    """
    Handles request data validation using the provided serializer.
    """

    def __init__(self, serializer=None) -> None:
        self.serializer = serializer
        self.valid_data = None
        self.errors = None

    def validate(self, data, instance=None, partial=False):
        """
        Validate user request data.

        Args:
            data (dict): Request data to validate.

        Returns:
            None: Sets `self.valid_data` if valid, otherwise sets `self.errors`.
        """
        if self.serializer:
            serializer = self.serializer(data=data, instance=instance, partial=partial)

            if serializer.is_valid():
                self.valid_data = serializer.validated_data
            else:
                self.errors = serializer.errors
