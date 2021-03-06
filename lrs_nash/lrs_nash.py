"""
A library to use the lrs Nash library. This is currently done in a pretty poor way.
"""
from __future__ import division
from os import remove
from subprocess import Popen, PIPE, call
import random
import string


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """
    A function to generate random file names for physical files needed to communicate with lrs.
    """
    return ''.join(random.choice(chars) for x in range(size))


def multiple_equilibria_clean(l):
    if len(l) > 2:
        r = []
        for e in l[:-1]:
            r.append([e, l[-1]])
        return r
    return [l]


class Normal_Form_Equilibria:
    """
    A class for an equilibria of a normal form game
    """
    def __init__(self, lrs_output):
        self.row_strategy_distribution = lrs_output[1][1:-1]
        self.col_strategy_distribution = lrs_output[0][1:-1]
        self.row_utility = lrs_output[0][-1]
        self.col_utility = lrs_output[1][-1]


class Normal_Form_Game:
    """
    A class for a normal form game
    """
    def __init__(self, row_matrix, col_matrix):
        self.row_size = len(row_matrix)
        self.col_size = len(row_matrix[0])
        self.row_matrix = row_matrix
        self.col_matrix = col_matrix

    def solve(self):
        """
        Method that write physical files so that lrs can be used to solve game.
        """
        # Write game file
        file1 = id_generator(6)
        game = open(file1, "w")
        game.write("%s %s\n" % (self.row_size, self.col_size))
        for i in self.row_matrix:
            game.write("\n")
            game.write(" ".join([str(e) for e in i]))
        game.write("\n")
        for j in self.col_matrix:
            game.write("\n")
            game.write(" ".join([str(e) for e in j]))
        game.close()

        # Write H representations for each player (really should automate this)
        file2 = id_generator(6)
        file3 = id_generator(6)
        call(["setupnash", file1, file2, file3], stdout=PIPE)
        # Solve game using lrs:
        process = Popen(["nash", file2, file3], stdout=PIPE)
        # Save output
        lrs_output = [row for row in process.stdout]
        # Delete lrs files, need to do this without writing hard files
        for f in [file1, file2, file3]:
            remove(f)
        # Find number of equilibria
        self.number_of_equilibria = eval([row for row in lrs_output if "*Number of equilibria found:" in row][0].split()[-1])
        # This obtains pairs of equilibria as output by lrs. Can be improved.
        lrs_output = [[eval(e) for e in row[:-2].split('  ')] for row in lrs_output[7:-7] if row != '\n']
        # Create empty list for equilibria
        self.equilibria = []
        while lrs_output:
            # Go through elements of output of lrs
            if len(lrs_output) > 1:
                # If there is an element left
                i = [row[0] for row in lrs_output].index(1)
                temp = []  # A temp list that will hold a portion of the lrs output
                for e in lrs_output[: i + 1]:
                    temp.append(lrs_output.pop(0))
                for e in multiple_equilibria_clean(temp):
                    # Create the required Normal form equilibria objects
                    self.equilibria.append(Normal_Form_Equilibria(e))


if __name__ == '__main__':
    a = Normal_Form_Game([[3, 3], [2, 5], [0, 6]], [[3, 2], [2, 6], [3, 1]])
    a.solve()
    for e in a.equilibria:
        print e
        print "\tRow player plays:", e.row_strategy_distribution, "with utility:", e.row_utility
        print "\tCol player plays:", e.col_strategy_distribution, "with utility:", e.col_utility
