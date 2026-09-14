from .bea import BEAAdapter
from .bls import BLSAdapter
from .census import CensusAdapter
from .fec import FECAdapter
from .fed_z1 import FederalReserveZ1Adapter
from .sec import SECAdapter
from .treasury import TreasuryAdapter
from .usaspending import USASpendingAdapter

ADAPTERS = {
    "bea": BEAAdapter,
    "bls": BLSAdapter,
    "census": CensusAdapter,
    "fec": FECAdapter,
    "fed-z1": FederalReserveZ1Adapter,
    "sec": SECAdapter,
    "treasury": TreasuryAdapter,
    "usaspending": USASpendingAdapter,
}
