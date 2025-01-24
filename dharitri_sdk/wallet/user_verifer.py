from dharitri_sdk.core.address import Address
from dharitri_sdk.wallet.interfaces import IAddress, ISignature
from dharitri_sdk.wallet.user_keys import UserPublicKey


class UserVerifier:
    def __init__(self, public_key: UserPublicKey) -> None:
        self.public_key = public_key

    @classmethod
    def from_address(cls, address: IAddress) -> 'UserVerifier':
        buffer: bytes = Address.new_from_bech32(address.to_bech32()).get_public_key()
        public_key = UserPublicKey(buffer)
        return UserVerifier(public_key)

    def verify(self, data: bytes, signature: ISignature) -> bool:
        return self.public_key.verify(data, signature)
