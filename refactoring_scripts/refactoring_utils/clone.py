import ast
import sys
from .clone_ast_utilities import CloneASTUtilities as CAU
from .parametrized_arg import ParametrizedArg
class Clone():
    """Keeps track of a single clone, including its node in the AST, and the file it came from."""

    def __init__(self, ast_node, parent_node, lineno) -> None:
        self.parametrized_args = [] #list of parametrizedArg object
        self.is_fixture : bool = False
        self.unknown_decorator = False
        self.ast_node = ast_node
        self.parent_node = parent_node
        self.lineno = lineno
        self.funcname = ast_node.name
        
        self.parse_decorator_list()
    
    def parse_decorator_list(self):
        """'Parses' decorator list of this function to see if function is a fixture or is parameterized.
        Sets value of self.is_fixture, a boolean telling whether this clone is a fixture (fixtures can be disregarded).
        Also sets value of self.parameterized_values:
            if no pytest.mark.parametrization decorator exists -> None
            if pytest.mark.parametrization decorator exists, a tuple of [0] constants (names of parameters) and [1] tuples of values
        """
        

        for decorator in self.ast_node.decorator_list:
            
            if CAU.is_parametrize_decorator(decorator):
                #get contents of p.m.parametrize as actual literals
                #assuming param_names is string
                param_names = decorator.args[0].value

                # argvalues can be as name, or a list of either tuples or single elements.
                if type(decorator.args[1]) == ast.Name: 
                    print("Error: refactoring program does not currently handle names as args to .parametrize decorator")
                    sys.exit()
                else:
                    param_names = param_names.split(",")
                    self.parametrized_args = []
                    for name in param_names:
                        self.parametrized_args.append(ParametrizedArg(argname=name))
                    for args in decorator.args[1].elts:
                        if type(args) == ast.Tuple:
                            [self.parametrized_args[args.index(x)].add_value(x) for x in args]
                        elif type(args) == ast.Constant:        
                            #should only be one ParametrizedArg object
                            self.parametrized_args[0].add_value(args)
 

                self.ast_node.decorator_list.remove(decorator) #remove decorator for parametrize (added again later)
                return


            elif CAU.is_fixture_decorator(decorator):
                self.is_fixture = True
            
            else:
                print("unknown decorator")
                print(ast.unparse(decorator))
                self.unknown_decorator = True                

    def get_ast_node(self):
        return self.ast_node
    
    def detach(self):
        """Detach this clone's node from the AST."""
        
        self.parent_node.body.remove(self.ast_node)