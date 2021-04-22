    #--------------------------------------------------------------------------

class UnwrapList(object):
    value : object
    position : int = 0
    def __len__(self):
        return 1
    def __eq__(self, other):
        if not isinstance(other, Unwrap):
            return False
        return self.value == other.value
    def __getitem__(self, key):
        if not isinstance(key, int):
            raise TypeError(f"UnwrapList requires integer keys, "
                            f"key '{key}' is not an integer.")
        if key > 0:
            raise KeyError(f"UnwrapList, key '{key}' out of range.")
        return self.value
    def __setitem__(self, key, value):
        raise TypeError("UnwrapList does not support assignment.")
        
    #--------------------------------------------------------------------------

# Unnecessary, as visit now defaults to oneself.

    # Note: Will simplify to plain string if no encapsulating concept has
    #       a visit method, either oneself or specific.
    _self = ( ' docopt '
              ' program '
              ' usage_pattern '
              ' '
            )
        # for rule_name in self._self.split() :
        #     setattr(self, f"visit_{rule_name}", self.oneself)

    def oneself(self, node, children):
        if len(children) > 0:
            out = NonTerminal(node.rule, children)
            which = 'non-term'
        else:
            out = Terminal(node.rule, 0, node.value)
            which = 'terminal'
        return out

    #--------------------------------------------------------------------------

    def visit_argument(self, node, children):
        i = node._indent
        print(f"{i}: visit_argument")
        print(f"{i}  - rule_name  = {node.rule_name}")
        extra =   '                 '
        print(f"{i}  - node       = {str(type(node))}\n"
              f"{node.indent(node.tree_str(), extra)}")
        print(f"{i}  - value      = {node.value}")
        print(f"{i}  - children[0]  => {str(type(children[0]))} : {children[0]}")
        print(f"{i}    < unwrapped >")
        # print('')
        return Unwrap(children[0])

    #--------------------------------------------------------------------------

    # make BAR directly searchable within the choice list
    def visit_BAR(self, node, children):
        return self._BAR

    # eliminate fake choice
    def visit_choice(self, node, children):
        print(f": choice :\n{children}\n= = = =\n")
        if self._BAR in children:
            return node
        print(f": choice : elide fake choice")
        marker = Terminal(StrMatch('.','choice:fake'), 0, '.')
        if False : # True :
            return marker
        if ( isinstance(children, list) and len(children) == 1 and
             isinstance(children[0], NonTerminal) ) :
            node = children[0]
            children = node
            # return NonTerminal(Sequence(
        return children

    #==========================================================================

    # *** Unnecessary 
    
    _strip = ( ' docopt usage usage_line usage_entry '
               ' other_sections other '
               ' option short long long_with_arg long_with_eq_arg '
               # ' expression '
               ' argument '
               ' operand_line '
               ' option_line  '
               # it does not matter what kind of operand it is
               # ' operand_all_caps operand_angled '
             )

    # Do not strip BAR, it's prescense is necessary for choice
    _empty = 'blankline newline EOF COMMA LPAREN RPAREN LBRACKET RBRACKET OR'

    def OLD___init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self._strip = set(self._strip.split())
        # self._empty = set(self._empty.split())
        # for rule_name in self._strip.split() :
        #     setattr(self, f"visit_{rule_name}", self.strip)
        # for rule_name in self._empty.split() :
        #     setattr(self, f"visit_{rule_name}", self.empty)
        for rule_name in self._self.split() :
            setattr(self, f"visit_{rule_name}", self.oneself)

    def _visit(self, node):
        responses = []
        if isinstance(node, NonTerminal):
            responses = []
            for child in node : # NonTerminal IS the list
                response = self.visit(child)
                if response:
                    responses.append(response)
        if node.rule_name in self._empty :
            return None
        if node.rule_name in self._strip :
            return self.strip(node, responses)
        method = f"visit_{node.rule_name}"
        if hasattr(self, method):
            return eval(f"self.{method}(node, responses)")
        if isinstance(node, Terminal):
            return node
        return NonTerminal(node.rule, responses)
    

    def _visit_description(self, node, children):
        return Terminal(node.rule, '\n'.join(children))

    def _visit_line(self, node, children):
        return ' '.join(children)

    def _visit_word(self, node, children):
        return node.value

    def _visit_trailing (self, node, children):
        return Terminal(node.rule, '\n'.join(children))

    def _visit_trailing_line (self, node, children):
        return ' '.join(children)

    def _visit_fragment(self, node, children):
        return ' '.join(children)

    #--------------------------------------------------------------------------

    def _visit_operand_intro(self, node, children):
        return Terminal(node.rule, ' '.join(children))

    def _visit_operand_help(self, node, children):
        while isinstance(children[-1], list):
            tmp = children[-1]
            children = children[:-1]
            children.extend(tmp)
        return Terminal(node.rule, ' '.join(children))

    #--------------------------------------------------------------------------

    def _visit_options_intro(self, node, children):
        return Terminal(node.rule, ' '.join(children))

    def _visit_option_help(self, node, children):
        while isinstance(children[-1], list):
            tmp = children[-1]
            children = children[:-1]
            children.extend(tmp)
        return Terminal(node.rule, ' '.join(children))

