"""OT3 Homing Accuracy Test."""
import argparse
import asyncio
import os, time, random

from opentrons.hardware_control.ot3api import OT3API
from opentrons.hardware_control.types import Axis
# from opentrons_hardware.hardware_control import encoder_hardware as encoder_hardware
# from hardware_testing.opentrons_api import encoder_hardware as encoder_hardware

from hardware_testing import data
from hardware_testing.opentrons_api.types import GantryLoad, OT3Mount, OT3Axis, Point
from hardware_testing.opentrons_api.helpers_ot3 import (
    build_async_ot3_hardware_api,
    GantryLoadSettings,
    set_gantry_load_per_axis_settings_ot3,
    home_ot3,
    get_endstop_position_ot3,
)

from hardware_testing.drivers import mitutoyo_digimatic_indicator as dial

MOUNT = OT3Mount.RIGHT
LOAD = GantryLoad.NONE
CYCLES = 25
SPEED_XY = 400
SPEED_Z = 65

MOVE_POS = Point(227.826, 362.808, 250.0) #Point(235.414, 385.308, 509.15)
FIXTURE_POS = Point(227.826, 362.808, 44.61) #Point(235.414, 385.308, 303.965)

SETTINGS = {
    OT3Axis.X: GantryLoadSettings(
        max_speed=SPEED_XY,
        acceleration=1000,
        max_start_stop_speed=10,
        max_change_dir_speed=5,
        hold_current=0.1,
        run_current=1.4,
    ),
    OT3Axis.Y: GantryLoadSettings(
        max_speed=SPEED_XY,
        acceleration=500,
        max_start_stop_speed=10,
        max_change_dir_speed=5,
        hold_current=0.1,
        run_current=1.4,
    ),
    OT3Axis.Z_L: GantryLoadSettings(
        max_speed=SPEED_Z,
        acceleration=500,
        max_start_stop_speed=10,
        max_change_dir_speed=5,
        hold_current=0.1,
        run_current=1.4,
    ),
    OT3Axis.Z_R: GantryLoadSettings(
        max_speed=SPEED_Z,
        acceleration=500,
        max_start_stop_speed=10,
        max_change_dir_speed=5,
        hold_current=0.1,
        run_current=1.4,
    ),
}

async def _main(is_simulating: bool) -> None:
    api = await build_async_ot3_hardware_api(is_simulating=is_simulating)
    # await set_gantry_load_per_axis_settings_ot3(api, SETTINGS, load=LOAD)

    test_tag = input("Enter test tag:\n\t>> ")
    test_robot = input("Enter robot ID:\n\t>> ")

    test_name = "encoder-stall-validation"
    file_name = data.create_file_name(test_name=test_name, run_id=data.create_run_id(), tag=test_tag)

    header = ['Cycle', 'Test Robot', 'Test Axis', 'Init Position Read (mm)', 'Stall Position Read (mm)', 'Difference (mm)', 'Encoder Value Before', 'Encoder Value After']
    header_str = data.convert_list_to_csv_line(header)
    data.append_data_to_file(test_name=test_name, file_name=file_name, data=header_str)

    for cycle in range(CYCLES):
        print(f"Cycle: {cycle+1} out of {CYCLES}")
        ### time.sleep(1)
        await home_ot3(api)
        # MOVE_POS = Point(227.826, 362.808, 250.0) #Point(235.414, 385.308, 509.15)
        # FIXTURE_POS = Point(227.826, 362.808, 44.61) #Point(235.414, 385.308, 303.965)
        # await api.move_to(MOUNT, Point(227.826, 362.808, 250.0)) #, speed = 50)
        await api.move_to(MOUNT, Point(226.526, 362.208, 250.0)) #, speed = 50)
        ### time.sleep(1)
        # await api.move_to(MOUNT, Point(227.826, 362.808, 52.61)) #, speed = 50)
        await api.move_to(MOUNT, Point(226.526, 362.208, 151.0)) #, speed = 50)
        ### time.sleep(1)
        # await api.move_to(MOUNT, Point(227.826, 362.808, 42.61)) #, speed = 50)
        await api.move_to(MOUNT, Point(226.526, 362.208, 141.0)) #, speed = 50) ### Point(226.526, 362.608, 146.0)) makes contact with gauge
        ### time.sleep(1)
        init_reading = gauge.read()
        init_robot_pos = await api.current_position_ot3(MOUNT, refresh=True)
        init_encoder_pos = await api.encoder_current_position_ot3(MOUNT, refresh=True)
        print(f"Initial Dial Reading (mm) = {init_reading}\n")
        print(f"Initial robot position: {init_robot_pos[OT3Axis.Z_R]}\n")
        print(f"Initial encoder position: {init_encoder_pos[OT3Axis.Z_R]}\n")
        await asyncio.sleep(1)

        # input("Press enter to continue test...\n")
        # print("\n--STALLING--\n")
        # # await api.move_rel(MOUNT, delta=Point(z=10))
        # await api.move_to(MOUNT, Point(227.826, 362.808, 52.61)) #, speed = 50)
        # ### time.sleep(1)
        # # await api.move_rel(MOUNT, delta=Point(x=30))
        # await api.move_to(MOUNT, Point(257.826, 362.808, 52.61)) #, speed = 50)
        # ### time.sleep(1)
        # try:
        #     await api.move_rel(MOUNT, delta=Point(z=-20), _check_stalls=True)
        # except RuntimeError as e:
        #     if "collision_detected" in str(e):
        #         print("--COLLISION DETECTED--\n")
        #         collision_detected = True
        #         print("--UPDATE POSITION--\n")
        #         await api._update_position_estimation([OT3Axis.Z_R])

        print("\n--PICK UP TIP--\n")
        # await api.move_rel(MOUNT, delta=Point(z=10))
        # await api.move_to(MOUNT, Point(227.826, 362.808, 52.61)) #, speed = 50)
        await api.move_to(MOUNT, Point(226.526, 362.208, 151.0)) #, speed = 50)
        ### time.sleep(1)
        # await api.move_rel(MOUNT, delta=Point(x=30))
        # await api.move_to(MOUNT, Point(257.826, 362.808, 52.61)) #, speed = 50)
        await api.move_to(MOUNT, Point(177.926, 362.208, 151.0)) #, speed = 50)
        await api.move_to(MOUNT, Point(177.926, 287.408, 151.0)) #, speed = 50)
        ### time.sleep(1)
        await api.move_to(MOUNT, Point(177.926, 287.408, 104.5))
        ### multi: (177.926, 287.408, 99.2)
        ### single: (177.726, 287.708, 99.5)
        await api.move_to(MOUNT, Point(177.926, 287.408, 99.2), speed = 50)
        # try:
        #     # await api.move_rel(MOUNT, delta=Point(z=-20), _check_stalls=True)
        #     await api.pick_up_tip(MOUNT, tip_length=57)
        # except RuntimeError as e:
        #     if "collision_detected" in str(e):
        #         print("--COLLISION DETECTED--\n")
        #         # collision_detected = True
        #         print("--UPDATE POSITION--\n")
        #         await api._update_position_estimation([OT3Axis.Z_R])
        print("Picking up tip\n")
        await api.pick_up_tip(MOUNT, tip_length=57)
        # print("--UPDATE POSITION--\n")
        # await api._update_position_estimation([OT3Axis.Z_R])
        # await asyncio.sleep(1)
        print("Dropping tip\n")
        await api.drop_tip(MOUNT, home_after=False)

        ### all 3 --> weird behavior, the probe moves diagonally when trying to hit the gauge after the stall
        ### first and third commented out --> able to reach gauge, but is off by like 2mm
        ### first and second commented out --> similar to first and third behavior, also off by like 2mm
        ### second and third commented out --> all good
        # 1 await asyncio.sleep(1) ### --> if this is the only one commented out,  ~2.4mm diff present
        # if collision_detected:
        #     print("--UPDATE POSITION--\n")
        #     await api._update_position_estimation([OT3Axis.Z_R])
        # 2 await asyncio.sleep(1) ### --> if this is the only one commented out, everything is good
        stall_robot_pos = await api.current_position_ot3(MOUNT, refresh=True)
        stall_encoder_pos = await api.encoder_current_position_ot3(MOUNT, refresh=True)
        print(f"Stalled robot position: {stall_robot_pos[OT3Axis.Z_R]}\n")
        print(f"Stalled encoder position: {stall_encoder_pos[OT3Axis.Z_R]}\n")
        # 3 await asyncio.sleep(1) ### --> if this is the only one commented out, everything is good

        # MOVE_POS = Point(227.826, 362.808, 250.0) #Point(235.414, 385.308, 509.15)
        # FIXTURE_POS = Point(227.826, 362.808, 44.61) #Point(235.414, 385.308, 303.965)

        # await api.move_to(MOUNT, Point(257.826, 362.808, 52.61)) #, speed = 50)
        await api.move_to(MOUNT, Point(177.926, 287.408, 151.0)) #, speed = 50)
        await api.move_to(MOUNT, Point(177.926, 362.208, 151.0)) #, speed = 50)
        await api.move_to(MOUNT, Point(226.526, 362.208, 151.0)) #, speed = 50)
        ### time.sleep(1)
        # await api.move_to(MOUNT, Point(227.826, 362.808, 52.61)) #, speed = 50)
        ### time.sleep(1)
        # pos = await api.current_position_ot3(MOUNT)
        # input(f"Current pos: {pos[OT3Axis.Z_R]}")
        # await api.move_to(MOUNT, Point(227.826, 362.808, 42.61)) #, speed = 50)
        await api.move_to(MOUNT, Point(226.526, 362.208, 141.0)) #, speed = 50)
        ### time.sleep(1)
        # pos = await api.current_position_ot3(MOUNT)
        # input(f"Current pos: {pos[OT3Axis.Z_R]}")

        stall_reading = gauge.read()
        updated_robot_pos = await api.current_position_ot3(MOUNT, refresh=True)
        updated_encoder_pos = await api.encoder_current_position_ot3(MOUNT, refresh=True)
        print(f"Stall Dial Reading (mm) = {stall_reading}\n")
        print(f"Updated robot position: {updated_robot_pos[OT3Axis.Z_R]}\n")
        print(f"Updated encoder position: {updated_encoder_pos[OT3Axis.Z_R]}\n")
        await asyncio.sleep(1)

        reading_diff = init_reading - stall_reading
        print(f"Dial reading difference after stall: {reading_diff} mm\n")

        if cycle > 0:
            test_robot = ""
            test_tag = ""

        cycle_data = [cycle+1, test_robot, test_tag, init_reading, stall_reading, reading_diff, init_encoder_pos[OT3Axis.Z_R], updated_encoder_pos[OT3Axis.Z_R]]
        cycle_data_str = data.convert_list_to_csv_line(cycle_data)
        data.append_data_to_file(test_name=test_name, file_name=file_name, data=cycle_data_str)

        await api.move_to(MOUNT, Point(226.526, 362.208, 151.0))
        await api.move_to(MOUNT, Point(485.0, 386.0, 151.0))
        # await api.move_to(MOUNT, Point(485.0, 386.0, 225.0))

    await home_ot3(api)
    await api.disengage_axes([OT3Axis.X, OT3Axis.Y, OT3Axis.Z_L, OT3Axis.Z_R])

if __name__ == "__main__":
    print("\nSTART TEST\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", action="store_true")

    parser.add_argument("--cycles", type=int, default=CYCLES)
    parser.add_argument("--speed-xy", type=int, default=SPEED_XY)
    parser.add_argument("--speed-z", type=int, default=SPEED_Z)
    parser.add_argument("--test_home_speed", type=int, default=40)
    parser.add_argument("--mod_port", type=str, required=False, \
                        default = "/dev/ttyUSB0")
    args = parser.parse_args()

    CYCLES = args.cycles
    SPEED_XY = args.speed_xy
    SPEED_Z = args.speed_z
    SETTINGS[OT3Axis.X].max_speed = SPEED_XY
    SETTINGS[OT3Axis.Y].max_speed = SPEED_XY
    SETTINGS[OT3Axis.Z_L].max_speed = SPEED_Z
    SETTINGS[OT3Axis.Z_R].max_speed = SPEED_Z

    gauge = dial.Mitutoyo_Digimatic_Indicator(port=args.mod_port)
    gauge.connect()

    asyncio.run(_main(args.simulate))
