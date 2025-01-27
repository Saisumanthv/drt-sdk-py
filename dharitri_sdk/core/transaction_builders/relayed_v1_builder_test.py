import pytest

from dharitri_sdk.core.address import Address
from dharitri_sdk.core.errors import ErrInvalidRelayerV1BuilderArguments
from dharitri_sdk.core.token_payment import TokenPayment
from dharitri_sdk.core.transaction import Transaction
from dharitri_sdk.core.transaction_builders.relayed_v1_builder import \
    RelayedTransactionV1Builder
from dharitri_sdk.core.transaction_computer import TransactionComputer
from dharitri_sdk.testutils.wallets import load_wallets


class NetworkConfig:
    def __init__(self) -> None:
        self.min_gas_limit = 50_000
        self.gas_per_data_byte = 1_500
        self.gas_price_modifier = 0.01
        self.chain_id = "T"


class TestRelayedV1Builder:
    wallets = load_wallets()
    alice = wallets["alice"]
    bob = wallets["bob"]
    frank = wallets["frank"]
    grace = wallets["grace"]
    carol = wallets["carol"]
    transaction_computer = TransactionComputer()

    def test_without_arguments(self):
        relayed_builder = RelayedTransactionV1Builder()

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

        inner_transaction = Transaction(
            chain_id="1",
            sender=self.alice.label,
            receiver="drt1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls6prdez",
            gas_limit=10000000,
            nonce=15,
            data=b"getContractConfig"
        )
        relayed_builder.set_inner_transaction(inner_transaction)

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

        network_config = NetworkConfig()
        relayed_builder.set_network_config(network_config)

        with pytest.raises(ErrInvalidRelayerV1BuilderArguments):
            relayed_builder.build()

    def test_compute_relayed_v1_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.bob.label,
            receiver="drt1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls6prdez",
            gas_limit=60000000,
            nonce=198,
            data=b"getContractConfig"
        )
        inner_tx.signature = self.bob.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        relayed_tx = relayed_builder.build()
        relayed_tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414141415141414141414141414141414141414141414141414141414141432f2f383d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a22566e30744e364269687150476c59526f4b77696e455a6b4b6742706d76504d7a396e4d2b652b707635695175692b47344b36704447317030633235642b5852796c424c345a626d4679597a4a5830696a7672613641513d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a327d"
        assert relayed_tx.signature.hex() == "6a4474e28873d965e46421e714a9a797be95cda78fac6c11791325b89806989261099c9dcef52712a54521f46b9bf3878273883d663df2a548438558e3ed180d"

    def test_compute_guarded_inner_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.bob.label,
            receiver="drt1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q6dlssu",
            gas_limit=60000000,
            nonce=198,
            data=b"getContractConfig",
            guardian=self.grace.label,
            version=2,
            options=2
        )
        inner_tx.signature = self.bob.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))
        inner_tx.guardian_signature = self.grace.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.new_from_bech32(self.alice.label))

        relayed_tx = relayed_builder.build()
        relayed_tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a226c52366f3333423948656f34516f757a4b6b4542516b68372b4661774d55786d76453470354c5176776261634c6b515449562b6d6b4f66424370446d316961593870414c6b30503143722b6e756265467569683341773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a2235666d3844462b777752616d626432716b3972322b6b3856327277374c755a303173577873433669336c4f566547464e4a4a526478626b7243345a544a69553648597979584636356f503734736a476143434e5742513d3d227d"
        assert relayed_tx.signature.hex() == "fc25fddeb1027b9d692c65c24042b1753678fcee52048b98495ec1fe789b0dc8d9dcf489b417636477e50327fdb62a625d74e013eca12c1f008a7bc5141b5e02"

    def test_guarded_inner_tx_and_guarded_relayed_tx(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.bob.label,
            receiver="drt1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q6dlssu",
            gas_limit=60000000,
            nonce=198,
            data=b"addNumber",
            guardian=self.grace.label,
            version=2,
            options=2
        )
        inner_tx.signature = self.bob.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))
        inner_tx.guardian_signature = self.grace.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        relayed_builder = RelayedTransactionV1Builder()
        relayed_builder.set_inner_transaction(inner_tx)
        relayed_builder.set_relayer_nonce(2627)
        relayed_builder.set_network_config(network_config)
        relayed_builder.set_relayer_address(Address.new_from_bech32(self.alice.label))
        relayed_builder.set_relayed_transaction_version(2)
        relayed_builder.set_relayed_transaction_options(2)
        relayed_builder.set_relayed_transaction_guardian(Address.new_from_bech32(self.frank.label))

        relayed_tx = relayed_builder.build()
        relayed_tx.signature = self.alice.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))
        relayed_tx.guardian_signature = self.frank.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        assert relayed_tx.nonce == 2627
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225957526b546e5674596d5679222c227369676e6174757265223a2244514d6651635a4c77472b34426562746535785875647765722b5931444e504c4f2b6666644e496b514e4f4178487a77534a6d575058466a6176326979314c7a764973673831346764375a51792b4d4973386b4f41673d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a224e467666594d2b615950667a6a565341734a4f584c72542f357472732f76306d6d6553377a4e4e445136434b424d7062444d614f35752b307649646553452f485948653732444857397a7a41556b496a6559666143513d3d227d"
        assert relayed_tx.signature.hex() == "8a5dede58c168793bfb20aa097da484316707d5a5239482315e4e8eb3d96516686313495ed021b392e08fdd7e23207c19a1b0a560547c5c9d9224528656c770f"

    def test_compute_relayedV1_with_usernames(self):
        network_config = NetworkConfig()

        inner_tx = Transaction(
            chain_id=network_config.chain_id,
            sender=self.carol.label,
            receiver=self.alice.label,
            gas_limit=50000,
            sender_username="carol",
            receiver_username="alice",
            nonce=208,
            value=TokenPayment.rewa_from_amount(1).amount_as_integer
        )
        inner_tx.signature = self.carol.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(inner_tx))

        builder = RelayedTransactionV1Builder()
        builder.set_inner_transaction(inner_tx)
        builder.set_relayer_nonce(715)
        builder.set_network_config(network_config)
        builder.set_relayer_address(Address.new_from_bech32(self.frank.label))

        relayed_tx = builder.build()
        relayed_tx.signature = self.frank.secret_key.sign(self.transaction_computer.compute_bytes_for_signing(relayed_tx))

        assert relayed_tx.nonce == 715
        assert relayed_tx.data.decode() == "relayedTx@7b226e6f6e6365223a3230382c2273656e646572223a227371455656633553486b6c45344a717864556e59573068397a536249533141586f3534786f32634969626f3d222c227265636569766572223a2241546c484c76396f686e63616d433877673970645168386b77704742356a6949496f3349484b594e6165453d222c2276616c7565223a313030303030303030303030303030303030302c226761735072696365223a313030303030303030302c226761734c696d6974223a35303030302c2264617461223a22222c227369676e6174757265223a225931376171763275666e43364e4367373132514957363046426853317949444e625267554e615a65384a705774372b3655652b574c6d63346943665a5738336b7470774b6464492b36484a6666335a645561687341673d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c22736e64557365724e616d65223a22593246796232773d222c22726376557365724e616d65223a22595778705932553d227d"
        assert relayed_tx.signature.hex() == "a6660b9cd898ca022fb61d9389904db58cc45937d796636ac06871c52a8a3a1879454e8adba9ee9e31153169aa22cf80193ff9f7963af2e2dc1e537f03f85c0f"
