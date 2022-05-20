import math
import random
from typing import Tuple
import matplotlib.pyplot as plt
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
    """ User Interface.

    Renders the home page when the web page is first loaded.
    """
    return render_template('home.html')


@app.route('/run_scenario', methods=['GET', 'POST'])
def scenario():
    """ Runs the given scenario

    This function takes in the users inputs from the HTML form which are used in the baseline algorithm as well as my
    created algorithm, it will then display another page which shows the results of the test.

    Returns:
        This function returns a new page which displays the results of the tests.

    """
    floor_amount: int = request.form['floors']  # Number of floors in the building
    customer_amount: int = request.form['customers']  # Number of people who want to use the list
    max_capacity: int = request.form['max_capacity']  # Max capacity of the lift

    # Randomly generate people who want to go up / down
    customer_list: list = people(floor_amount, customer_amount)
    customer_list_two: list = list(customer_list)  # Second list of identical people to compare against the baseline
    # Then create the baseline.
    baseline_score = baseline(customer_list, max_capacity, floor_amount)
    print("baseline score: ", baseline_score)
    lift_algorithm_score = lift_algorithm(customer_list_two, max_capacity, floor_amount)
    print("algorithm score: ", lift_algorithm_score)
    return render_template('scenario_output.html', baseline_value=baseline_score, my_value=lift_algorithm_score,
                           floors=floor_amount, customers=customer_amount, capacity=max_capacity)


@app.route('/create_chart', methods=['GET', 'POST'])
def generate_chart_data():
    """ Generate chart data

        This function takes in inputs from the HTML form and uses them to generate x and y coordinate data. The data
        will then be returned.

        Example:
            *Function takes in an alarm scheduled for 9pm on the 12th December 2021*
            Output: The function will append the alarm to a list in the format 'DATE HOUR MINUTE NAME'.

        Returns:
            This function re-renders the home page so that the user can generate another chart or complete a specific
            test.
        """
    floors: int = request.form['chart_floors']  # Number of floors in the building
    customer_limit: float = request.form['chart_customers']  # Customer amount the chart will go up to
    max_capacity: int = request.form['chart_capacity']  # Max capacity of the lift
    baseline_data_set: list = []  # Data from the baseline
    algorithm_data_set: list = []  # Date from my algorithm

    # The graph will have 10 'points', this could be changed but it could take a while for the graph to be made
    customer_points: list = []
    for points in range(10):
        customer_points.append(math.floor((points + 1)/10 * float(customer_limit)))

    # Generation of the data set
    for points in range(10):
        print(points)
        data_point: int = customer_points[points]
        customer_list: list = people(floors, data_point)
        customer_list_two: list = list(customer_list)

        _ = baseline(customer_list, max_capacity, floors)
        baseline_data_set.append(_)
        _ = lift_algorithm(customer_list_two, max_capacity, floors)
        algorithm_data_set.append(_)

    generate_chart(baseline_data_set, algorithm_data_set, customer_points)
    return render_template("home.html")


def people(max_floors: int, people_waiting: int) -> list:
    """ Creates a random list of people

    This function generates a random set of 'people' within the data parameters.

    Example:
        *Function takes in max_floors value of 10 and a people_waiting value of 50*
        Output: The function will generate a list of 50 where the current floor and destination floor will be between
        1 and 10.

    Arguments:
        max_floors:
            (int) Top floor of the building.
        people_waiting:
            (int) Simulated amount of people waiting.

    Returns:
        waiting_list:
            (list) This list stores the generated data.
    """
    waiting_list: list = []  # List of all the people who want to access the lift
    for i in range(0, int(people_waiting)):
        current_floor: int = random.randint(1, int(max_floors))  # Lowest floor will be floor 1
        destination_floor: int = current_floor

        while current_floor == destination_floor:
            destination_floor = random.randint(1, int(max_floors))  # Lowest floor will be floor 1

        if current_floor < destination_floor:
            direction: str = "up"
        else:
            direction: str = "down"

        _ = str(current_floor) + " " + str(destination_floor) + " " + direction
        waiting_list.append(_)

    return waiting_list


def baseline(customers: list, lift_capacity: int, max_floors: int) -> int:
    """ Baseline algorithm

        This function simulates the baseline lift.

        Arguments:
            customers:
                (list) List of customers waiting.
            lift_capacity:
                (int) How many people the lift can hold.
            max_floors:
                (int) Highest floor in the building.

        Returns:
            floors_visited:
                (int) Baseline score.
        """
    lift_current_floor: int = 1  # Starts at floor 1
    lift_list: list = []
    lift_direction: str = "up"  # Current direction of the lift
    floors_visited: int = 0  # Used as a basis to compare algorithms
    while len(customers) > 0:  # While there are still customers waiting
        if len(lift_list) > 0:
            # CHECK IF SOMEONE CAN GET OFF -> IF SO LET THEM OFF
            lift_list = lift_exit(lift_list, lift_current_floor)

        if len(lift_list) < int(lift_capacity):
            #  CHECK IF PEOPLE CAN GET ON -> IF SO LET THEM ON
            customers, lift_list, lift_capacity = lift_enter(customers, lift_list, lift_capacity, lift_current_floor)

        #  GO TO NEXT FLOOR
        if lift_direction == "up":
            if int(lift_current_floor) == int(max_floors):
                lift_current_floor = lift_current_floor - 1
                floors_visited = floors_visited + len(lift_list)
                lift_direction = "down"
            else:
                lift_current_floor = lift_current_floor + 1
                floors_visited = floors_visited + len(lift_list)
        elif lift_direction == "down":
            if int(lift_current_floor) == 1:
                lift_current_floor = lift_current_floor + 1
                floors_visited = floors_visited + len(lift_list)
                lift_direction = "up"
            else:
                lift_current_floor = lift_current_floor - 1
                floors_visited = floors_visited + len(lift_list)
    return floors_visited


def lift_algorithm(customers: list, lift_capacity: int, max_floors: int):
    """ My lift algorithm

        This function simulates my version of a lift control system.

        Arguments:
            customers:
                (list) List of customers waiting.
            lift_capacity:
                (int) How many people the lift can hold.
            max_floors:
                (int) Highest floor in the building.

        Returns:
            floors_visited:
                (int) My algorithm's score.
            """
    lift_current_floor: int = 1  # Starts at floor 1
    lift_list: list = []
    floors_visited: int = 0  # Used as a basis to compare algorithms
    while len(customers) > 0:  # While there are still customers waiting
        if len(lift_list) > 0:
            # CHECK IF SOMEONE CAN GET OFF -> IF SO LET THEM OFF
            lift_list = lift_exit(lift_list, lift_current_floor)

        if len(lift_list) < int(lift_capacity):
            # CHECK IF PEOPLE CAN GET ON -> IF SO LET THEM ON
            customers, lift_list, lift_capacity = lift_enter(customers, lift_list, lift_capacity, lift_current_floor)

        # Find the next floor to go to
        destination_floor: int = decide_next_floor(lift_list, lift_current_floor, max_floors, customers)

        while lift_current_floor != destination_floor:
            if lift_current_floor < int(destination_floor):
                lift_current_floor = lift_current_floor + 1
                floors_visited = floors_visited + len(lift_list)
                if len(lift_list) > 0:
                    # CHECK IF SOMEONE CAN GET OFF -> IF SO LET THEM OFF
                    lift_list = lift_exit(lift_list, lift_current_floor)
                if len(lift_list) < int(lift_capacity):
                    # CHECK IF PEOPLE CAN GET ON -> IF SO LET THEM ON
                    customers, lift_list, lift_capacity = lift_enter(customers, lift_list, lift_capacity,
                                                                     lift_current_floor)

            else:
                lift_current_floor = lift_current_floor - 1
                floors_visited = floors_visited + len(lift_list)
                if lift_current_floor < 1:
                    lift_current_floor = 1
                if len(lift_list) > 0:
                    # CHECK IF SOMEONE CAN GET OFF -> IF SO LET THEM OFF
                    lift_list = lift_exit(lift_list, lift_current_floor)
                if len(lift_list) < int(lift_capacity):
                    # CHECK IF PEOPLE CAN GET ON -> IF SO LET THEM ON
                    customers, lift_list, lift_capacity = lift_enter(customers, lift_list, lift_capacity,
                                                                     lift_current_floor)

    return floors_visited


def decide_next_floor(in_lift: list, current_floor: int, max_floor: int, customer_list: list):
    """ Decides which floor should be visited next

        This function is apart of my algorithm. It takes into account who is in the lift as well as where the lift
        currently is. It uses it position and where the next closest customer is to determine which floor it should
        go to.

        Arguments:
            in_lift:
                (list) Current people in the lift.
            current_floor:
                (int) Current floor the lift is on.
            max_floor:
                (int) Highest floor in the building.
            customer_list:
                (list) List of all the customers waiting - not including the customers in the lift.

        Returns:
            decided_floor:
                (int) The floor which the lift will go to next.
        """
    destination_floors: list = []  # List of all the floors that the people in the lift want to go to
    decided_floor: int = 1  # Default set to 1 so the lift will return there when done

    for i in range(0, len(in_lift)):
        string: str = "".join(in_lift[i])
        position: int = string.find(" ")  # We can find the first space to see the customer's destination floor
        string = string[position + 1:len(string)]
        position_second: int = string.find(" ")  # Second instance of a space in the string
        string = string[0:position_second]
        destination_floors.append(string)

    floor_decided: bool = False  # A floor to go to hasn't been decided
    floor_upper: int = current_floor
    floor_lower: int = current_floor
    match: bool = False  # Floor match not found

    if (len(customer_list) > 0) and (len(destination_floors) < 1):
        temp_decide: int = int(max_floor)
        temp_decide_distance: int = 1000000000000

        for i in range(0, len(customer_list)):
            string = "".join(customer_list[i])
            position: int = string.find(" ")
            string = string[0:position]  # Current floor of the customer

            if int(string) > current_floor:
                _ = int(string) - current_floor
                if _ < temp_decide_distance:
                    temp_decide = int(string)
                    temp_decide_distance = _

            else:
                _ = current_floor - int(string)
                if _ < temp_decide_distance:
                    temp_decide = int(string)
                    temp_decide_distance = _

        decided_floor = temp_decide

    while (floor_decided is False) and (len(destination_floors) > 0):

        if (str(floor_lower) in destination_floors) and (str(floor_upper) in destination_floors):
            temp_floor = floor_upper
            floor_upper = int(floor_upper) + 1
            floor_lower = int(floor_lower) - 1
            if floor_upper == max_floor:
                if match:
                    decided_floor = temp_floor
                else:
                    decided_floor = 1
                floor_decided = True

            if floor_lower < 1:
                if match:
                    decided_floor = temp_floor
                else:
                    decided_floor = 1
                floor_decided = True

        elif (str(floor_lower) not in destination_floors) and (str(floor_upper) not in destination_floors):
            floor_upper = int(floor_upper) + 1
            if floor_upper > int(max_floor):
                floor_upper = max_floor
            floor_lower = floor_lower - 1
            if floor_lower < 1:
                floor_lower = 1

        elif (str(floor_lower) not in destination_floors) and (str(floor_upper) in destination_floors):
            decided_floor = floor_upper
            floor_decided = True

        elif (str(floor_upper) not in destination_floors) and (str(floor_lower) in destination_floors):
            decided_floor = floor_lower
            floor_decided = True

        else:
            decided_floor = 1
            floor_decided = True

    return decided_floor


def lift_exit(in_lift: list, floor: int) -> list:
    """Checks if people can exit on the current floor

        This function checks through the in_lift list to see if they can exit.

        Arguments:
            in_lift:
                (list) List of people in the lift.
            floor:
                (int) Current floor the lift is on.

        Returns:
            in_lift:
                (list) Current people in the lift.
            """
    for i in range(len(in_lift)-1, -1, -1):
        if i < 0:
            return in_lift
        string: str = "".join(in_lift[i])
        position: int = string.find(" ")  # We can find the first space to see the customer's destination floor
        string = string[position+1:len(string)]
        position_second: int = string.find(" ")  # Second instance of a space in the string
        string = string[0:position_second]
        if str(floor) in string:
            in_lift.pop(i)
    return in_lift


def lift_enter(waiting: list, in_lift: list, capacity: int, current_floor: int) -> Tuple[list, list, int]:
    """Checks if people can enter the lift

        This function checks if the anyone on the current floor can enter the lift.

        Arguments:
            waiting:
                (list) List of customers waiting.
            in_lift:
                (list) List of people in the lift.
            capacity:
                (int) Maximum capacity of the list (people).
            current_floor:
                (int) Current floor the list is on.

        Returns:
            waiting:
                (list) List of people waiting.
            in_lift:
                (list) Current people in the lift.
            capacity:
                (int) Capacity of the lift
            """
    if waiting != 0:
        for i in range(len(waiting)-1, -1, -1):
            if i < 0:
                break
            string = "".join(waiting[i])
            position: int = string.find(" ")
            string = string[0:position]  # Current floor of the customer
            if int(string) == current_floor:
                if len(in_lift) < int(capacity):
                    in_lift.append(waiting[i])
                    waiting.pop(i)

    return waiting, in_lift, capacity


def generate_chart(baseline_data: list, algorithm_data: list, customer_num: list):
    """Generates a visual chart

        This function takes in the chart data in the form of a list and turns it into a visual graph using matplot.

        Arguments:
            baseline_data:
                (list) List of the baseline data.
            algorithm_data:
                (list) List of data generated from my algorithm.
            customer_num:
                (list) List of customer numbers. e.g. [10, 20, 30,..., 80, 90, 100]
        Returns:
            None - this function displays a pop-out of a chart.
            """
    # Baseline line
    plt.plot(customer_num, baseline_data, label="Baseline")

    # My algorithm line
    plt.plot(customer_num, algorithm_data, label="My Algorithm")

    # Labeling chart
    plt.xlabel('Customers')
    plt.ylabel('Cost')
    plt.title('Algorithm Comparison')

    plt.legend()
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.show()
    return None


def main():
    app.run()


if __name__ == '__main__':
    main()
