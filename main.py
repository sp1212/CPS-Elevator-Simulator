import csv

class Elevator:
    def __init__(self, num_floors, scheduling_method='FCFS'):
        self.current_floor = 1  # Starts at the lowest floor
        self.num_floors = num_floors
        self.direction = 1  # 1 for up, -1 for down
        self.door_open = False
        self.time_to_next_action = 0
        self.requests = []  # Future requests
        self.active_requests = []  # Currently being processed requests
        self.passengers = []  # Passengers currently in the elevator
        self.scheduling_method = scheduling_method
        self.target_floor = None  # Next target to stop at

    def move(self, current_time_step):
        # Activate requests due at current time step
        while self.requests and self.requests[0][0] == current_time_step:
            self.active_requests.append(self.requests.pop(0))

        if self.time_to_next_action > 0:
            self.time_to_next_action -= 1
            return

        if self.door_open:
            self.close_doors()
        elif self.target_floor and self.current_floor != self.target_floor:
            self.move_towards_target()
        else:
            self.process_next_request()

    def move_towards_target(self):
        step = 1 if self.target_floor > self.current_floor else -1
        self.current_floor += step
        self.time_to_next_action = 2  # Time to move one floor

    def process_next_request(self):
        # Check and drop off any passengers whose destination is the current floor
        for passenger in self.passengers[:]:  # Copy list for safe iteration
            if passenger[3] == self.current_floor:
                self.open_doors()  # Open doors to let passengers out
                self.passengers.remove(passenger)

        # Pick up new passengers at the current floor
        for request in self.active_requests[:]:  # Copy list for safe iteration
            if request[1] == self.current_floor:
                self.open_doors()  # Open doors to pick up new passengers
                self.passengers.append(request)
                self.active_requests.remove(request)

        # If no specific action, find the next target
        if not self.door_open:
            self.set_next_target()

    def set_next_target(self):
        # Determine the next target based on passenger destinations and active requests
        if self.passengers:
            self.target_floor = min(self.passengers, key=lambda x: abs(x[3] - self.current_floor))[3]
        elif self.active_requests:
            self.target_floor = min(self.active_requests, key=lambda x: abs(x[1] - self.current_floor))[1]

    def open_doors(self):
        self.door_open = True
        self.time_to_next_action = 5  # Time for doors to open and close

    def close_doors(self):
        self.door_open = False

    def format_requests(self):
        # Show both active requests and passengers being transported
        active = '; '.join(f"Active: ({r[1]}, {r[2]}, {r[3]})" for r in self.active_requests)
        passengers = '; '.join(f"Passenger: ({r[1]}, {r[2]}, {r[3]})" for r in self.passengers)
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
            next(request_reader)  # Skip header
            for row in request_reader:
                time_step, start_floor, direction, destination_floor = int(row[0]), int(row[1]), row[2], int(row[3])
                self.elevator.requests.append((time_step, start_floor, direction, destination_floor))

    def run(self, total_time_steps):
        with open("output.txt", "w") as file:
            file.write(f"Scheduling Method: {self.scheduling_method}, Floors: {self.num_floors}, Total Time Steps: {total_time_steps}\n")
            file.write("Time Step,Current Floor,Doors Status,Moving Status,Start Floor,Stop Floor,Requests\n")
            for _ in range(total_time_steps):
                self.elevator.move(self.time_step)
                moving_status = 'Moving' if not self.elevator.door_open and self.elevator.current_floor != self.elevator.target_floor else 'Stationary'
                doors_status = 'Open' if self.elevator.door_open else 'Closed'
                start_floor = self.elevator.current_floor if self.elevator.door_open else ''
                stop_floor = self.elevator.target_floor if self.elevator.door_open else ''
                requests_status = self.elevator.format_requests()
                file.write(f"{self.time_step},{self.elevator.current_floor},{doors_status},{moving_status},{start_floor},{stop_floor},{requests_status}\n")
                self.time_step += 1

# Assuming the CSV input file structure is correct and exists, run the simulation:
sim = Simulation(num_floors=10, scheduling_method='FCFS')
sim.run(100)  # Run the simulation for 100 time steps
