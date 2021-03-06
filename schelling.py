#Egemen Pamukcu
"""
CS121: Schelling Model of Housing Segregation

  Program for simulating a variant of Schelling's model of
  housing segregation.  This program takes six parameters:

    filename -- name of a file containing a sample city grid

    R - The radius of the neighborhood: home at Location (i, j) is in
        the neighborhood of the home at Location (k,l)
        if k-R <= i <= k+R and l-R <= j <= l+R

    similarity_satisfaction_range (lower bound and upper bound) -
         acceptable range for ratio of the number of
         homes of a similar color to the number
         of occupied homes in a neighborhood.

   patience - number of satisfactory homes that must be visited before choosing
              the last one visited.

   max_steps - the maximum number of passes to make over the city
               during a simulation.

  Sample: python3 schelling.py --grid_file=tests/a20-sample-writeup.txt --r=1
         --sim_lb=0.40 --sim_ub=0.7 --patience=3 --max_steps=1
  The sample command is shown on two lines, but should be entered on
  a single line in the linux command-line
"""

import click
import utility

def color(grid, location):
    '''
    Returns the status of a homeowner/house at the given location of the 
        given city.

    Inputs:
        grid (list of lists of strings): the grid
        location (tuple of integers): a position in the grid specifying a row 
            and a column
    Returns: (string) 'M' and 'B' for maroon and blue households respectively. 
        'F' for houses for sale. 
    '''
    owner = grid[location[0]][location[1]]
    return owner


def neighbor_list(grid, location, R):
    '''
    Create and return a list of houses in the neighborhood.

    Inputs:
        grid (list of lists of strings): the grid
        location (tuple of integers): a position in the grid specifying 
            a row and a column
        R (int): neighborhood parameter

    Returns: (list of tuples of integers) The locations of houses in the 
        neighborhood.
    '''
    n_list = []
    
    for row, lines in enumerate(grid):
        for column, house in enumerate(lines):
            if (0 <= abs(location[0] - row) + abs(location[1] - column) <= R):
                n_list.append((row, column))
            
    return n_list


def neighbor_list_col(grid, location, R):
    '''
    Create and returns a list of the statuses of houses in given neighborhood

    Inputs:
        grid (list of lists of strings): the grid
        location (tuple of integers): a position in the grid specifying 
            a rown and a column
        R (int): neighborhood parameter

    Returns: (list of strings) The status of houses in the neighborhood.
    '''
    neighbors = neighbor_list(grid, location, R)
    neighbor_colors = []
    
    for col in neighbors:
        neighbor_colors.append(color(grid, col))
    
    return neighbor_colors


def calculate_similarity(grid, location, R):
    '''
    Calculate similarity score based on status of the houses
    in the neighborhood.

    Inputs:
        grid (list of lists of strings): the grid
        location (tuple of integers): a position in the grid specifying 
            a rown and a column
        R (int): neighborhood parameter
    
    Returns: (float between 0 and 1) similarity score of a given house.
    '''
    neighbor_colors = neighbor_list_col(grid,location,R)
    num_same_color = 0
    num_all_occupied = 0
    for col in neighbor_colors: 
        if col == color(grid,location) and col != 'F':
            num_same_color += 1
            num_all_occupied += 1
        elif col != color(grid,location) and col != 'F':
            num_all_occupied +=1
            
    similarity = num_same_color / num_all_occupied
    
    return similarity

def is_satisfied(grid, R, location, sim_sat_range):
    '''
    Determine whether or not the homeowner at a specific location is
    satisfied using an R-neighborhood centered around the location.
    That is, does their similarity score fall with the specified
    range (inclusive)

    Inputs:
        grid: the grid
        R (int): neighborhood parameter
        location (int, int): a grid location
        sim_sat_range (float, float): lower bound and upper bound on
          the range (inclusive) for when the homeowner is satisfied
          with his similarity score.
    Returns: bool
    '''
    assert color(grid, location) != 'F'
    
    lb = sim_sat_range[0]
    ub = sim_sat_range[1]
    satisfied = False
    
    if lb <= calculate_similarity(grid, location, R) <= ub:
        satisfied = True

    return satisfied


def swap_house(grid, location1, location2):
    '''
    Swaps the status of two houses by modifying the given grid.
    
    Inputs:
        grid: the grid
        location1 (int, int): location of the first house to be swapped
        location2 (int, int): location of the second house to be swapped
    '''
    grid[location1[0]][location1[1]], grid[location2[0]][location2[1]] =\
    grid[location2[0]][location2[1]], grid[location1[0]][location1[1]]


def move_homeowner(grid, R, location, sim_sat_range, patience, homes_for_sale):
    '''
    Moves the single homeowner in the provided location to its next home
    based on patience, similarity score and satifaction range. 

    Inputs:
        grid (list of lists of strings): the grid
        R (int): neighborhood parameter
        sim_sat_range (float, float): lower bound and upper bound on
          the range (inclusive) for when the homeowner is satisfied
          with his similarity score.
        patience (int): number of satisfactory houses a homeowner will tour
            in order to move
        homes_for_sale (list of tuples): a list of locations with homes for sale

    Returns:
        move (int): 0 if no move is done, 1 if a move is done.
    '''
    p = patience
    move = 0
    
    for i, home in enumerate(homes_for_sale):
        swap_house(grid, home, location) 
        if is_satisfied(grid, R, home, sim_sat_range) == True:
            if p > 1: 
                p = p - 1
                swap_house(grid, home, location) 
            else:
                del homes_for_sale[i]
                homes_for_sale.insert(0,location)
                move += 1
                break
        else: 
            swap_house(grid, home, location)

    return move


def sim_wave(grid, R, sim_sat_range, patience, homes_for_sale, wave_color):
    '''
    Simulate a wave.

    Inputs:
        grid (list of lists of strings): the grid
        R (int): neighborhood parameter
        sim_sat_range (float, float): lower bound and upper bound on
          the range (inclusive) for when the homeowner is satisfied
          with his similarity score.
        patience (int): number of satisfactory houses a homeowner will tour
            in order to move
        homes_for_sale (list of tuples): a list of locations with homes for sale
        wave_color (str): determines if a maroon wave or a blue wave is to be
            simulated

    Returns: 
        total_wave_moves (int): total number of moves done during wave        
    '''
    wave_move_list = []
    for row, lines in enumerate(grid):
        for column, homes in enumerate(lines):
            if homes == wave_color and is_satisfied(grid, R, (row, column), sim_sat_range) == False:
                move = move_homeowner(grid, R, (row, column), sim_sat_range, patience, homes_for_sale)
                wave_move_list.append(move)
    
    total_wave_moves = sum(wave_move_list)
    
    return total_wave_moves


def sim_step(grid, R, sim_sat_range, patience, homes_for_sale):
    '''
    Simulate a step, that is a maroon wave followed by a blue wave. 

    Inputs:
        grid (list of lists of strings): the grid
        R (int): neighborhood parameter
        sim_sat_range (float, float): lower bound and upper bound on
          the range (inclusive) for when the homeowner is satisfied
          with his similarity score.
        patience (int): number of satisfactory houses a homeowner will tour
            in order to move
        homes_for_sale (list of tuples): a list of locations with homes for sale

    Returns: 
        grid (list of lists of strings): the modified grid
        total_step_moves (int): total number of moves done during the step
        homes_for_sale (list of tuples): an updated list of locations with homes for sale  
    '''
    steps = ['M', 'B']
    step_move_list = []

    for wave_col in steps:
        total_wave_moves = sim_wave(grid, R, sim_sat_range, patience, homes_for_sale, wave_col)
        step_move_list.append(total_wave_moves)
        
    total_step_moves = sum(step_move_list)
    
    return total_step_moves


def do_simulation(grid, R, sim_sat_range, patience, max_steps, homes_for_sale):
    '''
    Do a full simulation.

    Inputs:
        grid (list of lists of strings): the grid
        R (int): neighborhood parameter
        sim_sat_range (float, float): lower bound and upper bound on
          the range (inclusive) for when the homeowner is satisfied
          with his similarity score.
        patience (int): number of satisfactory houses a homeowner will tour
            in order to move
        max_steps (int): maximum number of steps to do
        homes_for_sale (list of tuples): a list of locations with homes for sale

    Returns: (int) The number of relocations completed.
    '''
    sim_move_list = []
    for i in range(max_steps):
        total_step_moves = sim_step(grid, R, sim_sat_range, patience, homes_for_sale)
        sim_move_list.append(total_step_moves)
        if sim_move_list[-1] == 0:
            break
            
    total_sim_moves = sum(sim_move_list)
    return total_sim_moves


@click.command(name="schelling")
@click.option('--grid_file', type=click.Path(exists=True))
@click.option('--r', type=int, default=1,
              help="neighborhood radius")
@click.option('--sim_lb', type=float, default=0.40,
              help="Lower bound of similarity range")
@click.option('--sim_ub', type=float, default=0.70,
              help="Upper bound of similarity range")
@click.option('--patience', type=int, default=1, help="patience level")
@click.option('--max_steps', type=int, default=1)
def cmd(grid_file, r, sim_lb, sim_ub, patience, max_steps):
    '''
    Put it all together: do the simulation and process the results.
    '''

    if grid_file is None:
        print("No parameters specified...just loading the code")
        return

    grid = utility.read_grid(grid_file)
    for_sale = utility.find_homes_for_sale(grid)
    sim_sat_range = (sim_lb, sim_ub)


    if len(grid) < 20:
        print("Initial state of city:")
        for row in grid:
            print(row)
        print()

    num_relocations = do_simulation(grid, r, sim_sat_range, patience,
                                    max_steps, for_sale)

    if len(grid) < 20:
        print("Final state of the city:")
        for row in grid:
            print(row)
        print()

    print("Total number of relocations done: " + str(num_relocations))

if __name__ == "__main__":
    cmd() # pylint: disable=no-value-for-parameter
