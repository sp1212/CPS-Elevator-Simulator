# This code was adapted with the help of ChatGPT

from random import randint, choice

class Elevator:
    def __init__(self, num_floors, scheduling_method='FCFS'):
        self.current_floor = 1  # Elevator starts at the lowest floor
        self.num_floors = num_floors
        self.direction = 1  # 1 for up, -1 for down
        self.door_open = False
        self.time_to_next_action = 0
        self.requests = []  # Requests are tuples (start_floor, direction, destination_floor)
        self.scheduling_method = scheduling_method
        self.target_floor = None  # Target floor to stop at

    def move(self):
        if self.time_to_next_action > 0:
            self.time_to_next_action -= 1
            return

        if self.door_open:
            self.close_doors()
        else:
            if self.target_floor and self.current_floor != self.target_floor:
                self.move_towards_target()
            else:
                next_request = self.next_request()
                if next_request:
                    self.process_request(next_request)
                else:
                    self.target_floor = None  # No target when idle

    def move_towards_target(self):
        step = 1 if self.target_floor > self.current_floor else -1
        self.current_floor += step
        self.time_to_next_action = 2  # Time to move one floor

    def next_request(self):
        if not self.requests:
            return None

        if self.scheduling_method == 'FCFS':
            return self.requests[0]
        elif self.scheduling_method == 'SSTF':
            return min(self.requests, key=lambda req: abs(self.current_floor - req[0]))
        elif self.scheduling_method == 'Directional':
            direction_requests = [req for req in self.requests if (req[0] - self.current_floor) * self.direction > 0]
            if not direction_requests:
                self.direction *= -1
                direction_requests = self.requests
            return min(direction_requests, key=lambda req: abs(self.current_floor - req[0]))

    def process_request(self, request):
        start_floor, direction, destination_floor = request
        self.target_floor = start_floor
        if self.current_floor == start_floor:
            self.open_doors()
            self.target_floor = destination_floor  # Update the target to destination after door closes
            self.requests.remove(request)
        else:
            self.time_to_next_action = 2 * abs(self.current_floor - start_floor)  # Schedule movement if needed

    def open_doors(self):
        self.door_open = True
        self.time_to_next_action = 5

    def close_doors(self):
        self.door_open = False
        self.time_to_next_action = 5

    def add_request(self, start_floor, direction):
        if direction == 'up' and start_floor < self.num_floors:
            destination_floor = randint(start_floor + 1, self.num_floors)
        elif direction == 'down' and start_floor > 1:
            destination_floor = randint(1, start_floor - 1)
        else:
            return  # Invalid request for top or bottom floors
        self.requests.append((start_floor, direction, destination_floor))

    def format_requests(self):
        return '; '.join(f"({r[0]}, {r[1]}, {r[2]})" for r in self.requests)

class Simulation:
    def __init__(self, num_floors, scheduling_method):
        self.elevator = Elevator(num_floors, scheduling_method)
        self.time_step = 0
        self.num_floors = num_floors
        self.scheduling_method = scheduling_method

    def run(self, total_time_steps):
        with open("output.txt", "w") as file:
            file.write(f"Scheduling Method: {self.scheduling_method}, Floors: {self.num_floors}, Total Time Steps: {total_time_steps}\n")
            file.write("Time Step,Current Floor,Doors Status,Moving Status,Start Floor,Stop Floor,Requests\n")
            for _ in range(total_time_steps):
                if self.time_step % 10 == 0:
                    floor = randint(1, self.elevator.num_floors)
                    direction = choice(['up', 'down'])
                    self.elevator.add_request(floor, direction)

                self.elevator.move()
                moving_status = 'Moving' if self.elevator.target_floor and not self.elevator.door_open and self.elevator.current_floor != self.elevator.target_floor else 'Stationary'
                start_floor = self.elevator.current_floor if self.elevator.door_open else ''
                stop_floor = self.elevator.target_floor if self.elevator.door_open else ''
                requests_status = self.elevator.format_requests()
                file.write(f"{self.time_step},{self.elevator.current_floor},{'Open' if self.elevator.door_open else 'Closed'},{moving_status},{start_floor},{stop_floor},{requests_status}\n")
                self.time_step += 1

# Create and run the simulation for each scheduling method
sim_fcfs = Simulation(num_floors=10, scheduling_method='FCFS')
sim_sstf = Simulation(num_floors=10, scheduling_method='SSTF')
sim_scan = Simulation(num_floors=10, scheduling_method='Directional')

sim_fcfs.run(100)  # Run the simulation for 100 time steps
