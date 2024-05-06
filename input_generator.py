import csv
import random



fields = ["time_step", "start_floor", "destination_floor"]


def closing(num_floors):
    filename = f"closing_{num_floors}.csv"
    with open(filename, 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['time_step', 'start_floor', 'destination_floor'])


        for i in range(250):
            # number of requests to process in a time slice
            num_request = random.randint(1, num_floors)
            

            if(i > 200):
                num_request = int(num_request*.9)
            elif(i > 100):
                num_request = int(num_request*.75)
            elif(i > 0):
                num_request = int(num_request*.5)
            


            # generate each request
            for ii in range(num_request):
                
                # cut some of these requests
                if random.randint(0, 10) < 5:
                    continue
                start_floor = random.randint(1, num_floors)
                dest_floor = 1

                writer.writerow([i,start_floor, dest_floor])


def opening(num_floors):
    filename = f"opening_{num_floors}.csv"
    with open(filename, 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['time_step', 'start_floor', 'destination_floor'])


        for i in range(250):
            # number of requests to process in a time slice
            num_request = random.randint(1, num_floors)
            

            if(i > 200):
                num_request = int(num_request*.5)
            elif(i > 100):
                num_request = int(num_request*.75)
            elif(i > 50):
                num_request = int(num_request*.9)
            


            # generate each request
            for ii in range(num_request):
                
                # cut some of these requests
                if random.randint(0, 10) < 5:
                    continue
                start_floor = 1
                dest_floor = random.randint(1, num_floors)

                writer.writerow([i,start_floor, dest_floor])

        

def normal(num_floors):
    filename = f"normal_{num_floors}.csv"

    with open(filename, 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['time_step', 'start_floor', 'destination_floor'])



        # for each time step
        for i in range(300):

            # the number of requests to process
            # 50% chance there are no requests in this time step
            num_request = random.randint(1, num_floors*2)
            if num_request > num_floors:
                continue

            # generate each request
            for ii in range(num_request):
                # make it more infequent by cutting out half
                if random.randint(0,10) < 5:
                    continue
                start_floor = random.randint(1, num_floors)
                dest_floor = random.randint(1, num_floors)
                while dest_floor == start_floor:
                    dest_floor = random.randint(1, num_floors)

                writer.writerow([i,start_floor, dest_floor])

normal(5)
normal(10)
normal(50)
opening(5)
opening(10)
opening(50)
closing(5)
closing(10)
closing(50)