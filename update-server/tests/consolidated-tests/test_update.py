""" These tests are common for openembedded and buildroot
"""
import asyncio
import binascii
import hashlib
import os
import zipfile

import pytest

from otupdate.buildroot import update, config, update_actions
from otupdate.common import file_actions
from otupdate.common.session import UpdateSession, Stages
from otupdate.common.update_actions import UpdateActionsInterface
from otupdate.openembedded import Updater
from tests.openembedded.conftest import (
    mock_root_fs_interface_,
    mock_partition_manager_valid_switch_,
)


@pytest.fixture
async def update_session(test_cli):
    resp = await test_cli[0].post("/server/update/begin")
    body = await resp.json()
    yield body["token"]
    await test_cli[0].post("/server/update/cancel")


def session_endpoint(token, endpoint):
    return f"/server/update/{token}/{endpoint}"


async def test_begin(test_cli):
    # Creating a session should work
    resp = await test_cli[0].post("/server/update/begin")
    body = await resp.json()
    assert resp.status == 201
    assert "token" in body
    assert test_cli[0].server.app.get(update.SESSION_VARNAME)
    assert test_cli[0].server.app[update.SESSION_VARNAME].token == body["token"]

    # Creating a session twice shouldn’t
    resp = await test_cli[0].post("/server/update/begin")
    body = await resp.json()
    assert resp.status == 409
    assert "message" in body


async def test_cancel(test_cli):
    # cancelling when there’s a session should work great
    resp = await test_cli[0].post("/server/update/begin")
    assert test_cli[0].server.app.get(update.SESSION_VARNAME)

    resp = await test_cli[0].post("/server/update/cancel")
    assert resp.status == 200
    assert test_cli[0].server.app.get(update.SESSION_VARNAME) is None

    # and so should cancelling when there isn’t one

    resp = await test_cli[0].post("/server/update/cancel")
    assert resp.status == 200


async def test_commit_fails_wrong_state(test_cli, update_session):
    resp = await test_cli[0].post(session_endpoint(update_session, "commit"))
    assert resp.status == 409


br_handler = update_actions.OT2UpdateActions()


@pytest.fixture(
    params=[
        (
            0,
            lambda: Updater(
                mock_root_fs_interface_(), mock_partition_manager_valid_switch_()
            ),
        ),
        (1, lambda: update_actions.OT2UpdateActions()),
    ]
)
def sys_handler(request):
    return request.param


async def test_updater_chain(
    otupdate_config,
    downloaded_update_file_common,
    loop,
    testing_partition,
    sys_handler,
):
    conf = config.load_from_path(otupdate_config)
    session = UpdateSession(conf.download_storage_path)
    fut = update._begin_validation(
        session,
        conf,
        loop,
        downloaded_update_file_common.pop(sys_handler[0]),
        sys_handler[1](),
    )
    assert session.stage == Stages.VALIDATING
    last_progress = 0.0
    while session.stage == Stages.VALIDATING:
        assert session.state["progress"] >= last_progress
        assert session.state["stage"] == "validating"
        assert session.stage == Stages.VALIDATING
        last_progress = session.state["progress"]
        await asyncio.sleep(0.01)
    assert fut.done()
    last_progress = 0.0
    while session.stage == Stages.WRITING:
        assert session.state["progress"] >= last_progress
        last_progress = session.state["progress"]
        await asyncio.sleep(0.1)
    assert session.stage == Stages.DONE, session.error


@pytest.mark.exclude_rootfs_ext4
async def test_session_catches_validation_fail(
    otupdate_config,
    downloaded_update_file_common,
    loop,
    sys_handler,
):
    conf = config.load_from_path(otupdate_config)
    session = UpdateSession(conf.download_storage_path)
    fut = update._begin_validation(
        session,
        conf,
        loop,
        downloaded_update_file_common.pop(sys_handler[0]),
        sys_handler[1](),
    )
    with pytest.raises(file_actions.FileMissing):
        await fut
    assert session.state["stage"] == "error"
    assert session.stage == Stages.ERROR
    assert "error" in session.state
    assert "message" in session.state


async def test_update_happypath(
    test_cli,
    update_session,
    downloaded_update_file_common,
    loop,
    testing_partition,
    monkeypatch,
    mock_root_fs_interface,
    mock_partition_manager_valid_switch,
    extracted_update_file_common,
):
    updaters = [
        Updater(
            root_FS_intf=mock_root_fs_interface,
            part_mngr=mock_partition_manager_valid_switch,
        ),
        (update_actions.OT2UpdateActions()),
    ]

    # Upload
    if test_cli[1] == "otupdate.openembedded":
        monkeypatch.setattr(
            UpdateActionsInterface, "from_request", lambda x: updaters[0]
        )
        resp = await test_cli[0].post(
            session_endpoint(update_session, "file"),
            data={
                os.path.basename(downloaded_update_file_common[0]): open(
                    downloaded_update_file_common[0], "rb"
                )
            },
        )
    elif test_cli[1] == "otupdate.buildroot":
        monkeypatch.setattr(
            UpdateActionsInterface, "from_request", lambda x: updaters[1]
        )
        resp = await test_cli[0].post(
            session_endpoint(update_session, "file"),
            data={
                os.path.basename(downloaded_update_file_common[1]): open(
                    downloaded_update_file_common[1], "rb"
                )
            },
        )

    assert resp.status == 201
    body = await resp.json()
    assert body["stage"] == "validating"
    assert "progress" in body
    # Wait through validation
    then = loop.time()
    last_progress = 0.0
    while body["stage"] == "validating":
        assert body["progress"] >= last_progress
        resp = await test_cli[0].get(session_endpoint(update_session, "status"))
        assert resp.status == 200
        body = await resp.json()

        last_progress = body["progress"]
        assert loop.time() - then <= 300

    if body["stage"] == "writing":
        # Wait through write
        then = loop.time()
        last_progress = 0.0
        while body["stage"] == "writing":
            assert body["progress"] >= last_progress
            resp = await test_cli[0].get(session_endpoint(update_session, "status"))
            assert resp.status == 200
            body = await resp.json()
            last_progress = body["progress"]
            assert loop.time() - then <= 300

    assert body["stage"] == "done"

    if test_cli[1] == "otupdate.buildroot":
        with zipfile.ZipFile(downloaded_update_file_common[1], "r") as zf:
            tp_hasher = hashlib.sha256()
            fd = open(testing_partition, "rb")
            tp_hasher.update(fd.read())
            tp_hash = binascii.hexlify(tp_hasher.digest())
            assert tp_hash == zf.read("rootfs.ext4.hash").strip()
            fd.close()