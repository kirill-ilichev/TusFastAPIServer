# TODO: think around how to customise the error message

from tusfastapiserver import TUS_RESUMABLE

from fastapi import status, HTTPException


class InvalidTusResumableException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail=f"Invalid Tus-Resumable header. Expected {TUS_RESUMABLE}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidUploadDeferLengthException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Invalid Upload-Defer-Length header",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidUploadLengthException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Invalid Upload-Length header",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class MissingUploadLengthException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Either Upload-Defer-Length or Upload-Length should be specified!",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class MissingContentTypeException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Missing Content-Type header",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InvalidContentTypeException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Invalid Content-Type header",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class InvalidMetadataException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Invalid Metadata header",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class FileNotFoundException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="File not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class MissingUploadOffsetException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Missing Upload-Offset header",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidUploadOffsetException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Invalid Upload-Offset header",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class MismatchUploadOffsetException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Mismatch between Upload-Offset and actual metadata offset",
            status_code=status.HTTP_409_CONFLICT,
        )


class MismatchUploadLengthException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            detail="Mismatch between Upload-Length and actual metadata length",
            status_code=status.HTTP_409_CONFLICT,
        )
