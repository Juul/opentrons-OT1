from opentrons.types import Point
from opentrons import types
import numpy as np


metadata = {
    'protocolName': 'Omega HDQ DNA Extraction with Lysis: Cells',
    'author': 'Zach Galluzzo <zachary.galluzzo@opentrons.com>',
    "apiLevel": "2.13",

}

requirements = {
    "robotType": "OT-3",
    "apiLevel": "2.13",
}

USE_GRIPPER = True

DECK_SLOT_TIPS_A = 2
DECK_SLOT_TIPS_B = 3
DECK_SLOT_MAG_PLATE = 6
DECK_SLOT_HEATER_SHAKER = 10
DECK_SLOT_PLATE_ELUTION = 1
DECK_SLOT_LIQUID_WASTE = 9
DECK_SLOT_RESERVOIR_LYSIS = 5
DECK_SLOT_RESERVOIR_ELUSION = 4
DECK_SLOT_RESERVOIR_WASH = 7
DECK_SLOT_RESERVOIR_BIND = 8

LABWARE_TYPE_TIPS = "opentrons_ot3_96_tiprack_1000ul"
LABWARE_TYPE_PLATE_ELUTION = "opentrons_96_aluminumblock_nest_wellplate_100ul"
LABWARE_TYPE_PLATE_DEEP_WELL = "nest_96_wellplate_2ml_deep"
LABWARE_TYPE_RESERVOIR_WASTE = "nest_1_reservoir_195ml"

RESUSPEND_PELLET_POINTS_AROUND_CIRCLE_RADIUS_1_MM = [
    types.Point(x=1.00),  # right
    types.Point(x=0.75, y=0.75),  # back-right
    types.Point(y=1.00),  # back
    types.Point(x=-0.75, y=0.75),  # back-left
    types.Point(x=-1.00),  # left
    types.Point(x=-0.75, y=-0.75),  # front-left
    types.Point(y=-1.00),  # front
    types.Point(x=0.75, y=-0.75),  # front-right
]

BEAD_MIX_POINTS_MOVING_UPWARDS_MM = [
    types.Point(z=1), types.Point(z=8), types.Point(z=16), types.Point(z=24),
]


def grip_offset(action, item, slot=None):
    """Grip offset."""
    # do NOT edit these values
    # NOTE: these values will eventually be in our software
    #       and will not need to be inside a protocol
    _hw_offsets = {
        "deck": Point(),
        "mag-plate": Point(z=29.5),
        "heater-shaker-right": Point(x=(-3 - -0.125), y=(-1 - 1.125), z=(24 - 68.275)),
        "heater-shaker-left": Point(x=(3 - -0.125), y=(1 - 1.125), z=(24 - 68.275)),
        "temp-module": Point(x=(0 - -1.45), y=(0 - -0.15), z=(9 - 80.09)),
        "thermo-cycler": Point(x=(-20 - 0), y=(67.5 - 68.06), z=(-0.04 - 98.26)),
    }
    # EDIT these values
    # NOTE: we are still testing to determine our software's defaults
    #       but we also expect users will want to edit these
    _pick_up_offsets = {
        "deck": Point(x=-0.2),
        "mag-plate": Point(),
        "heater-shaker": Point(),
        "temp-module": Point(),
        "thermo-cycler": Point(),
    }
    # EDIT these values
    # NOTE: we are still testing to determine our software's defaults
    #       but we also expect users will want to edit these
    _drop_offsets = {
        "deck": Point(z=-2),
        "mag-plate": Point(z=9.5),
        "heater-shaker": Point(z=-2),
        "temp-module": Point(z=-2),
        "thermo-cycler": Point(),
    }
    # make sure arguments are correct
    action_options = ["pick-up", "drop"]
    item_options = list(_hw_offsets.keys())
    item_options.remove("heater-shaker-left")
    item_options.remove("heater-shaker-right")
    item_options.append("heater-shaker")
    if action not in action_options:
        raise ValueError(
            f'"{action}" not recognized, available options: {action_options}'
        )
    if item not in item_options:
        raise ValueError(f'"{item}" not recognized, available options: {item_options}')
    if item == "heater-shaker":
        assert slot, "argument slot= is required when using \"heater-shaker\""
        if slot in [1, 4, 7, 10]:
            side = "left"
        elif slot in [3, 6, 9, 12]:
            side = "right"
        else:
            raise ValueError("heater shaker must be on either left or right side")
        hw_offset = _hw_offsets[f"{item}-{side}"]
    else:
        hw_offset = _hw_offsets[item]
    if action == "pick-up":
        offset = hw_offset + _pick_up_offsets[item]
    else:
        offset = hw_offset + _drop_offsets[item]
    # convert from Point() to dict()
    return {"x": offset.x, "y": offset.y, "z": offset.z}


def _mix_at_points_in_well(pipette, volume, well, points, reps, mm_from_bottom):
    if volume > pipette.working_volume:
        volume = pipette.working_volume
    mix_volume = volume * 0.9
    locations = [
        well.bottom(mm_from_bottom).move(p)
        for p in points
    ]
    for _ in range(reps):
        for loc in locations:
            pipette.aspirate(mix_volume, loc)
            pipette.dispense(mix_volume, loc)


def resuspend_pellet(pipette, volume, well, reps=3, mm_from_bottom=0):
    _mix_at_points_in_well(pipette, volume, well,
                           RESUSPEND_PELLET_POINTS_AROUND_CIRCLE_RADIUS_1_MM,
                           reps, mm_from_bottom)


def bead_mix(pipette, volume, well, reps=5, mm_from_bottom=0):
    _mix_at_points_in_well(pipette, volume, well,
                           BEAD_MIX_POINTS_MOVING_UPWARDS_MM,
                           reps, mm_from_bottom)


# Start protocol
def run(ctx):
    # Same for all HDQ Extractions
    wash_vol = 600  # ***ASPIRATED***
    num_washes = 3
    settling_time = 4

    # Differences between sample types
    # NOTE: also aspirates 1000 uL
    #       ALL_ASPIRATES = [50, 250, 340, 430, 1000]
    AL_vol = 250  # ***ASPIRATED***
    sample_start_vol = 180
    binding_buffer_vol = 340  # ***ASPIRATED***
    elution_vol = 50  # ***ASPIRATED***
    starting_vol = AL_vol + sample_start_vol  # ***ASPIRATED***

    # PIPETTE and TIPS
    pip = ctx.load_instrument('p1000_96', mount="left")
    pip.flow_rate.aspirate = 50
    pip.flow_rate.dispense = 150
    pip.flow_rate.blow_out = 300
    # TODO (spp, 2023-1-11): these lines were originally loading filter tipracks. Is that necessary?
    tips_a = ctx.load_labware(LABWARE_TYPE_TIPS, DECK_SLOT_TIPS_A)
    tips_b = ctx.load_labware(LABWARE_TYPE_TIPS, DECK_SLOT_TIPS_B)

    # MODULES and LABWARE
    h_s = ctx.load_module('heaterShakerModuleV1', DECK_SLOT_HEATER_SHAKER)
    sample_plate = h_s.load_labware(LABWARE_TYPE_PLATE_DEEP_WELL)
    h_s.close_labware_latch()  # Just in case

    elution_plate = ctx.load_labware(LABWARE_TYPE_PLATE_ELUTION, DECK_SLOT_PLATE_ELUTION)
    waste_labware = ctx.load_labware(LABWARE_TYPE_RESERVOIR_WASTE, DECK_SLOT_LIQUID_WASTE, 'Liquid Waste')
    waste = waste_labware.wells()[0].top()

    lysis_res = ctx.load_labware(LABWARE_TYPE_PLATE_DEEP_WELL, DECK_SLOT_RESERVOIR_LYSIS)
    elution_res = ctx.load_labware(LABWARE_TYPE_PLATE_DEEP_WELL, DECK_SLOT_RESERVOIR_ELUSION)
    wash_res = ctx.load_labware(LABWARE_TYPE_PLATE_DEEP_WELL, DECK_SLOT_RESERVOIR_WASH)
    bind_res = ctx.load_labware(LABWARE_TYPE_PLATE_DEEP_WELL, DECK_SLOT_RESERVOIR_BIND)

    # Transfer and mix lysis
    pip.pick_up_tip(tips_a)
    pip.aspirate(AL_vol, lysis_res)
    pip.dispense(AL_vol, sample_plate)
    resuspend_pellet(pip, starting_vol * 0.9, sample_plate, reps=4, mm_from_bottom=1)
    pip.drop_tip(tips_a)

    # Mix 10 minutes, then heat 10 minutes
    h_s.set_and_wait_for_shake_speed(rpm=1800)
    ctx.delay(minutes=10)
    h_s.deactivate_shaker()
    h_s.set_and_wait_for_temperature(celcius=55)
    ctx.delay(minutes=10)
    h_s.deactive_heater()

    # Transfer and mix bind&beads
    pip.pick_up_tip(tips_b)
    bead_mix(pip, binding_buffer_vol * 0.9, bind_res, reps=5)
    pip.aspirate(binding_buffer_vol, bind_res)
    pip.dispense(binding_buffer_vol, sample_plate)
    bead_mix(pip, (binding_buffer_vol + starting_vol) * 0.9, sample_plate, reps=7)
    pip.home()

    # Shake for binding incubation
    h_s.set_and_wait_for_shake_speed(rpm=1800)
    ctx.delay(minutes=10)
    h_s.deactivate_shaker()
    h_s.open_labware_latch()

    # Transfer plate to magnet
    ctx.move_labware(
        sample_plate,
        DECK_SLOT_MAG_PLATE,
        use_gripper=USE_GRIPPER,
        pick_up_offset=grip_offset("pick-up", "heater-shaker", slot=DECK_SLOT_HEATER_SHAKER),
        drop_offset=grip_offset("drop", "mag-plate")
    )

    ctx.delay(minutes=settling_time, msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet.')

    # Remove Supernatant and move off magnet
    pip.aspirate(1000, sample_plate.bottom(0.3))
    pip.dispense(1000, waste)
    if starting_vol + binding_buffer_vol > 1000:
        pip.aspirate(1000, sample_plate.bottom(0.3))
        pip.dispense(1000, waste)

    # Transfer plate from magnet to H/S
    ctx.move_labware(
        sample_plate,
        h_s,
        use_gripper=USE_GRIPPER,
        pick_up_offset=grip_offset("pick-up", "mag-plate"),
        drop_offset=grip_offset("drop", "heater-shaker", slot=DECK_SLOT_HEATER_SHAKER)
    )

    h_s.close_labware_latch()

    # Washes
    for i in range(num_washes):
        pip.aspirate(wash_vol, wash_res)
        pip.dispense(wash_vol, sample_plate)
        resuspend_pellet(pip, wash_vol * 0.9, sample_plate, reps=3, mm_from_bottom=1)

        pip.home()

        h_s.set_and_wait_for_shake_speed(rpm=1800)
        ctx.delay(minutes=2)
        h_s.deactivate_shaker()
        h_s.open_labware_latch()

        # Transfer plate to magnet
        ctx.move_labware(
            sample_plate,
            DECK_SLOT_MAG_PLATE,
            use_gripper=USE_GRIPPER,
            pick_up_offset=grip_offset("pick-up", "heater-shaker", slot=DECK_SLOT_HEATER_SHAKER),
            drop_offset=grip_offset("drop", "mag-plate")
        )

        ctx.delay(minutes=settling_time, msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet.')

        # Remove Supernatant and move off magnet
        pip.aspirate(1000, sample_plate.bottom(0.3))
        pip.dispense(1000, bind_res.top())
        if wash_vol > 1000:
            pip.aspirate(1000, sample_plate.bottom(0.3))
            pip.dispense(1000, bind_res.top())

        # Transfer plate from magnet to H/S
        ctx.move_labware(
            sample_plate,
            h_s,
            use_gripper=USE_GRIPPER,
            pick_up_offset=grip_offset("pick-up", "mag-plate"),
            drop_offset=grip_offset("drop", "heater-shaker", slot=DECK_SLOT_HEATER_SHAKER)
        )
        h_s.close_labware_latch()

    # Dry beads
    drybeads = 10  # Number of minutes you want to dry for
    for beaddry in np.arange(drybeads, 0, -0.5):
        ctx.delay(minutes=0.5, msg='There are ' + str(beaddry) + ' minutes left in the drying step.')

    # Elution
    pip.aspirate(elution_vol, elution_res)
    pip.dispense(elution_vol, sample_plate)
    resuspend_pellet(pip, elution_vol * 0.9, sample_plate, reps=3, mm_from_bottom=1)
    pip.home()

    h_s.set_and_wait_for_shake_speed(rpm=2000)
    ctx.delay(minutes=5, msg='Please wait 5 minutes to allow dna to elute from beads.')
    h_s.deactivate_shaker()
    h_s.open_labware_latch()

    # Transfer plate to magnet
    ctx.move_labware(
        sample_plate,
        DECK_SLOT_MAG_PLATE,
        use_gripper=USE_GRIPPER,
        pick_up_offset=grip_offset("pick-up", "heater-shaker", slot=DECK_SLOT_HEATER_SHAKER),
        drop_offset=grip_offset("drop", "mag-plate")
    )

    ctx.delay(minutes=settling_time, msg='Please wait ' + str(settling_time) + ' minute(s) for beads to pellet.')

    pip.aspirate(elution_vol, sample_plate)
    pip.dispense(elution_vol, elution_plate)
    pip.drop_tip(tips_b)

    pip.home()
