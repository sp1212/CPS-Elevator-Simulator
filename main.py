# This code was adapted with the help of ChatGPT

import csv
import sys
from itertools import chain

import pandas as pd 
import matplotlib.pyplot as plt 



class Elevator:
    def __init__(self, num_floors, scheduling_method='FCFS'):
        self.current_floor = 1  # Starts at the lowest floor
        self.num_floors = num_floors
        self.direction = 1  # Initialize direction to go up initially
        self.door_open = False
        self.time_to_next_action = 0
        self.requests = []  # Future requests pending activation
        self.active_requests = []  # Requests ready for processing
        self.passengers = []  # Passengers currently in the elevator
        self.scheduling_method = scheduling_method
        self.target_floor = None  # Next target to stop at
        self.floors_traversed = 0  # Initialize total floors traversed counter
        self.requests_completed = 0  # Initialize total completed requests counter
        self.max_passengers = 6  # Maximum number of passengers allowed in the elevator

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
        if self.target_floor is not None:
            step = 1 if self.target_floor > self.current_floor else -1
            self.current_floor += step
            self.floors_traversed += 1
            self.time_to_next_action = 2

    def process_requests(self):
        # Process passengers reaching their destination
        for passenger in list(self.passengers):
            if passenger[2] == self.current_floor:
                self.open_doors()
                self.passengers.remove(passenger)
                self.requests_completed += 1  # Increment request completion count

        # Board new passengers if there is capacity
        if len(self.passengers) < self.max_passengers:
            for request in list(self.active_requests):
                if request[1] == self.current_floor and len(self.passengers) < self.max_passengers:
                    self.open_doors()
                    self.passengers.append(request)
                    self.active_requests.remove(request)
                    if len(self.passengers) >= self.max_passengers:
                        break

        if not self.door_open:
            self.update_target_floor()

    def update_target_floor(self):
        destinations = [p[2] for p in self.passengers]  # Destinations of current passengers
        request_destinations = [r[1] for r in self.active_requests]

        if self.scheduling_method == 'SSTF':
            # Combine destinations of passengers and active request floors if below capacity
            all_destinations = destinations + ([r[1] for r in self.active_requests if len(self.passengers) < self.max_passengers])
            if all_destinations:
                self.target_floor = min(all_destinations, key=lambda x: abs(x - self.current_floor))
            else:
                # If no destinations or active requests, the elevator stays idle until a new request arrives
                self.target_floor = None

        elif self.scheduling_method == 'Directional':
            in_direction = list(filter(lambda x: (x - self.current_floor) * self.direction > 0, destinations + request_destinations))
            if not in_direction:
                self.direction *= -1  # Reverse the direction if no more floors in the current direction
                in_direction = list(filter(lambda x: (x - self.current_floor) * self.direction > 0, destinations + request_destinations))
            self.target_floor = in_direction[0] if in_direction else None

        else:  # FCFS
            # Prioritize destinations of passengers first, then the requests if there is space
            if destinations:
                self.target_floor = destinations[0]
            elif len(self.passengers) < self.max_passengers and request_destinations:
                self.target_floor = request_destinations[0]
            else:
                self.target_floor = None

        # Fallback to ensure the elevator doesn't idle if there are pending requests or passenger destinations
        if self.target_floor is None and (destinations or request_destinations):
            self.target_floor = destinations[0] if destinations else request_destinations[0] if request_destinations else None


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
    def __init__(self, num_floors, scheduling_method, input_file):
        self.elevator = Elevator(num_floors, scheduling_method)
        self.time_step = 0
        self.num_floors = num_floors
        self.scheduling_method = scheduling_method
        self.input_file = input_file
        self.load_requests()

    def load_requests(self):
        with open(self.input_file, newline='') as csvfile:
            request_reader = csv.reader(csvfile, delimiter=',')
            next(request_reader)  # Skip header
            for row in request_reader:
                time_step, start_floor, destination_floor = int(row[0]), int(row[1]), int(row[2])
                self.elevator.requests.append((time_step, start_floor, destination_floor))

    def run(self):
        total_time_steps = 6969696969  # Maximum time steps as a timeout
        output_lines = []  # Collect all output lines to write at once
        output_lines.append("Time Step,Current Floor,Doors Status,Moving Status,Requests\n")  # Column header
        while self.time_step < total_time_steps and (self.elevator.requests or self.elevator.active_requests or self.elevator.passengers):
            self.elevator.move(self.time_step)
            moving_status = 'Moving' if not self.elevator.door_open and self.elevator.current_floor != self.elevator.target_floor else 'Stationary'
            doors_status = 'Open' if self.elevator.door_open else 'Closed'
            requests_status = self.elevator.format_requests()
            output_lines.append(f"{self.time_step},{self.elevator.current_floor},{doors_status},{moving_status},{requests_status}\n")
            self.time_step += 1
            if not self.elevator.requests and not self.elevator.active_requests and not self.elevator.passengers:
                break  # All requests are handled, terminate early

        with open("output.txt", "w") as file:
            # Write the operation data
            file.writelines(output_lines)
            file.write(f"Scheduling Method: {self.scheduling_method}, Floors: {self.num_floors}, Input File: {self.input_file}\n")
            file.write(f"Total Floors Traversed: {self.elevator.floors_traversed}\n")
            file.write(f"Total Time Steps Taken: {self.time_step}\n")
            file.write(f"Total Requests Completed: {self.elevator.requests_completed}\n")

# Assuming the CSV input file structure is correct and exists, run the simulation:

# Visualization
def plot_metrics(scenario, metric):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=False)  # sharey is set to False
    for i, floor in enumerate([5, 10, 50]):
        subset = df[(df['Scenario'] == scenario) & (df['Floors'] == floor)]
        subset.sort_values(by='Scheduling Method').plot(
            x='Scheduling Method', y=metric, kind='bar', ax=axes[i], legend=None, title=f"{metric} for {floor} Floors"
        )
        axes[i].set_xlabel('')
        axes[i].set_ylabel(metric)
    plt.suptitle(f'{metric} Comparison Across Floors for {scenario} Scenario')
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for the title
    filename = f'{scenario}_{metric.replace(" ", "_")}.png'
    plt.savefig(filename)  # Ensure saving happens after plotting
    plt.close(fig)  # Close the figure to free up memory



def run_and_plot_all():
    results = []

    # Assuming Simulation is a class you have that can run these simulations
    for f in ['test/normal_', 'test/opening_', 'test/closing_']:
        for ff in [5, 10, 50]:
            for fff in ['Directional', 'FCFS', 'SSTF']:
                sim = Simulation(num_floors=ff, scheduling_method=fff, input_file=f"{f}{ff}.csv")
                sim.run()
                print(f"Scheduling Method: {sim.scheduling_method}, Floors: {sim.num_floors}, Input File: {sim.input_file}")
                print(f"Total Floors Traversed: {sim.elevator.floors_traversed}")
                print(f"Total Time Steps Taken: {sim.time_step}")
                print(f"Total Requests Completed: {sim.elevator.requests_completed}")
                results.append({
                    'Scenario': f.split('/')[1],
                    'Floors': ff,
                    'Scheduling Method': fff,
                    'Total Floors Traversed': sim.elevator.floors_traversed,
                    'Total Time Steps Taken': sim.time_step,
                    'Total Requests Completed': sim.elevator.requests_completed
                })
                print(f"{f}{ff}.csv --> {fff}")

    # Convert list to DataFrame
    df = pd.DataFrame(results)
    for scenario in df['Scenario'].unique():
        plot_metrics(scenario, 'Total Floors Traversed')
        plot_metrics(scenario, 'Total Time Steps Taken')


if __name__ == "__main__":


    if len(sys.argv) == 4:
        sim = Simulation(num_floors=sys.argv[2], scheduling_method=str(sys.argv[3]), input_file=str(sys.argv[1]))
        sim.run()
        print(f"Scheduling Method: {sim.scheduling_method}, Floors: {sim.num_floors}, Input File: {sim.input_file}\n")
        print(f"Total Floors Traversed: {sim.elevator.floors_traversed}\n")
        print(f"Total Time Steps Taken: {sim.time_step}\n")
        print(f"Total Requests Completed: {sim.elevator.requests_completed}\n")
        
    else:
        print("Usage: python run.py <input_file> <num_floors> <scheduling_method>")
        print("\t<scheduling_method> = {Directional, FCFS, SSTF}")

