# -*- coding: utf-8 -*-

from astrobox.space_field import SpaceField
from karpov import KarpovDrone

DRONES_QTY = 5


def main():
    KarpovDrone.set_logger()
    scene = SpaceField(speed=3, asteroids_count=15)
    drones = [KarpovDrone() for _ in range(DRONES_QTY)]
    scene.go()


if __name__ == '__main__':
    main()
