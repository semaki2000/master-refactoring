import ast
import itertools

from .parametrize_decorator import ParametrizeDecorator
class TargetParametrizeDecorator(ParametrizeDecorator):
    """Subclass of ParametrizeDecorator which has functionality specifically for the target of the refactoring."""

    def add_value_list(self, argname:str, vals_list):
        """Takes an argname and a list of values for that argname, adding the value at each index to the clone dict at each index.
        """
        assert argname in self.argnames, "Error: an unrecognized argument name has been provided to the parametrize decorator: " + argname
        assert len(self.argvals) == len(vals_list), "Error: amount of values supplied does not correspond to the amount of clones"
        
        for ind in range(len(vals_list)):
            self.argvals[ind][argname].append(vals_list[ind])


    def remove_value_list(self, argname:str, vals_list):
        """Takes an argname a list of values for that argname, removing the value at each index from the clone dict at each index.
        Throws an error if the value doesn't exist in the dict."""
        assert argname in self.argnames, "Error: trying to remove a value from an unrecognized argument name in the parametrize decorator: " + argname
        assert len(self.argvals) == len(vals_list), "Error: amount of values supplied does not correspond to the amount of clones"
        
        for i in range(len(vals_list)):
            values = self.argvals[i][argname]
            for j in range(len(values)):
                value = values[j]
                if type(vals_list[i]) == type(value):
                    if type(value) == ast.Name:
                        if vals_list[i].id == value.id:
                            values.pop(j)
                    elif type(value) == ast.Constant:
                        if vals_list[i].value == value.value:
                            values.pop(j)
    

    def add_values_to_index(self, index, argname, values):
        """Takes an index, an argname and a list of values, adding each of these values to the list in self.argvals[index][argname].
        """
        self.argvals[index][argname].extend(values)
    
    def get_decorator(self):
        """Creates and returns a @pytest.mark.parametrize AST decorator-node 
        using info from ParametrizedArg objects.
        https://docs.pytest.org/en/7.3.x/how-to/parametrize.html 
        Doesn't yet take into account adding preexisting f_params to the f_params list,
        or combining the tuples of a_params with preexisting ones.

        Returns:
            An ast.Call node containing a pytest.mark.parametrize decorator, to be put into ast.FunctionDef.decorator_list
        """
        args = []
        args.append(ast.Constant(value=", ".join(self.argnames)))
        
        a_params = []
        for clone_dict in self.argvals:
            all_vals = []
            for key in clone_dict.keys():
                all_vals.append(clone_dict[key])
            a_params.extend(list(itertools.product(*all_vals)))

        list_tuples = []
        for tup in a_params:
            list_tuples.append(ast.Tuple(elts = list(tup)))
        args.append(ast.List(elts=list_tuples))
        
        pytest_node = ast.Call(
            func=ast.Attribute(
                value = ast.Attribute(
                    value = ast.Name(id="pytest"), 
                    attr = "mark"),
                attr = "parametrize"), 
            args = args,
            keywords = [])
                
        return pytest_node