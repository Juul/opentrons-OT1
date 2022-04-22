import os
from unittest.mock import MagicMock
import pytest

from otupdate import openembedded
from otupdate.common.update_actions import Partition, UpdateActionsInterface
from otupdate.openembedded.updater import RootFSInterface, PartitionManager, Updater

HERE = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def mock_update_actions_interface(
    mock_root_fs_interface: MagicMock, mock_partition_manager_invalid_switch: MagicMock
) -> MagicMock:
    """Mock UpdateActionsInterface"""
    updater = Updater(
        root_FS_intf=mock_root_fs_interface,
        part_mngr=mock_partition_manager_invalid_switch,
    )
    mock = MagicMock(spec=UpdateActionsInterface)
    mock.from_request.return_value = updater


@pytest.fixture
async def test_cli(aiohttp_client, loop, otupdate_config, monkeypatch):
    """
    Build an app using dummy versions, then build a test client and return it
    """
    app = openembedded.get_app(
        system_version_file=os.path.join(HERE, "version.json"),
        config_file_override=otupdate_config,
        name_override="opentrons-test",
        boot_id_override="dummy-boot-id-abc123",
        loop=loop,
    )
    client = await loop.create_task(aiohttp_client(app))
    return client, app


def mock_root_fs_interface_() -> MagicMock:
    """Mock RootFSInterface."""
    return MagicMock(spec=RootFSInterface)


@pytest.fixture
def mock_root_fs_interface() -> MagicMock:
    """Mock RootFSInterface."""
    return MagicMock(spec=RootFSInterface)


def mock_partition_manager_valid_switch_() -> MagicMock:
    """Mock Partition Manager."""
    mock = MagicMock(spec=PartitionManager)
    mock.find_unused_partition.return_value = Partition(
        2, "/dev/mmcblk0p2", "/media/mmcblk0p2"
    )
    mock.switch_partition.return_value = Partition(
        2, "/dev/mmcblk0p2", "/media/mmcblk0p2"
    )
    mock.resize_partition.return_value = True
    mock.mount_fs.return_value = True
    mock.umount_fs.return_value = True

    mock.mountpoint_root.return_value = "/mnt"

    return mock


@pytest.fixture
def mock_partition_manager_valid_switch() -> MagicMock:
    """Mock Partition Manager."""
    mock = MagicMock(spec=PartitionManager)
    mock.find_unused_partition.return_value = Partition(
        2, "/dev/mmcblk0p2", "/media/mmcblk0p2"
    )
    mock.switch_partition.return_value = Partition(
        2, "/dev/mmcblk0p2", "/media/mmcblk0p2"
    )
    mock.resize_partition.return_value = True
    mock.mount_fs.return_value = True
    mock.umount_fs.return_value = True

    mock.mountpoint_root.return_value = "/mnt"

    return mock


@pytest.fixture
def mock_partition_manager_invalid_switch() -> MagicMock:
    """Mock Partition Manager."""
    mock = MagicMock(spec=PartitionManager)
    mock.find_unused_partition.return_value = Partition(
        2, "/dev/mmcblk0p2", "/media/mmcblk0p2"
    )
    mock.switch_partition.return_value = Partition(
        3, "/dev/mmcblk0p3", "/media/mmcblk0p3"
    )
    mock.resize_partition.return_value = True

    mock.mountpoint_root.return_value = "/mnt"

    return mock