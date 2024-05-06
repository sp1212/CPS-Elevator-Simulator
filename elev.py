import csv
import random



fields = ["time_step", "start_floor", "destination_floor"]

num_floors = 5
filename = f"normal_{num_floors}.csv"

with open(filename, 'w') as file:
    writer = csv.writer(file)

    writer.writerow(['time_step', 'start_floor', 'destination_floor'])


    for i in range(1000):
        num_request = random.randint(1, 10)

        if num_request == 5:
            continue

        for ii in range(num_request):
            if random.randint(0,10) < 5:
                continue
            start_floor = random.randint(1, num_floors)
            dest_floor = random.randint(1, num_floors)
            while dest_floor == start_floor:
                dest_floor = random.randint(1, num_floors)

            writer.writerow([i,start_floor, dest_floor])

        
