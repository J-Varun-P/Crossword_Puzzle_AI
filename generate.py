import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.domains:
            temp = set()
            for x in self.domains[v]:
                if len(x) != v.length:
                    temp.add(x)
            for y in temp:
                if y in self.domains[v]:
                    self.domains[v].remove(y)
        #raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        temp1 = self.crossword.overlaps[x,y]
        temp2 = set()
        for value1 in self.domains[x]:
            check = 0
            for value2 in self.domains[y]:
                if value2[temp1[1]] == value1[temp1[0]]:
                    check = 1
            if check == 0:
                revised = True
                temp2.add(value1)
        for value1 in temp2:
            self.domains[x].remove(value1)
        return revised
        #raise NotImplementedError

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            queue = []
            for x in self.domains:
                temp = self.crossword.neighbors(x)
                for y in temp:
                    if (x,y) not in queue:
                        queue.append((x,y))
        else:
            queue = arcs
        while len(queue) != 0:
            (x1,y1) = queue[0]
            queue = queue[1:]
            if self.revise(x1, y1):
                if len(self.domains[x1]) == 0:
                    return False
                temp1 = self.crossword.neighbors(x1)
                temp1.remove(y1)
                for z in temp1:
                    queue.append((z,x1))
        return True
        #raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        check = True
        for variable in self.crossword.variables:
            if variable not in assignment:
                check = False
                return check
        return check
        #raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for variable in assignment:
            if variable.length != len(assignment[variable]):
                return False
        temp = []
        for variable in assignment:
            if assignment[variable] in temp:
                return False
            temp.append(assignment[variable])
        for variable1 in assignment:
            if len(assignment) != 0:
                temp2 = self.crossword.neighbors(variable1)
                for variable2 in temp2:
                    if variable2 in assignment:
                        temp3 = self.crossword.overlaps[variable1,variable2]
                        if temp3 is not None:
                            if assignment[variable1][temp3[0]] != assignment[variable2][temp3[1]]:
                                return False
        return True
        #raise NotImplementedError

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        """
        temp = []
        for x in self.domains[var]:
            temp.append(x)
        return temp
        """
        temp = []
        for x in self.domains[var]:
            temp.append(x)
        temp2 = {}
        for x in temp:
            z = 0
            temp3 = self.crossword.neighbors(var)
            for y in temp3:
                meeting_point = self.crossword.overlaps[var,y]
                for value in self.domains[y]:
                    if value[meeting_point[1]] != x[meeting_point[0]]:
                        z += 1
            temp2[x] = z
        temp.sort(key=lambda x: temp2[x])
        return temp
        #raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        temp = []
        for x in self.crossword.variables:
            if x not in assignment:
                temp.append(x)
        temp.sort(key=lambda x: len(self.domains[x]))
        if len(temp) > 1:
            if len(self.domains[temp[0]]) < len(self.domains[temp[1]]):
                return temp[0]
            else:
                temp2 = []
                for x in temp:
                    if len(self.domains[x]) == len(self.domains[temp[0]]):
                        temp2.append(x)
                temp2.sort(key=lambda x: len(self.crossword.neighbors(x)), reverse=True)
                return temp2[0]
        else:
            return temp[0]
        #raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        check = True
        temp1 = []
        for variable in self.crossword.variables:
            temp1.append(variable)
            if variable not in assignment:
                check = False
        if check == True:
            return assignment
        """
        for variable in temp1:
            if variable not in assignment:
                temp2 = variable
                break
        """
        temp2 = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(temp2, assignment):
            assignment[temp2] = value
            temp3 = self.consistent(assignment)
            if temp3:
                result = self.backtrack(assignment)
                if result:
                    return result
                else:
                    if temp2 in assignment:
                        assignment.pop(temp2)
            if temp2 in assignment:
                assignment.pop(temp2)
        return None
        #raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
