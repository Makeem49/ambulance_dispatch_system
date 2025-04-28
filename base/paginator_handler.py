from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class to modify the response structure and behavior.
    """

    page_size = 10  # Default items per page
    page_size_query_param = "page_size"  # Allow the client to set the page size
    max_page_size = 100  # Limit the maximum page size
    page_query_param = "page"  # Query parameter for the page number

    def calculate_page_range(self, current_page, total_pages, delta=2, edge=2):
        """
        Calculate a range of pages to display.

        Args:
            current_page (int): The current page number.
            total_pages (int): The total number of pages.
            delta (int): Number of pages to show around the current page.
            edge (int): Number of pages to always show at the start and end.

        Returns:
            list: A list of page numbers or placeholders (e.g., '...').
        """
        if total_pages <= (2 * edge + 2 * delta + 1):
            # Show all pages if the total is small
            return list(range(1, total_pages + 1))

        # Start and end pages
        range_start = list(range(1, edge + 1))
        range_end = list(range(total_pages - edge + 1, total_pages + 1))

        # Middle pages around the current page
        range_middle = list(
            range(
                max(current_page - delta, edge + 1),
                min(current_page + delta + 1, total_pages - edge + 1),
            )
        )

        # Combine ranges and add ellipses
        range_combined = []
        if range_start:
            range_combined.extend(range_start)
        if range_middle[0] > range_start[-1] + 1:
            range_combined.append("...")
        range_combined.extend(range_middle)
        if range_end[0] > range_middle[-1] + 1:
            range_combined.append("...")
        range_combined.extend(range_end)

        return range_combined

    def get_paginated_response(self, data, serializer=None, request=None):
        """
        Customizes the paginated response structure.

        Args:
            data (list): Serialized data for the current page.

        Returns:
            Response: Customized paginated response.
        """
        if serializer:
            serialized_data = serializer(
                data, context={"request": request}, many=True
            ).data

        current_page = self.page.number
        total_pages = self.page.paginator.num_pages

        pages = self.calculate_page_range(current_page, total_pages)

        return {
            "pagination": {
                "current_page": self.page.number,
                "next_page": self.get_next_link(),
                "previous_page": self.get_previous_link(),
                "total_items": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "page_size": self.get_page_size(self.request),
                "pages": pages,
            },
            "results": serialized_data,
        }
