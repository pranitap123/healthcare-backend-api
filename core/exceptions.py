import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

CODES = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: "unsupported_media_type",
    status.HTTP_429_TOO_MANY_REQUESTS: "throttled",
}


def build_error(status_code, message, details=None, code=None):
    body = {
        "status": status_code,
        "code": code or CODES.get(status_code, "error"),
        "message": message,
    }
    if details is not None:
        body["details"] = details
    return {"error": body}


def api_exception_handler(exc, context):
    if isinstance(exc, IntegrityError):
        logger.warning("Integrity error: %s", exc)
        return Response(
            build_error(status.HTTP_409_CONFLICT, "The request conflicts with existing data."),
            status=status.HTTP_409_CONFLICT,
        )

    response = exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled exception", exc_info=exc)
        return Response(
            build_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "An unexpected error occurred.",
                code="server_error",
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValidationError):
        response.data = build_error(
            response.status_code, "Validation failed.", response.data, code="validation_error"
        )
        return response

    data = response.data
    message = data.get("detail") if isinstance(data, dict) else None
    response.data = build_error(response.status_code, str(message) if message else "Request failed.")
    return response
