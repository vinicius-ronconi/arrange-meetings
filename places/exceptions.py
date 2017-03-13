class PlacesException(Exception):
    pass


class InvalidRequestException(PlacesException):
    pass


class NoDataFoundException(PlacesException):
    pass


class RequestDeniedException(PlacesException):
    pass


class ExceededQuotaException(PlacesException):
    pass


STATUS_TO_EXCEPTION_MAP = {
    'INVALID_REQUEST': InvalidRequestException,
    'OVER_QUERY_LIMIT': ExceededQuotaException,
    'REQUEST_DENIED': RequestDeniedException,
    'ZERO_RESULTS': NoDataFoundException,
}
