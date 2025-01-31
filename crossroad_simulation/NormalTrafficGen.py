from multiprocessing import Process

class NormalTrafficGen:
    def __init__(self, vehicule_id):
        self.vehicle_id = vehicule_id
        self.vehicle_type = vehicle