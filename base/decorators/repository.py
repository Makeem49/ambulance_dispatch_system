import re
import logging
from functools import wraps
from django.db import IntegrityError, DatabaseError
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.transaction import TransactionManagementError


logger = logging.getLogger(__name__)


def handle_repository_exceptions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
            matches = re.findall(r"\((.*?)\)", str(e))
            if "unique constraint" in str(e):
                error = f"This entry must be unique {matches}. Please check your data and try again."
            elif "foreign key constraint" in str(e):
                error = f"The specified related entry does not exist {matches}. Please make sure all referenced entries are valid."
            else:
                error = "There was an error processing your request. Please check your data and try again."
            logger.error(f"IntegrityError: {str(e)}")
            return None, error

        except ValidationError as e:
            error = f"Validation error: {str(e)}"
            logger.error(f"ValidationError: {str(e)}")
            return None, error

        except DatabaseError as e:
            error = f"Database error: {str(e)}"
            logger.error(f"DatabaseError: {str(e)}")
            return None, error

        except ObjectDoesNotExist as e:
            error = f"Record does not exist: {str(e)}"
            logger.error(f"ObjectDoesNotExist: {str(e)}")
            return None, error

        except TransactionManagementError as e:
            error = f"Transaction management error: {str(e)}"
            logger.error(f"TransactionManagementError: {str(e)}")
            return None, error

        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            logger.error(f"UnexpectedError: {str(e)}")
            return None, error

    return wrapper
