import sys
from typing import NamedTuple
import unittest


# ===========================================================================
#                            Imported Modules
# ===========================================================================
class RadarBlip(NamedTuple):
    fish_id: int
    dir: str  # "TL"RADAR_TOP_LEFT etc.


class Drone:
    drone_id: int
    # pos: Vector #type: ignore
    dead: bool
    battery: int
    scans: list[int]
    # role: DroneRole # type: ignore
    # target: Vector  # type: ignore
    waiting: bool
    is_light_enabled: bool
    context: dict[str, object]
    monsters_nearby = dict[int, int]


RADAR_TOP_LEFT = "TL"
RADAR_TOP_RIGHT = "TR"
RADAR_BOTTOM_RIGHT = "BR"
RADAR_BOTTOM_LEFT = "BL"
# ===========================================================================


class Radar:
    drone: Drone
    detected: dict[str, list[RadarBlip]]

    def __init__(self, drone: Drone, radar_blips: list[RadarBlip]) -> None:
        self.drone = drone
        self.detected = {
            RADAR_TOP_LEFT: [],
            RADAR_TOP_RIGHT: [],
            RADAR_BOTTOM_LEFT: [],
            RADAR_BOTTOM_RIGHT: [],
        }
        self.scan(radar_blips)

    def get_blips(self, direction: str) -> list[RadarBlip]:
        return self.detected[direction]

    def scan(self, radar_blips: RadarBlip) -> None:
        for blip in radar_blips:
          if blip.dir == RADAR_TOP_LEFT:
              self.detected[RADAR_TOP_LEFT].append(blip)
          elif blip.dir == RADAR_TOP_RIGHT:
              self.detected[RADAR_TOP_RIGHT].append(blip)
          elif blip.dir == RADAR_BOTTOM_LEFT:
              self.detected[RADAR_BOTTOM_LEFT].append(blip)
          elif blip.dir == RADAR_BOTTOM_RIGHT:
              self.detected[RADAR_BOTTOM_RIGHT].append(blip)
          else:
              raise ValueError("Invalid blip direction")


class MyTestCase(unittest.TestCase):
    radar_blips = [
            RadarBlip(1, RADAR_TOP_LEFT),
            RadarBlip(2, RADAR_TOP_LEFT),
            RadarBlip(3, RADAR_TOP_RIGHT),
            RadarBlip(4, RADAR_TOP_RIGHT),
            RadarBlip(5, RADAR_BOTTOM_LEFT),
            RadarBlip(6, RADAR_BOTTOM_LEFT),
            RadarBlip(7, RADAR_BOTTOM_RIGHT),
            RadarBlip(8, RADAR_BOTTOM_RIGHT),
        ]

    def test_init_radar(self):
        drone = Drone()
        drone.drone_id = 1


        radar = Radar(drone, self.radar_blips)
        self.maxDiff = None
        self.assertEqual(
            radar.detected,
            {
                RADAR_TOP_LEFT: [
                    RadarBlip(1, RADAR_TOP_LEFT),
                    RadarBlip(2, RADAR_TOP_LEFT),
                ],
                RADAR_TOP_RIGHT: [
                    RadarBlip(3, RADAR_TOP_RIGHT),
                    RadarBlip(4, RADAR_TOP_RIGHT),
                ],
                RADAR_BOTTOM_LEFT: [
                    RadarBlip(5, RADAR_BOTTOM_LEFT),
                    RadarBlip(6, RADAR_BOTTOM_LEFT),
                ],
                RADAR_BOTTOM_RIGHT: [
                    RadarBlip(7, RADAR_BOTTOM_RIGHT),
                    RadarBlip(8, RADAR_BOTTOM_RIGHT),
                ],
            },
        )

    def test_get_blips(self):
        drone = Drone()
        drone.drone_id = 1

        radar = Radar(drone, self.radar_blips)
        self.assertEqual(
            radar.get_blips(RADAR_TOP_LEFT),
            [
                RadarBlip(1, RADAR_TOP_LEFT),
                RadarBlip(2, RADAR_TOP_LEFT),
            ],
        )


if __name__ == "__main__":
    unittest.main()
