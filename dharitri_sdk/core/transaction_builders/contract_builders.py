from typing import Any, List, Optional, Protocol, Sequence

from dharitri_sdk.core.constants import VM_TYPE_WASM_VM
from dharitri_sdk.core.interfaces import (IAddress, ICodeMetadata, IGasLimit,
                                          IGasPrice, INonce, ITokenPayment,
                                          ITransactionValue)
from dharitri_sdk.core.serializer import arg_to_string, args_to_strings
from dharitri_sdk.core.transaction_builders.transaction_builder import (
    ITransactionBuilderConfiguration, TransactionBuilder)


class IContractDeploymentConfiguration(ITransactionBuilderConfiguration, Protocol):
    deployment_address: IAddress


class ContractDeploymentBuilder(TransactionBuilder):
    def __init__(self,
                 config: IContractDeploymentConfiguration,
                 code: bytes,
                 code_metadata: ICodeMetadata,
                 deploy_arguments: Sequence[Any],
                 owner: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.sender = owner
        self.receiver = config.deployment_address
        self.code = code
        self.code_metadata = code_metadata
        self.deploy_arguments = deploy_arguments

    def _build_payload_parts(self) -> List[str]:
        return [
            self.code.hex(),
            arg_to_string(VM_TYPE_WASM_VM),
            arg_to_string(self.code_metadata)
        ] + args_to_strings(self.deploy_arguments)


class ContractUpgradeBuilder(TransactionBuilder):
    def __init__(self,
                 config: ITransactionBuilderConfiguration,
                 contract: IAddress,
                 code: bytes,
                 code_metadata: ICodeMetadata,
                 upgrade_arguments: Sequence[Any],
                 owner: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.sender = owner
        self.receiver = contract
        self.code = code
        self.code_metadata = code_metadata
        self.upgrade_arguments = upgrade_arguments
        self.owner = owner

    def _build_payload_parts(self) -> List[str]:
        return [
            "upgradeContract",
            self.code.hex(),
            arg_to_string(self.code_metadata)
        ] + args_to_strings(self.upgrade_arguments)


class ContractCallBuilder(TransactionBuilder):
    def __init__(self,
                 config: ITransactionBuilderConfiguration,
                 contract: IAddress,
                 function_name: str,
                 call_arguments: Sequence[Any],
                 caller: IAddress,
                 nonce: Optional[INonce] = None,
                 value: Optional[ITransactionValue] = None,
                 dcdt_transfers: Sequence[ITokenPayment] = [],
                 gas_limit: Optional[IGasLimit] = None,
                 gas_price: Optional[IGasPrice] = None
                 ) -> None:
        super().__init__(config, nonce, value, gas_limit, gas_price)
        self.contract = contract
        self.function_name = function_name
        self.call_arguments = call_arguments
        self.caller = caller
        self.dcdt_transfers = dcdt_transfers

    def _get_sender(self) -> IAddress:
        return self.caller

    def _get_receiver(self) -> IAddress:
        receiver_is_same_as_sender = self._has_multiple_transfers() or self._has_single_nft_transfer()
        return self.caller if receiver_is_same_as_sender else self.contract

    def _build_payload_parts(self) -> List[str]:
        parts: List[str] = []

        if self._has_single_dcdt_transfer():
            transfer = self.dcdt_transfers[0]
            parts = [
                "DCDTTransfer",
                arg_to_string(transfer.token_identifier),
                arg_to_string(transfer.amount_as_integer),
                arg_to_string(self.function_name),
                *args_to_strings(self.call_arguments)
            ]
        elif self._has_single_nft_transfer():
            transfer = self.dcdt_transfers[0]
            parts = [
                "DCDTNFTTransfer",
                arg_to_string(transfer.token_identifier),
                arg_to_string(transfer.token_nonce),
                arg_to_string(transfer.amount_as_integer),
                self.contract.to_hex(),
                arg_to_string(self.function_name),
                *args_to_strings(self.call_arguments)
            ]
        elif self._has_multiple_transfers():
            parts = [
                "MultiDCDTNFTTransfer",
                self.contract.to_hex(),
                arg_to_string(len(self.dcdt_transfers))
            ]

            for transfer in self.dcdt_transfers:
                parts.extend([
                    arg_to_string(transfer.token_identifier),
                    arg_to_string(transfer.token_nonce),
                    arg_to_string(transfer.amount_as_integer)
                ])

            parts.extend([
                arg_to_string(self.function_name),
                *args_to_strings(self.call_arguments)
            ])
        else:
            parts = [self.function_name] + args_to_strings(self.call_arguments)

        return parts

    def _has_single_dcdt_transfer(self) -> bool:
        return len(self.dcdt_transfers) == 1 and self.dcdt_transfers[0].is_fungible()

    def _has_single_nft_transfer(self) -> bool:
        return len(self.dcdt_transfers) == 1 and not self.dcdt_transfers[0].is_fungible()

    def _has_multiple_transfers(self) -> bool:
        return len(self.dcdt_transfers) > 1
