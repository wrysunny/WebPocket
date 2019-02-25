from lib.cmd2 import Cmd
from utils.files import ROOT_PATH
from utils.module import name_convert
from pathlib import Path
from colorama import Fore, Style
from tabulate import tabulate
from importlib import import_module
from lib.Database import Database
from lib.ExploitOption import ExploitOption
from lib.exception.Module import ModuleNotUseException


class Pocket(Cmd, Database):
    colors = "Always"

    console_prompt = "{COLOR_START}WebPocket{COLOR_END}".format(COLOR_START="\033[4m", COLOR_END="\033[0m")
    console_prompt_end = " > "
    module_name = None
    module_instance = None

    def __init__(self):
        super(Pocket, self).__init__()
        Database.__init__(self)
        self.prompt = self.console_prompt + self.console_prompt_end
        self.hidden_commands.extend(['alias', 'edit', 'macro', 'py', 'pyscript', 'shell', 'shortcuts', 'load'])

    def do_list(self, args):
        modules = self.get_modules()
        self.poutput("Module List:", "\n\n", color=Fore.CYAN)
        self.poutput(tabulate(modules, headers=('module_name', 'check', 'disclosure_date', 'description')), '\n\n')

    def do_set(self, args):
        [arg, value] = args.split(" ")
        if arg == 'debug':
            self.debug = value
            return None

        if not self.module_instance:
            raise ModuleNotUseException()

        self.module_instance.options.set_option(arg, value)

    def do_use(self, module_name):
        module_file = name_convert(module_name)
        module_type = module_name.split("/")[0]

        if Path(module_file).is_file():
            self.module_name = module_name
            module_class = import_module("modules.{module_name}".format(module_name=module_name.replace("/", ".")))
            self.module_instance = module_class.Exploit()
            self.set_prompt(module_type=module_type, module_name=module_name)
        else:
            self.poutput("Module/Exploit not found.")

    def do_back(self, args):
        self.module_name = None
        self.module_instance = None
        self.prompt = self.console_prompt + self.console_prompt_end

    def do_show(self, content):
        if not self.module_instance:
            raise ModuleNotUseException()

        if content == "info":
            info = self.module_instance.get_info()
            info_table = []
            self.poutput("Module info:", "\n\n", color=Fore.CYAN)
            for item in info.keys():
                info_table.append([item + ":", info.get(item)])
            self.poutput(tabulate(info_table, colalign=("right",), tablefmt="plain"), "\n\n")

        if content == "options" or content == "info":
            options = self.module_instance.options.get_options()
            default_options_instance = ExploitOption()
            options_table = []
            for option in options:
                options_table_row = []
                for field in default_options_instance.__dict__.keys():
                    options_table_row.append(getattr(option, field))
                options_table.append(options_table_row)

            self.poutput("Module options:", "\n\n", color=Fore.CYAN)
            self.poutput(
                tabulate(
                    options_table,
                    headers=default_options_instance.__dict__.keys(),
                ),
                "\n\n"
            )

    def do_exploit(self, args):
        if not self.module_instance:
            raise ModuleNotUseException()

        exploit_result = self.module_instance.exploit()
        self.poutput("{style}[+]{style_end} {message}".format(
            style=Fore.YELLOW + Style.BRIGHT,
            style_end=Style.RESET_ALL,
            message=exploit_result,
        ))
        self.poutput("{style}[*]{style_end} module execution completed".format(
            style=Fore.BLUE + Style.BRIGHT,
            style_end=Style.RESET_ALL
        ))

    def do_db_rebuild(self, args):
        self.db_rebuild()
        self.poutput("Database rebuild done.", color=Fore.GREEN)

    def set_prompt(self, module_type, module_name):
        module_prompt = " {module_type}({color}{module_name}{color_end})".format(
            module_type=module_type,
            module_name=module_name.replace(module_type + "/", ""),
            color=Fore.RED,
            color_end=Fore.RESET
        )
        self.prompt = self.console_prompt + module_prompt + self.console_prompt_end
