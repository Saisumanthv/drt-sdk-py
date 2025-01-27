import pytest

from dharitri_sdk.core.address import Address
from dharitri_sdk.core.errors import InvalidInnerTransactionError
from dharitri_sdk.core.transaction import Transaction
from dharitri_sdk.core.transaction_computer import TransactionComputer
from dharitri_sdk.core.transactions_factories.relayed_transactions_factory import \
    RelayedTransactionsFactory
from dharitri_sdk.core.transactions_factories.transactions_factory_config import \
    TransactionsFactoryConfig
from dharitri_sdk.testutils.wallets import load_wallets


class TestRelayedTransactionsFactory:
    config = TransactionsFactoryConfig("T")
    factory = RelayedTransactionsFactory(config)
    transaction_computer = TransactionComputer()
    wallets = load_wallets()

    def test_create_relayed_v1_with_invalid_inner_tx(self):
        alice = self.wallets["alice"]

        inner_transaction = Transaction(
            sender=alice.label,
            receiver="drt1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls6prdez",
            gas_limit=10000000,
            data="getContractConfig".encode(),
            chain_id=self.config.chain_id
        )

        with pytest.raises(InvalidInnerTransactionError, match="The inner transaction is not signed"):
            self.factory.create_relayed_v1_transaction(
                inner_transaction=inner_transaction,
                relayer_address=Address.from_bech32(self.wallets["bob"].label)
            )

        inner_transaction.gas_limit = 0
        inner_transaction.signature = b"invalidsignature"

        with pytest.raises(InvalidInnerTransactionError, match="The gas limit is not set for the inner transaction"):
            self.factory.create_relayed_v1_transaction(
                inner_transaction=inner_transaction,
                relayer_address=Address.from_bech32(self.wallets["bob"].label)
            )

    def test_create_relayed_v1_transaction(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="drt1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls6prdez",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=198
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 2627

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414141415141414141414141414141414141414141414141414141414141432f2f383d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a22566e30744e364269687150476c59526f4b77696e455a6b4b6742706d76504d7a396e4d2b652b707635695175692b47344b36704447317030633235642b5852796c424c345a626d4679597a4a5830696a7672613641513d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a327d"
        assert relayed_transaction.signature.hex() == "6a4474e28873d965e46421e714a9a797be95cda78fac6c11791325b89806989261099c9dcef52712a54521f46b9bf3878273883d663df2a548438558e3ed180d"

    def test_create_relayed_v1_transaction_with_usernames(self):
        alice = self.wallets["alice"]
        carol = self.wallets["carol"]
        frank = self.wallets["frank"]

        inner_transaction = Transaction(
            sender=carol.label,
            receiver=alice.label,
            gas_limit=50000,
            chain_id=self.config.chain_id,
            nonce=208,
            sender_username="carol",
            receiver_username="alice",
            value=1000000000000000000
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = carol.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(frank.label)
        )
        relayed_transaction.nonce = 715

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = frank.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3230382c2273656e646572223a227371455656633553486b6c45344a717864556e59573068397a536249533141586f3534786f32634969626f3d222c227265636569766572223a2241546c484c76396f686e63616d433877673970645168386b77704742356a6949496f3349484b594e6165453d222c2276616c7565223a313030303030303030303030303030303030302c226761735072696365223a313030303030303030302c226761734c696d6974223a35303030302c2264617461223a22222c227369676e6174757265223a225931376171763275666e43364e4367373132514957363046426853317949444e625267554e615a65384a705774372b3655652b574c6d63346943665a5738336b7470774b6464492b36484a6666335a645561687341673d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c22736e64557365724e616d65223a22593246796232773d222c22726376557365724e616d65223a22595778705932553d227d"
        assert relayed_transaction.signature.hex() == "a6660b9cd898ca022fb61d9389904db58cc45937d796636ac06871c52a8a3a1879454e8adba9ee9e31153169aa22cf80193ff9f7963af2e2dc1e537f03f85c0f"

    def test_compute_relayed_v1_with_guarded_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        grace = self.wallets["grace"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="drt1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q6dlssu",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=198,
            version=2,
            options=2,
            guardian=grace.label
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)
        inner_transaction.guardian_signature = grace.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 2627

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225a3256305132397564484a68593352446232356d6157633d222c227369676e6174757265223a226c52366f3333423948656f34516f757a4b6b4542516b68372b4661774d55786d76453470354c5176776261634c6b515449562b6d6b4f66424370446d316961593870414c6b30503143722b6e756265467569683341773d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a2235666d3844462b777752616d626432716b3972322b6b3856327277374c755a303173577873433669336c4f566547464e4a4a526478626b7243345a544a69553648597979584636356f503734736a476143434e5742513d3d227d"
        assert relayed_transaction.signature.hex() == "fc25fddeb1027b9d692c65c24042b1753678fcee52048b98495ec1fe789b0dc8d9dcf489b417636477e50327fdb62a625d74e013eca12c1f008a7bc5141b5e02"

    def test_guarded_relayed_v1_with_guarded_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        grace = self.wallets["grace"]
        frank = self.wallets["frank"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="drt1qqqqqqqqqqqqqpgq54tsxmej537z9leghvp69hfu4f8gg5eu396q6dlssu",
            gas_limit=60000000,
            chain_id=self.config.chain_id,
            data=b"addNumber",
            nonce=198,
            version=2,
            options=2,
            guardian=grace.label
        )

        inner_tx_bytes = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(inner_tx_bytes)
        inner_transaction.guardian_signature = grace.secret_key.sign(inner_tx_bytes)

        relayed_transaction = self.factory.create_relayed_v1_transaction(
            inner_transaction=inner_transaction,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.options = 2
        relayed_transaction.nonce = 2627
        relayed_transaction.guardian = frank.label

        relayed_tx_bytes = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(relayed_tx_bytes)
        relayed_transaction.guardian_signature = frank.secret_key.sign(relayed_tx_bytes)

        assert relayed_transaction.data.decode() == "relayedTx@7b226e6f6e6365223a3139382c2273656e646572223a2267456e574f65576d6d413063306a6b71764d354241707a61644b46574e534f69417643575163776d4750673d222c227265636569766572223a22414141414141414141414146414b565841323879704877692f79693741364c64504b704f68464d386958513d222c2276616c7565223a302c226761735072696365223a313030303030303030302c226761734c696d6974223a36303030303030302c2264617461223a225957526b546e5674596d5679222c227369676e6174757265223a2244514d6651635a4c77472b34426562746535785875647765722b5931444e504c4f2b6666644e496b514e4f4178487a77534a6d575058466a6176326979314c7a764973673831346764375a51792b4d4973386b4f41673d3d222c22636861696e4944223a2256413d3d222c2276657273696f6e223a322c226f7074696f6e73223a322c22677561726469616e223a22486f714c61306e655733766843716f56696c70715372744c5673774939535337586d7a563868477450684d3d222c22677561726469616e5369676e6174757265223a224e467666594d2b615950667a6a565341734a4f584c72542f357472732f76306d6d6553377a4e4e445136434b424d7062444d614f35752b307649646553452f485948653732444857397a7a41556b496a6559666143513d3d227d"
        assert relayed_transaction.signature.hex() == "8a5dede58c168793bfb20aa097da484316707d5a5239482315e4e8eb3d96516686313495ed021b392e08fdd7e23207c19a1b0a560547c5c9d9224528656c770f"

    def test_create_relayed_v2_with_invalid_inner_tx(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]
        carol = self.wallets["carol"]

        inner_transaction = Transaction(
            sender=alice.label,
            receiver=bob.label,
            gas_limit=50000,
            chain_id=self.config.chain_id
        )

        with pytest.raises(InvalidInnerTransactionError, match="The gas limit should not be set for the inner transaction"):
            self.factory.create_relayed_v2_transaction(
                inner_transaction=inner_transaction,
                inner_transaction_gas_limit=50000,
                relayer_address=Address.from_bech32(carol.label)
            )

        inner_transaction.gas_limit = 0
        with pytest.raises(InvalidInnerTransactionError, match="The inner transaction is not signed"):
            self.factory.create_relayed_v2_transaction(
                inner_transaction=inner_transaction,
                inner_transaction_gas_limit=50000,
                relayer_address=Address.from_bech32(carol.label)
            )

    def test_compute_relayed_v2_transaction(self):
        alice = self.wallets["alice"]
        bob = self.wallets["bob"]

        inner_transaction = Transaction(
            sender=bob.label,
            receiver="drt1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzllls6prdez",
            gas_limit=0,
            chain_id=self.config.chain_id,
            data=b"getContractConfig",
            nonce=15,
            version=2,
            options=0
        )

        serialized_inner_transaction = self.transaction_computer.compute_bytes_for_signing(inner_transaction)
        inner_transaction.signature = bob.secret_key.sign(serialized_inner_transaction)

        relayed_transaction = self.factory.create_relayed_v2_transaction(
            inner_transaction=inner_transaction,
            inner_transaction_gas_limit=60_000_000,
            relayer_address=Address.from_bech32(alice.label)
        )
        relayed_transaction.nonce = 37

        serialized_relayed_transaction = self.transaction_computer.compute_bytes_for_signing(relayed_transaction)
        relayed_transaction.signature = alice.secret_key.sign(serialized_relayed_transaction)

        assert relayed_transaction.version == 2
        assert relayed_transaction.options == 0
        assert relayed_transaction.gas_limit == 60414500
        assert relayed_transaction.data.decode() == "relayedTxV2@000000000000000000010000000000000000000000000000000000000002ffff@0f@676574436f6e7472616374436f6e666967@1703b6e2a855fd93a0758c15f80427ebceb695c0ef12ae613fae90fa9fcc105cf79391cad98f034efded0a72a6b312ce4e798804c81abee632e07bc7747fb40c"
