# -*- coding: utf-8 -*-
import datetime
import logging

from astrobox.core import Drone


class KarpovDrone(Drone):
    my_team = []

    # будем здесь хранить доступный элериум на астероиде с учетом уже вылетевших на его сбор дронов
    my_asteroids = {}

    distance_flown_empty = 0
    distance_flown_partially_loaded = 0
    distance_flown_full = 0

    log = None

    @staticmethod
    def set_logger():
        log = logging.getLogger('karpov_drones_logger')
        log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('{asctime} - {levelname} - {message}', style='{')

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        log.addHandler(stream_handler)

        KarpovDrone.log = log

    def on_born(self):

        self.start_time = datetime.datetime.now()

        if len(self.my_team) == 0:  # это первый дрон
            KarpovDrone.set_logger()
            for ast in self.asteroids:
                self.my_asteroids[ast.id] = ast.payload

        self.log.disabled = False
        self.my_team.append(self)

        self.target = self._get_my_asteroid()
        self.move_at(self.target)

    def get_asteroid_by_id(self, id):
        for ast in self.asteroids:
            if ast.id == id:
                return ast

    def _get_my_asteroid(self):
        destination = None

        if self.free_space == 0:
            destination = self.mothership

        if not destination:
            for ast_id, ast_payload in self.my_asteroids.items():
                if ast_payload > 0:
                    self.my_asteroids[ast_id] -= min(self.free_space, ast_payload)
                    destination = self.get_asteroid_by_id(ast_id)
                    break
            else:
                destination = self.mothership

        distance_to_destination = self.distance_to(destination)

        if self.fullness == 0:
            self.distance_flown_empty += distance_to_destination
        elif self.fullness < 1:
            self.distance_flown_partially_loaded += distance_to_destination
        else:
            self.distance_flown_full += distance_to_destination

        return destination

    def on_stop_at_asteroid(self, asteroid):
        self.load_from(asteroid)

    def on_load_complete(self):

        self.target = self._get_my_asteroid()
        self.move_at(self.target)

    def on_stop_at_mothership(self, mothership):
        self.unload_to(mothership)

    def on_unload_complete(self):

        if self.all_loot_collected():
            self.my_team.remove(self)

            if len(self.my_team) == 0:  # все мои дроны завершили активность
                self.time_elapsed = datetime.datetime.now() - self.start_time
                self.log.info(
                    f'Мои дроны собрали элериум со всех астероидов! Потребовалось времени: {self.time_elapsed}. Ура!')
                self.log.info(f'Пролетели расстояние пустыми: {self.distance_flown_empty}')
                self.log.info(f'Пролетели расстояние частично загруженными: {self.distance_flown_partially_loaded}')
                self.log.info(f'Пролетели расстояние полностью загруженными: {self.distance_flown_full}')
                return

        self.target = self._get_my_asteroid()
        self.move_at(self.target)

    def on_wake_up(self):
        self.target = self._get_my_asteroid()
        if self.target:
            self.move_at(self.target)

    def all_loot_collected(self):
        return all(payload == 0 for payload in self.my_asteroids.values())
