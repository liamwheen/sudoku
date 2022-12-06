#!/usr/bin/env python3
import numpy as np

def draw_grid(grid,n):
    x = [(' {}'*n+(' |'+' {}'*n)*(n-1)).format(*grid[r,:]).replace('0',' ') for r in range(n**2)]
    [x.insert(i,' '+'- '*(n**2+(n-1))) for i in list(range(n,n**2,n))[::-1]]
    return '\n'.join(x)

def check_section(sec,n):
    if sum(sec)!=sum(range(n**2+1)) or len(np.unique(sec))!=n**2:
        return False
    return True

def generate_squares(grid,n):
    return [grid[i*n:(i+1)*n,j*n:(j+1)*n] for i in range(n) for j in range(n)]

def check_grid(grid):
    # Check subgrids
    for square in generate_squares(grid,n):
        if not check_section(square.flatten(),n):
            return False
    # Check rows 
    for row in grid:
        if not check_section(row,n):
            return False
    # Check cols
    for col in grid.T:
        if not check_section(col,n):
            return False
    return True

def generate_solved_sudoku(n):
    rows = [np.random.choice(np.arange(1,n**2+1),n**2,False).tolist()]
    for i in range(1,n**2):
        if i%n==0:
            rows+=[np.roll(rows[i-1],1).tolist()]
        else:
            rows+=[np.roll(rows[i-1],n).tolist()]
    grid = np.array(rows).squeeze()
    # Swap two random columns within col blocks
    for block in range(0,n**2,n):
        i,j = np.random.choice(list(range(block,block+n)),2,False)
        grid[:,[i,j]] = grid[:,[j,i]]
    return grid

def solve_sudoku_random(grid,n,original_grid=None):
    'Naive approach that randomly assigns values to empty cells until success'
    if original_grid is None:original_grid = grid.copy()
    empty = np.argwhere(grid==0)
    if len(empty)==0:
        if check_grid(grid):
            return grid
        else:
            return solve_sudoku_random(original_grid,n)
    rows,cols = empty.T
    for row in set(rows):
        nums_left = set(range(1,n**2+1))-set(grid[row,:])
        choices = np.random.choice(list(nums_left),len(nums_left),False)
        temp_grid = grid.copy()
        temp_grid[row,cols[empty[:,0]==row]] = choices
        return solve_sudoku_random(temp_grid,n,original_grid)

def generate_opts(grid,i,j,n):
    'Used for search function to avoid trying invalid values'
    in_row = set(grid[i,:])
    in_col = set(grid[:,j])
    in_square = set(grid[n*(i//n):n*(i//n+1),n*(j//n):n*(j//n+1)].flatten())
    return list(set(range(1,n**2+1))-in_row-in_col-in_square)

def solve_sudoku_search(grid,n):
    'More efficient approach that recursively searches the valid options'
    empty = np.argwhere(grid==0)
    opts = {(row,col):generate_opts(grid,row,col,n) for row,col in empty}
    # First assign known values, then sweep over possible pairs etc.
    coords = [coord for coord in opts.keys() if len(opts[coord])==1]#num_poss]
    for i,j in coords:
        grid[i,j]=opts[(i,j)][0]
    if check_grid(grid):
        return grid
    return solve_sudoku_search(grid,n)

if __name__ == '__main__':
    import time
    import sys
    if sys.argv[-1][0] == '4':
        # Trial 4x4 example that can be solved with either method
        grid = np.array([[0,0,3,2],
                         [3,2,0,4],
                         [0,3,2,0],
                         [0,1,4,0]])
    else:
        # Select one of 10 puzzles with known solutions
        eg_puz = np.random.randint(1,10,1)[0]
        grid = np.load(f'puzzles/q{eg_puz}.npy')
    n = int(np.sqrt(grid.shape[0])) # sqrt of number of squares in a line
    print('Input:')
    print('~'*2*(n**2+n-1))
    print(draw_grid(grid,n))
    start = time.time()
    sol = solve_sudoku_search(grid,n)
    print(f'\nSolution: ({time.time()-start:.3} s)')
    print('~'*2*(n**2+n-1))

    try:
        known_sol = np.load(f'puzzles/a{eg_puz}.npy')
    except(NameError):
        print(draw_grid(sol,n))
        quit()

    if not (sol-known_sol).any():
        print(draw_grid(sol,n))
        print('\nMatches known solution')
    else:
        print('Differs from known solution - check result')
        sol[(sol-known_sol)!=0] = '0'
        print(draw_grid(sol,n))
 
