from abc import ABC, abstractmethod
from typing import AbstractSet, Optional, Sequence

from clingo.ast import AST, ASTType, parse_files
from clingo.symbol import Symbol
from instantiator import Instantiator
from rule import Rule
from tarjan import Graph
from util import body_symbolic_atoms, head_symbolic_atoms


def sccs_to_str(sccs: list[list[AST]]) -> str:
    """
    Convert a list of strongly connected components to a string.
    """
    return ("\n" + "-" * 60 + "\n").join(
        "\n".join(str(rule) for rule in scc) for scc in sccs
    )


class Grounder(ABC):
    def __init__(self, instantiator: Optional[Instantiator] = None) -> None:
        self._program: list[AST] = []
        if not instantiator:
            instantiator = Instantiator()
        self.instantiator = instantiator

    def __append_rule_to_program_ast(self, stm: AST) -> None:
        if stm.ast_type == ASTType.Rule:
            self._program.append(stm)

    def add_files(self, files: Sequence[str]):
        parse_files(files, self.__append_rule_to_program_ast)

    def ground(self) -> list[Rule]:
        return self._grounding_algorithm(self._program)[0]

    @abstractmethod
    def _grounding_algorithm(
        self, program: list[AST], atoms: AbstractSet[Symbol] = frozenset()
    ) -> tuple[list[Rule], set[Symbol]]:
        pass


class BottomUpGrounder(Grounder):
    def _grounding_algorithm(
        self, program: list[AST], atoms: AbstractSet[Symbol] = frozenset()
    ) -> tuple[list[Rule], set[Symbol]]:
        """
        Grounds a program bottom up.
        """
        # YOUR CODE HERE
        grounded_rules = []
        head_atoms = set(atoms) #Start with the initial set atoms

        while True:
            new_grounded_rules = []
            new_head_atoms = set()

            for rule in program:
               #Ground the rule according to current head_atoms
                grounded = self.instantiator.ground_rule(rule, head_atoms)

                for gr in grounded:
                    
                    if gr not in grounded_rules:        #Avoid the duplicates problem we encountered early in the development
                        new_grounded_rules.append(gr)
                       
                        new_head_atoms.update(gr.head)    #Add new head_atoms


            #Next 3 lines add newly grounded atoms and update the set of head_atoms
            grounded_rules.extend(new_grounded_rules)
            new_atoms_count = len(new_head_atoms- head_atoms)
            head_atoms.update(new_head_atoms)

            #Break the loop if no new head atoms were generated
            if new_atoms_count==0:
                break

        
        return grounded_rules, head_atoms
        raise NotImplementedError


def depends(rule2: AST, rule1: AST) -> bool:
    """
    Check if rule2 depends on rule1. This is the case if the there is an atom in the body of rule2
    with the same name and number of arguments as an atom in the head of rule1.
    """
    assert rule2.ast_type == ASTType.Rule
    assert rule1.ast_type == ASTType.Rule
    # YOUR CODE HERE
    
    body_atoms= body_symbolic_atoms(rule2) 
    head_atoms= head_symbolic_atoms(rule1)
    #compare atoms from the body of rule2 with atoms from the head of rule1
    return any(atom.name == head_atom.name and 
               len(atom.arguments) == len(head_atom.arguments) for atom in body_atoms for head_atom in head_atoms)
    #raise NotImplementedError


def dependency_graph(program: Sequence[AST]) -> tuple[Graph[AST], list[AST]]:
    """
    Compute the dependency graph of a program using the depends function defined above.
    It returs such a graph and a list of rules that have no dependencies with any other rules.
    """
    # YOUR CODE HERE
    graph = Graph[AST]() #Start with an empty graph
    all_rules= set(program) #This is a set of all rules in the program
    dependent_rules = set() #Set of rules with dependencies
    
    #Iterate through each pair of rules to check/identify dependencies    
    for rule in program:
        for other_rule in program:
            if depends(rule, other_rule):
                graph.add_edge(other_rule, rule)
                dependent_rules.update({rule, other_rule}) #solved the issue of missing a rule
     #Independent rules are the rules that are not present in the dependent_rules set           
    independent_rules = list(all_rules - dependent_rules)
               
        
    return graph, independent_rules
    
    #raise NotImplementedError


def strongly_connected_components(program: Sequence[AST]) -> list[list[AST]]:
    """
    Compute the strongly connected components of a program. The strongly connected components are
    returned in topological order.
    """
    # YOUR CODE HERE
    #Compute the dependency graph
    graph, independent_rules = dependency_graph(program)
    #Get the strongly connected components
    sccs =graph.sccs()
    #Ensuring that independent rules are considered as strongly connected components
    for rule in independent_rules:
        sccs.append([rule])
    
    #Return a list of strongly connected components     
    return sccs

    #raise NotImplementedError


class GrounderWithDependencies(Grounder):
    def __init__(self, instantiator: Optional[Instantiator] = None) -> None:
        super().__init__(instantiator)
        self.bootom_up_grounder = BottomUpGrounder(self.instantiator)

    def _grounding_algorithm(
        self, program: list[AST], atoms: AbstractSet[Symbol] = frozenset()
    ) -> tuple[list[Rule], set[Symbol]]:
        """
        Ground a program bottom up using the dependency graph.
        """
        # YOUR CODE HERE
        # Calculate the dependency graph and independent rules and Initialize the set of head atoms
        graph, independent_rules = dependency_graph(program)
        head_atoms = set(atoms)
        grounded_rules = []

        #Get the Strongly connected components 
        sccs = graph.sccs()

        # Handle independent rules
        if independent_rules:
            # Ground independent the independent rules
            for rule in independent_rules:
                grounded_rule, new_head_atoms = self.bootom_up_grounder._grounding_algorithm([rule], head_atoms)
                grounded_rules.extend(grounded_rule)
                head_atoms.update(new_head_atoms)

        # Iterate over each Strongly connected components
        for scc in sccs:
            # Ground all the rules inside each Strongly connected components
            scc_grounded_rules, new_head_atoms = self.bootom_up_grounder._grounding_algorithm(scc, head_atoms)
            
            # Get the grounded rules and update the set of head_atoms
            grounded_rules.extend(scc_grounded_rules)
            head_atoms.update(new_head_atoms)

        # Return the list of grounded rules and the final set of head_atoms
        return grounded_rules, head_atoms
        #raise NotImplementedError
