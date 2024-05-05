# This code was adapted with the help of ChatGPT

import csv
from itertools import chain

class Elevator:
    def __init__(self, num_floors, scheduling_method='FCFS'):
        self.current_floor = 1
        self.num_floors = num_floors
        self.direction = 1  # 1 for up, -1 for down
        self.door_open = False
        self.time_to_next_action = 0
        self.requests = []  # Future requests pending activation
        self.active_requests = []  # Requests ready for processing
        self.passengers = []  # Passengers currently in the elevator
        self.scheduling_method = scheduling_method
        self.target_floor = None  # Next target to stop at

    def move(self, current_time_step):
        while self.requests and self.requests[0][0] == current_time_step:
            self.active_requests.append(self.requests.pop(0))

        if self.time_to_next_action > 0:
            self.time_to_next_action -= 1
            return

        if self.door_open:
            self.close_doors()
        elif not self.active_requests and not self.passengers:
            self.target_floor = None
        elif self.target_floor and self.current_floor != self.target_floor:
            self.move_towards_target()
        else:
            self.process_requests()

    def move_towards_target(self):
        step = 1 if self.target_floor > self.current_floor else -1
        self.current_floor += step
        self.time_to_next_action = 2

    def process_requests(self):
        for passenger in list(self.passengers):
            if passenger[2] == self.current_floor:
                self.open_doors()
                self.passengers.remove(passenger)

        for request in list(self.active_requests):
            if request[1] == self.current_floor:
                self.open_doors()
                self.passengers.append(request)
                self.active_requests.remove(request)

        if not self.door_open:
            self.update_target_floor()

    def update_target_floor(self):
        if self.scheduling_method == 'SSTF':
            all_destinations = [p[2] for p in self.passengers] + [r[1] for r in self.active_requests]
            if all_destinations:
                self.target_floor = min(all_destinations, key=lambda x: abs(x - self.current_floor))
        elif self.scheduling_method == 'Directional':
            current_destinations = [p[2] for p in self.passengers] + [r[1] for r in self.active_requests]
            in_direction = list(filter(lambda x: (x - self.current_floor) * self.direction > 0, current_destinations))
            if not in_direction and current_destinations:
                self.direction *= -1
                in_direction = list(filter(lambda x: (x - self.current_floor) * self.direction > 0, current_destinations))
            if in_direction:
                self.target_floor = sorted(in_direction, key=lambda x: abs(x - self.current_floor))[0]
            else:
                self.target_floor = None
        else:
            if self.passengers:
                self.target_floor = self.passengers[0][2]
            elif self.active_requests:
                self.target_floor = self.active_requests[0][1]

    def open_doors(self):
        self.door_open = True
        self.time_to_next_action = 5

    def close_doors(self):
        self.door_open = False

    def format_requests(self):
        active = '; '.join(f"Active: ({r[0]}, {r[1]}, {r[2]})" for r in self.active_requests)
        passengers = '; '.join(f"Passenger: ({r[0]}, {r[1]}, {r[2]})" for r in self.passengers)
        return active + " | " + passengers if active and passengers else active + passengers

class Simulation:
    def __init__(self, num_floors, scheduling_method):
        self.elevator = Elevator(num_floors, scheduling_method)
        self.time_step = 0
        self.num_floors = num_floors
        self.scheduling_method = scheduling_method
        self.load_requests()

    def load_requests(self):
        with open('input.csv', newline='') as csvfile:
            request_reader = csv.reader(csvfile, delimiter=',')
            next(request_reader)
            for row in request_reader:
                time_step, start_floor, destination_floor = int(row[0]), int(row[1]), int(row[2])
                self.elevator.requests.append((time_step, start_floor, destination_floor))

    def run(self, total_time_steps):
        with open("output.txt", "w") as file:
            file.write(f"Scheduling Method: {self.scheduling_method}, Floors: {self.num_floors}, Total Time Steps: {total_time_steps}\n")
            file.write("Time Step,Current Floor,Doors Status,Moving Status,Requests\n")
            for _ in range(total_time_steps):
                self.elevator.move(self.time_step)
                moving_status = 'Moving' if not self.elevator.door_open and self.elevator.current_floor != self.elevator.target_floor else 'Stationary'
                doors_status = 'Open' if self.elevator.door_open else 'Closed'
                requests_status = self.elevator.format_requests()
                file.write(f"{self.time_step},{self.elevator.current_floor},{doors_status},{moving_status},{requests_status}\n")
                self.time_step += 1

# Assuming the CSV input file structure is correct and exists, run the simulation:
sim = Simulation(num_floors=10, scheduling_method='FCFS')
sim.run(200)  # Run the simulation for 200 time steps
