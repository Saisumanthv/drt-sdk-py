from dharitri_sdk.core.proto.transaction_serializer import ProtoSerializer
from dharitri_sdk.core.transaction import Transaction
from dharitri_sdk.core.transaction_computer import TransactionComputer
from dharitri_sdk.testutils.wallets import load_wallets


class TestProtoSerializer:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]
    carol = wallets["carol"]
    proto_serializer = ProtoSerializer()
    transaction_computer = TransactionComputer()

    def test_serialize_tx_no_data_no_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=50000,
            chain_id="local-testnet",
            nonce=89,
            value=0,
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "0859120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340d08603520d6c6f63616c2d746573746e657458026240958869289b34a7c1ca0cab0c214c3a0c7ba7bb352162f8d369ba948d82ce02f0cf7258ce8b28833dc3cb00c39a9533034b6e7b4e02a46c8435219350eb467700"

    def test_serialize_tx_with_data_no_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=80000,
            chain_id="local-testnet",
            data=b"hello",
            nonce=90
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "085a120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc034080f1044a0568656c6c6f520d6c6f63616c2d746573746e657458026240878ae4f7309e7a303182a28fd649a24973f107566634b14b3ad4d3928489b917df327e85add77495e85aeaf3620f92f98388cebe3603dd18480bdf25d467250b"

    def test_serialize_tx_with_data_and_value(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            gas_limit=100000,
            chain_id="local-testnet",
            nonce=92,
            data=b"for the spaceship",
            value=123456789000000000000000000000
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "085c120e00018ee90ff6181f3761632000001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc0340a08d064a11666f722074686520737061636573686970520d6c6f63616c2d746573746e657458026240ce2fd0f2dab851612366151f6896bd83673a4409bb76714311c15c813289831b49fb954bd747a691f20bc6b29f4f66f06d7f94b2296f823a86531055fa5c010e"

    def test_serialize_tx_with_nonce_zero(self):
        transaction = Transaction(
            sender=self.alice.label,
            receiver=self.bob.label,
            chain_id="local-testnet",
            gas_limit=80000,
            nonce=0,
            value=0,
            data=b"hello",
            version=1
        )
        transaction.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "120200001a208049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f82a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1388094ebdc034080f1044a0568656c6c6f520d6c6f63616c2d746573746e657458016240a46d0601db75691aafd16d14d44aaec73cdb3dcbf80aa72ebfaf8361a143714c851dbba72c3689a8a397f8f6ed6288f48efbd5c5bc6c7a74ae1482f38c4e8e03"

    def test_serialized_tx_with_usernames(self):
        transaction = Transaction(
            sender=self.carol.label,
            receiver=self.alice.label,
            gas_limit=50000,
            chain_id="T",
            nonce=204,
            value=1000000000000000000,
            sender_username="carol",
            receiver_username="alice"
        )
        transaction.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(transaction))

        serialized_transaction = self.proto_serializer.serialize_transaction(transaction)
        assert serialized_transaction.hex() == "08cc011209000de0b6b3a76400001a200139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e12205616c6963652a20b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba32056361726f6c388094ebdc0340d08603520154580262405ac790366634a107930f4e47ef0e67b5e8f61503441bd38bc7cd12556f149b8edb43c08eedb7505e32e473f549ca598462388a11cecc917dd638968cd6178c06"
