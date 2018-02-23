class Executor:

    def __init__(self):
        self.func = {}

    def register(self, name, func):
        '''Register a func as a name.
        Args:
            name (str): a name to register the function as.
            func (function): a function to register under the name.
        '''
        self.func[name] = func

    def has(self, name):
        '''Returns true if the command exists; otherwise returns false.'''
        return name in self.func

    def __call__(self, name, *args, **kwargs):
        '''Execute a command registered under name and passing the additional arguments to the function.
        Args:
            name (str): the name of the function.
        '''
        if name in self.func:
            try:
                return self.func[name](*args, **kwargs)
            except ValueError as e:
                print("failure:", e)
            except EOFError:
                global running
                running = False

def poll_command():
    '''Poll an input from a user and split them into command and arguments.
    Returns:
        str: name of the command.
        list: list of string notating the arguments.
    '''
    user_input = input()
    if user_input:
        splits = user_input.split()
        command = splits[0]
        args = splits[1:]
        return command, args
    else:
        return None, None