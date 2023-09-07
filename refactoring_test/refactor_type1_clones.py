import ast;
from pathlib import Path
from refactoring_utilities import (
    parse_file_to_AST,
    parse_AST_to_file,
    find_clone_nodes_in_AST
)




def main():
    filename = Path("../test_files/calculator_type1.py")
    ast_tree = parse_file_to_AST(filename)

    clone_names : list = [["test_addition", "test_addition2"]] #list with lists of matching clones
    
    matched_clone_pairs : list = find_clone_nodes_in_AST(ast_tree, clone_names)
    
    print("Matched clone pairs:", len(matched_clone_pairs))

    ast_refactor_type1_clones(matched_clone_pairs)

    parse_AST_to_file(ast_tree, filename.stem + "_refactored.py")


def get_clone_names():
    return ["test_addition", "test_addition2"]


def ast_refactor_type1_clones(nodes):
    #type 1 clones == exact clone
    #example solution: replace implementation of clone1 with call to clone2
    for clone_pair in nodes:
        clone0 = clone_pair[0]
        clone1 = clone_pair[1]


        #ast.Call object must be wrapped in ast.Expr, 
        #otherwise it will be added onto the same line as last node.
        call_to_clone0 = ast.Expr(value=ast.Call(ast.Name(clone0.name), clone1.args.args, []))

        
        clone1.body = []
        clone1.body.append(call_to_clone0)

main()