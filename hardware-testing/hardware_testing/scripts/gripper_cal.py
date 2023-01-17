"""OT-3 Auto Gripper Calibration."""
import asyncio
import argparse
import csv
import logging

from opentrons.hardware_control.ot3_calibration import (
    calibrate_gripper_jaw,
    calibrate_gripper,
)


from hardware_testing.opentrons_api.types import OT3Mount, GripperProbe
from hardware_testing.opentrons_api import helpers_ot3

log = logging.getLogger(__name__)

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "basic": {"format": "%(asctime)s %(name)s %(levelname)s %(message)s"}
    },
    "handlers": {
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "basic",
            "filename": "/var/log/gripper_cal.log",
            "maxBytes": 5000000,
            "level": logging.INFO,
            "backupCount": 3,
        },
    },
    "loggers": {
        "": {
            "handlers": ["file_handler"],
            "level": logging.INFO,
        },
    },
}


async def _main(simulate: bool, slot: int, cycle: int, probe: str) -> None:

    api = await helpers_ot3.build_async_ot3_hardware_api(
        is_simulating=simulate,
        pipette_left="p1000_single_v3.3",
        pipette_right="p1000_single_v3.3",
        gripper="GRPV102",
        use_defaults=True,
    )

    for i in range(cycle):
        await api.home()

        if probe != "rear":
            # if probe is "all":
            #     input("Add probe to gripper REAR, then press ENTER: ")
            front_offset = await calibrate_gripper_jaw(api, GripperProbe.FRONT, slot)
            print(f"Front offset: {front_offset}")

            with open("/var/gripper_cal_data/front.csv", "a") as f:
                writer = csv.writer(f)
                to_write = list(v for v in front_offset)
                writer.writerow(to_write)
        # if probe is not "rear":
        #     if probe is "all":
        #         input("Add probe to gripper FRONT, then press ENTER: ")
        #     front_offset = await calibrate_gripper_jaw(api, GripperProbe.FRONT, slot)
        #     print(f"Front offset: {front_offset}")
        #     await api.home_z()

        if probe != "front":
            # if probe is "all":
            #     input("Add probe to gripper REAR, then press ENTER: ")
            rear_offset = await calibrate_gripper_jaw(api, GripperProbe.REAR, slot)
            print(f"Rear offset: {rear_offset}")

            with open("/var/gripper_cal_data/rear.csv", "a") as f:
                writer = csv.writer(f)
                to_write = list(v for v in rear_offset)
                writer.writerow(to_write)

        # await api.home()

        # if probe is "all":
        #     offset = await calibrate_gripper(api, front_offset, rear_offset)
        #     print(f"Offset: {offset}")

        # await api.home_z()
        # if i < (cycle - 1):
        #     input("Add probe to gripper FRONT, then press ENTER: ")


if __name__ == "__main__":
    print("\nOT-3 Auto-Calibration\n")
    arg_parser = argparse.ArgumentParser(description="OT-3 Auto-Calibration")

    arg_parser.add_argument("--simulate", action="store_true", default=False)
    arg_parser.add_argument("--slot", type=int, default=5)
    arg_parser.add_argument("--cycle", type=int, default=5)
    arg_parser.add_argument(
        "--probe", "-p", choices=["all", "front", "rear"], default="all"
    )
    args = arg_parser.parse_args()

    asyncio.run(_main(args.simulate, args.slot, args.cycle, args.probe))
