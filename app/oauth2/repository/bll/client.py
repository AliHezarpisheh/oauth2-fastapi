"""Module defines business-level logic for clients."""

from typing import ClassVar

from app.oauth2.helpers.enums import GrantTypeEnum, ResponseTypeEnum
from app.oauth2.helpers.exceptions import InvalidClientMetaDataError
from app.oauth2.helpers.messages import ClientMessages


class ClientBusinessLogicLayer:
    """Provide business logic operations."""

    GRANT_TYPE_TO_RESPONSE_TYPE: ClassVar = {
        GrantTypeEnum.AUTHORIZATION_CODE: ResponseTypeEnum.CODE,
        GrantTypeEnum.IMPLICIT: ResponseTypeEnum.TOKEN,
    }

    def validate_grant_types_and_response_types(
        self,
        grant_types: list[GrantTypeEnum],
        response_types: list[ResponseTypeEnum],
    ) -> None:
        """
        Validate that grant types have their required response types.

        Parameters
        ----------
        grant_types
            Grant types declared for the client.
        response_types
            Response types declared for the client.

        Raises
        ------
        InvalidClientMetaDataError
            If the declared response types do not exactly match those required
            by the grant types that define a corresponding response type.
        """
        valid_response_types = {
            self.GRANT_TYPE_TO_RESPONSE_TYPE[grant_type]
            for grant_type in grant_types
            if grant_type in self.GRANT_TYPE_TO_RESPONSE_TYPE
        }

        if set(response_types) != valid_response_types:
            raise InvalidClientMetaDataError(
                ClientMessages.GRANT_TYPES_AND_RESPONSE_TYPES_MISMATCH.value
            )
