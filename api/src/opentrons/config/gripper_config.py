from __future__ import annotations
from dataclasses import dataclass
import logging
from typing import List, Tuple, Optional, Dict

from opentrons_shared_data.gripper import load_definition
from opentrons_shared_data.gripper.dev_types import (
    GripperCustomizableFloat,
    GripperOffset,
    GripperSchemaVersion,
    GripperModel,
    GripperName,
)
from .types import Offset

log = logging.getLogger(__name__)

DEFAULT_GRIPPER_CALIBRATION_OFFSET = [0.0, 0.0, 0.0]


"""
Gripper load measurement
========================
10/13/2022

To lift a 1.5 kg load,
the velocity should be 19 mm/s & acceleration at 19 mm/s^2.
Run current: 0.7 A and Hold current: 0.2 A.
"""


@dataclass(frozen=True)
class GripperConfig:
    display_name: str
    name: GripperName
    model: GripperModel
    z_idle_current: float
    z_active_current: float
    jaw_reference_voltage: float
    jaw_duty_cycle_polynomial: List[Tuple[int, float]]
    base_offset_from_mount: Offset
    jaw_center_offset_from_base: Offset
    pin_one_offset_from_base: Offset
    pin_two_offset_from_base: Offset
    quirks: List[str]
    jaw_sizes_mm: Dict[str, float]


def _verify_value(
    def_specs: GripperCustomizableFloat, override: Optional[float] = None
) -> float:
    if override and def_specs.min <= override <= def_specs.max:
        return override
    return def_specs.default_value


def _get_offset(def_offset: GripperOffset) -> Offset:
    return (def_offset.x, def_offset.y, def_offset.z)


def info_num_to_model(num: str) -> GripperModel:
    major_model = num[0]
    model_map = {"0": GripperModel.V1, "1": GripperModel.V1}
    return model_map[major_model]


def load(
    gripper_model: GripperModel, gripper_id: Optional[str] = None
) -> GripperConfig:
    gripper_def = load_definition(version=GripperSchemaVersion.V1, model=gripper_model)
    return GripperConfig(
        name="gripper",
        display_name=gripper_def.display_name,
        model=gripper_def.model,
        z_idle_current=_verify_value(gripper_def.z_idle_current),
        z_active_current=_verify_value(gripper_def.z_active_current),
        jaw_reference_voltage=_verify_value(gripper_def.jaw_reference_voltage),
        jaw_duty_cycle_polynomial=gripper_def.jaw_duty_cycle_polynomial,
        base_offset_from_mount=_get_offset(gripper_def.base_offset_from_mount),
        jaw_center_offset_from_base=_get_offset(
            gripper_def.jaw_center_offset_from_base
        ),
        pin_one_offset_from_base=_get_offset(gripper_def.pin_one_offset_from_base),
        pin_two_offset_from_base=_get_offset(gripper_def.pin_two_offset_from_base),
        quirks=gripper_def.quirks,
        jaw_sizes_mm=gripper_def.jaw_sizes_mm,
    )


def duty_cycle_by_force(newton: float, sequence: List[Tuple[int, float]]) -> float:
    """
    Takes a force in newton and a sequence representing the polymomial
    equation of the gripper's force function in terms of duty cycle, where the
    integer represent the degree of the indeterminate (duty cycle), and
    the float representing its constant coefficient.

    The values come from shared-data/gripper/definitions/gripperVx.json.

    :return: the duty-cycle value for the specified force
    """
    return sum(ele[1] * (newton ** ele[0]) for ele in sequence)
