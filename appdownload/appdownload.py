"""This script checks and downloads applications' updates if any (or the full
installation package). See [[Usage description syntax]] for details about used
syntax.

This script is a [[Python Script|https://www.python.org/]] one. Thus, it must be
launched with [[python|https://docs.python.org/3/tutorial/interpreter.html#invoking-the-interpreter]]
command. (e.g. `python.exe -m appdownload`)

!!Usage

`appdownload [args...]`

!!Arguments

|^`args` |^specifies ..... |


!!Exit code

|''0'' |no error |
|''1'' |an error occurred while filtering application |
|''2'' |invalid argument. An argument of the command line is not valid (see Usage) |
|''...'' |... |


!!Environment variables

The following environment variables affect the execution of <code>{{!!title}}</code>:

|^[[VAR template]] |^{{VAR template!!contents}}  |

"""


import cots
import cots.adobeflashplayer

__author__ = "Frederic MEZOU"
__version__ = "0.3.0-dev"
__license__ = "GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007"


if __name__ == "__main__":
    print(__doc__)
    print(cots.__version__)
    print(cots.adobeflashplayer.__version__)
