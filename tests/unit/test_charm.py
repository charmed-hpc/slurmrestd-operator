#!/usr/bin/env python3
# Copyright 2023 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Test default charm events such as upgrade charm, install, etc."""

import unittest
from unittest.mock import PropertyMock, patch

from charm import SlurmrestdCharm
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from ops.testing import Harness


class TestCharm(unittest.TestCase):
    def setUp(self) -> None:
        self.harness = Harness(SlurmrestdCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    @patch("ops.framework.EventBase.defer")
    def test_config_available_fail(self, defer):
        self.harness.charm._slurmrestd.on.config_available.emit()
        defer.assert_called()

    @patch("slurm_ops_manager.SlurmManager.render_slurm_configs")
    @patch(
        "interface_slurmrestd.SlurmrestdRequires.get_stored_slurm_config",
        return_value={"cluster_name": "test"},
    )
    @patch(
        "slurm_ops_manager.SlurmManager.needs_reboot",
        new_callable=PropertyMock(return_value=False),
    )
    @patch(
        "interface_slurmrestd.SlurmrestdRequires.is_joined",
        new_callable=PropertyMock(return_value=True),
    )
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_munge_key", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_jwt_rsa", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_slurm_config", lambda _: True)
    @patch("ops.framework.EventBase.defer")
    def test_config_available_success(self, defer, *_):
        self.harness.charm._stored.slurm_installed = True
        self.harness.charm._stored.slurmrestd_restarted = True

        self.harness.charm._slurmrestd.on.config_available.emit()
        defer.assert_not_called()

    def test_config_unavailable(self):
        self.harness.charm._slurmrestd.on.config_unavailable.emit()
        self.assertFalse(self.harness.charm._stored.slurmrestd_restarted)

    @patch("pathlib.Path.read_text", return_value="v1.0.0")
    @patch("ops.framework.EventBase.defer")
    def test_install_fail(self, defer, *_):
        self.harness.charm.on.install.emit()
        self.assertFalse(self.harness.charm._stored.slurm_installed)
        defer.assert_called()

    @patch(
        "slurm_ops_manager.SlurmManager.needs_reboot",
        new_callable=PropertyMock(return_value=False),
    )
    @patch(
        "interface_slurmrestd.SlurmrestdRequires.is_joined",
        new_callable=PropertyMock(return_value=True),
    )
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_munge_key", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_jwt_rsa", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_slurm_config", lambda _: True)
    @patch("slurm_ops_manager.SlurmManager.install")
    @patch("pathlib.Path.read_text", return_value="v1.0.0")
    @patch("slurm_ops_manager.SlurmManager.start_munged", lambda _: True)
    @patch("ops.framework.EventBase.defer")
    def test_install_success(self, defer, *_):
        self.harness.charm.on.install.emit()
        self.assertTrue(self.harness.charm._stored.slurm_installed)
        self.assertEqual(self.harness.charm.unit.status, ActiveStatus("slurmrestd available"))
        defer.assert_not_called()

    @patch("ops.framework.EventBase.defer")
    def test_jwt_rsa_available_fail(self, defer):
        self.harness.charm._slurmrestd.on.jwt_rsa_available.emit()
        defer.assert_called()

    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_jwt_rsa")
    @patch("slurm_ops_manager.SlurmManager.configure_jwt_rsa")
    @patch("ops.framework.EventBase.defer")
    def test_jwt_rsa_available_success(self, defer, *_):
        self.harness.charm._stored.slurm_installed = True

        self.harness.charm._slurmrestd.on.jwt_rsa_available.emit()
        defer.assert_not_called()

    @patch("ops.framework.EventBase.defer")
    def test_munge_key_available_fail(self, defer):
        self.harness.charm._slurmrestd.on.munge_key_available.emit()
        defer.assert_called()

    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_munge_key")
    @patch("slurm_ops_manager.SlurmManager.configure_munge_key")
    @patch("slurm_ops_manager.SlurmManager.restart_munged")
    @patch("ops.framework.EventBase.defer")
    def test_munge_key_available_success(self, defer, *_):
        self.harness.charm._stored.slurm_installed = True

        self.harness.charm._slurmrestd.on.munge_key_available.emit()
        defer.assert_not_called()

    @patch("ops.framework.EventBase.defer")
    def test_restart_slurmrestd_fail(self, defer):
        self.harness.charm._slurmrestd.on.restart_slurmrestd.emit()
        defer.assert_called()

    @patch("slurm_ops_manager.SlurmManager.restart_slurm_component", lambda _: True)
    @patch(
        "slurm_ops_manager.SlurmManager.needs_reboot",
        new_callable=PropertyMock(return_value=False),
    )
    @patch(
        "interface_slurmrestd.SlurmrestdRequires.is_joined",
        new_callable=PropertyMock(return_value=True),
    )
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_munge_key", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_jwt_rsa", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_slurm_config", lambda _: True)
    @patch("ops.framework.EventBase.defer")
    def test_restart_slurmrestd_success(self, defer, *_):
        self.harness.charm._stored.slurm_installed = True

        self.harness.charm._slurmrestd.on.restart_slurmrestd.emit()
        self.assertTrue(self.harness.charm._stored.slurmrestd_restarted)
        defer.assert_not_called()

    def test_start(self):
        self.harness.charm.on.start.emit()
        self.assertEqual(self.harness.charm.unit.status, MaintenanceStatus(""))

    def test_update_status_fail(self):
        self.harness.charm.on.update_status.emit()
        self.assertEqual(
            self.harness.charm.unit.status, BlockedStatus("Error installing slurmrestd")
        )

    @patch(
        "slurm_ops_manager.SlurmManager.needs_reboot",
        new_callable=PropertyMock(return_value=False),
    )
    @patch(
        "interface_slurmrestd.SlurmrestdRequires.is_joined",
        new_callable=PropertyMock(return_value=True),
    )
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_munge_key", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_jwt_rsa", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_slurm_config", lambda _: True)
    def test_update_status_success(self, *_):
        self.harness.charm._stored.slurm_installed = True

        self.harness.charm.on.update_status.emit()
        self.assertEqual(self.harness.charm.unit.status, ActiveStatus("slurmrestd available"))

    @patch("pathlib.Path.read_text", return_value="v1.0.0")
    def test_upgrade_fail(self, *_):
        self.harness.charm.on.upgrade_charm.emit()
        self.assertEqual(
            self.harness.charm.unit.status, BlockedStatus("Error installing slurmrestd")
        )

    @patch("pathlib.Path.read_text", return_value="v1.0.0")
    @patch(
        "slurm_ops_manager.SlurmManager.needs_reboot",
        new_callable=PropertyMock(return_value=False),
    )
    @patch(
        "interface_slurmrestd.SlurmrestdRequires.is_joined",
        new_callable=PropertyMock(return_value=True),
    )
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_munge_key", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_jwt_rsa", lambda _: True)
    @patch("interface_slurmrestd.SlurmrestdRequires.get_stored_slurm_config", lambda _: True)
    def test_upgrade_success(self, *_):
        self.harness.charm._stored.slurm_installed = True

        self.harness.charm.on.upgrade_charm.emit()
        self.assertEqual(self.harness.charm.unit.status, ActiveStatus("slurmrestd available"))
