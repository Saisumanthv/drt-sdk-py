from typing import List

from dharitri_sdk.core.address import Address
from dharitri_sdk.core.code_metadata import CodeMetadata
from dharitri_sdk.core.interfaces import ITokenPayment
from dharitri_sdk.core.token_payment import TokenPayment
from dharitri_sdk.core.transaction_builders.contract_builders import (
    ContractCallBuilder, ContractDeploymentBuilder, ContractUpgradeBuilder)
from dharitri_sdk.core.transaction_builders.default_configuration import \
    DefaultTransactionBuildersConfiguration

dummyConfig = DefaultTransactionBuildersConfiguration(chain_id="D")


def test_contract_deployment_builder():
    owner = Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")
    metadata = CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True)

    builder = ContractDeploymentBuilder(
        dummyConfig,
        owner=owner,
        deploy_arguments=[42, "test"],
        code_metadata=metadata,
        code=bytes([0xAA, 0xBB, 0xCC, 0xDD]),
        gas_limit=10000000
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"aabbccdd@0500@0506@2a@74657374"
    assert tx.chain_id == "D"
    assert tx.sender == owner.to_bech32()
    assert tx.receiver == "drt1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq85hk5z"
    assert tx.gas_limit == 10000000
    assert tx.gas_price == 1000000000
    assert tx.data.decode() == str(payload)


def test_contract_upgrade_builder():
    contract = Address.new_from_bech32("drt1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qwgcss9")
    owner = Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")
    metadata = CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True)

    builder = ContractUpgradeBuilder(
        dummyConfig,
        contract=contract,
        owner=owner,
        upgrade_arguments=[42, "test"],
        code_metadata=metadata,
        code=bytes([0xAA, 0xBB, 0xCC, 0xDD]),
        gas_limit=10000000
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"upgradeContract@aabbccdd@0506@2a@74657374"
    assert tx.chain_id == "D"
    assert tx.sender == owner.to_bech32()
    assert tx.receiver == contract.to_bech32()
    assert tx.gas_limit == 10000000
    assert tx.gas_price == 1000000000
    assert tx.data.decode() == str(payload)


def test_contract_call_builder():
    contract = Address.new_from_bech32("drt1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qwgcss9")
    caller = Address.new_from_bech32("drt1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq889n6e")

    builder = ContractCallBuilder(
        dummyConfig,
        contract=contract,
        function_name="foo",
        caller=caller,
        call_arguments=[42, "test", Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")],
        gas_limit=10000000
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"foo@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert tx.sender == caller.to_bech32()
    assert tx.receiver == contract.to_bech32()
    assert tx.gas_limit == 10000000
    assert tx.data.decode() == str(payload)


def test_contract_call_builder_with_dcdt_transfer():
    contract = Address.new_from_bech32("drt1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qwgcss9")
    caller = Address.new_from_bech32("drt1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq889n6e")

    transfers: List[ITokenPayment] = [
        TokenPayment.fungible_from_amount("COUNTER-8b028f", "100.00", 2)
    ]

    builder = ContractCallBuilder(
        dummyConfig,
        contract=contract,
        function_name="hello",
        caller=caller,
        call_arguments=[42, "test", Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")],
        gas_limit=10000000,
        dcdt_transfers=transfers
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"DCDTTransfer@434f554e5445522d386230323866@2710@68656c6c6f@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert tx.sender == caller.to_bech32()
    assert tx.receiver == contract.to_bech32()
    assert tx.data.decode() == str(payload)


def test_contract_call_builder_with_dcdt_nft_transfer():
    contract = Address.new_from_bech32("drt1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qwgcss9")
    caller = Address.new_from_bech32("drt1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq889n6e")

    transfers: List[ITokenPayment] = [
        TokenPayment.non_fungible("TEST-38f249", 1)
    ]

    builder = ContractCallBuilder(
        dummyConfig,
        contract=contract,
        function_name="hello",
        caller=caller,
        call_arguments=[42, "test", Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")],
        gas_limit=10000000,
        dcdt_transfers=transfers
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"DCDTNFTTransfer@544553542d333866323439@01@01@00000000000000000500e0b77f1edfb01cb786a39120f02c31ff5fe40aad8974@68656c6c6f@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert tx.sender == caller.to_bech32()
    assert tx.receiver == caller.to_bech32()
    assert tx.data.decode() == str(payload)


def test_contract_call_builder_with_multi_dcdt_nft_transfer():
    contract = Address.new_from_bech32("drt1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qwgcss9")
    caller = Address.new_from_bech32("drt1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq889n6e")

    transfers = [
        TokenPayment.non_fungible("TEST-38f249", 1),
        TokenPayment.fungible_from_amount("BAR-c80d29", "10.00", 18)
    ]

    builder = ContractCallBuilder(
        dummyConfig,
        contract=contract,
        function_name="hello",
        caller=caller,
        call_arguments=[42, "test", Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")],
        gas_limit=10000000,
        dcdt_transfers=transfers
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"MultiDCDTNFTTransfer@00000000000000000500e0b77f1edfb01cb786a39120f02c31ff5fe40aad8974@02@544553542d333866323439@01@01@4241522d633830643239@@8ac7230489e80000@68656c6c6f@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert tx.sender == caller.to_bech32()
    assert tx.receiver == caller.to_bech32()
    assert tx.data.decode() == str(payload)
