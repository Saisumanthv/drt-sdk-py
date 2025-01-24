
from dharitri_sdk.core.address import Address
from dharitri_sdk.core.token_payment import TokenPayment
from dharitri_sdk.core.transaction_builders.default_configuration import \
    DefaultTransactionBuildersConfiguration
from dharitri_sdk.core.transaction_builders.transfers_builders import (
    DCDTNFTTransferBuilder, DCDTTransferBuilder, MultiDCDTNFTTransferBuilder,
    REWATransferBuilder)

dummyConfig = DefaultTransactionBuildersConfiguration(chain_id="D")


def test_rewa_transfer_builder():
    alice = Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")
    bob = Address.new_from_bech32("drt1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqlqde3c")
    payment = TokenPayment.rewa_from_amount("1.00")

    # With "data" field
    builder = REWATransferBuilder(
        config=dummyConfig,
        sender=alice,
        receiver=bob,
        payment=payment,
        data="for the book"
    )

    payload = builder.build_payload()
    tx = builder.build()
    assert payload.data == b"for the book"
    assert tx.chain_id == "D"
    assert tx.sender == alice.to_bech32()
    assert tx.receiver == bob.to_bech32()
    assert tx.gas_limit == 50000 + payload.length() * 1500
    assert tx.data.decode() == str(payload)

    # Without "data" field
    builder = REWATransferBuilder(
        config=dummyConfig,
        sender=alice,
        receiver=bob,
        payment=payment
    )

    payload = builder.build_payload()
    tx = builder.build()
    assert payload.data == b""
    assert tx.chain_id == "D"
    assert tx.sender == alice.to_bech32()
    assert tx.receiver == bob.to_bech32()
    assert tx.gas_limit == 50000
    assert tx.data.decode() == str(payload)


def test_dcdt_transfer_builder():
    alice = Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")
    bob = Address.new_from_bech32("drt1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqlqde3c")
    payment = TokenPayment.fungible_from_amount("COUNTER-8b028f", "100.00", 2)

    builder = DCDTTransferBuilder(
        config=dummyConfig,
        sender=alice,
        receiver=bob,
        payment=payment
    )

    payload = builder.build_payload()
    tx = builder.build()
    assert payload.data == b"DCDTTransfer@434f554e5445522d386230323866@2710"
    assert tx.chain_id == "D"
    assert tx.sender == alice.to_bech32()
    assert tx.receiver == bob.to_bech32()
    assert tx.gas_limit == 50000 + payload.length() * 1500 + 100000 + 200000
    assert tx.data.decode() == str(payload)


def test_dcdt_nft_transfer_builder():
    alice = Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")
    bob = Address.new_from_bech32("drt1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqlqde3c")
    payment = TokenPayment.non_fungible("TEST-38f249", 1)

    builder = DCDTNFTTransferBuilder(
        config=dummyConfig,
        sender=alice,
        destination=bob,
        payment=payment
    )

    payload = builder.build_payload()
    tx = builder.build()
    assert payload.data == b"DCDTNFTTransfer@544553542d333866323439@01@01@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"
    assert tx.chain_id == "D"
    assert tx.sender == alice.to_bech32()
    assert tx.receiver == alice.to_bech32()
    assert tx.gas_limit == 50000 + payload.length() * 1500 + 200000 + 800000
    assert tx.data.decode() == str(payload)


def test_multi_dcdt_nft_transfer_builder():
    alice = Address.new_from_bech32("drt1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssey5egf")
    bob = Address.new_from_bech32("drt1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqlqde3c")

    payment_one = TokenPayment.non_fungible("TEST-38f249", 1)
    payment_two = TokenPayment.fungible_from_amount("BAR-c80d29", "10.00", 18)

    builder = MultiDCDTNFTTransferBuilder(
        config=dummyConfig,
        sender=alice,
        destination=bob,
        payments=[payment_one, payment_two]
    )

    payload = builder.build_payload()
    tx = builder.build()
    assert payload.data == b"MultiDCDTNFTTransfer@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8@02@544553542d333866323439@01@01@4241522d633830643239@@8ac7230489e80000"
    assert tx.chain_id == "D"
    assert tx.sender == alice.to_bech32()
    assert tx.receiver == alice.to_bech32()
    assert tx.gas_limit == 50000 + payload.length() * 1500 + 2 * (200000 + 800000)
    assert tx.data.decode() == str(payload)
