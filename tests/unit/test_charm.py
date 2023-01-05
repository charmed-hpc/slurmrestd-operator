import unittest
from unittest.mock import PropertyMock, patch

from charm import SlurmrestdCharm
from ops.model import ActiveStatus, BlockedStatus
from ops.testing import Harness

class TestCharm(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = Harness(SlurmrestdCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()
        self.maxDiff = None

    def test_update_status_fail(self):
        self.harness.charm.on.update_status.emit()
        self.assertEqual(self.harness.charm.unit.status, BlockedStatus("Error installing slurmrestd"))

    @patch("interface_slurmrestd.SlurmrestdRequires.is_joined", new_callable=PropertyMock(return_value=True))
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_munge_key", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_jwt_rsa", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_slurm_config", lambda _: True)
    def test_update_status_success(self, _):
        self.harness.charm._stored.slurm_installed = True

        self.harness.charm.on.update_status.emit()
        self.assertEqual(self.harness.charm.unit.status, ActiveStatus("slurmrestd available"))