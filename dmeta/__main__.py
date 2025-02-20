"""DMeta main."""
import argparse
from art import tprint
from dmeta.functions import run_dmeta
from dmeta.params import DMETA_VERSION, CLI_MORE_INFO, OVERVIEW


def main():
    """
    CLI main function.

    :return: None
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--clear',
        nargs=1,
        metavar=".docx file",
        type=str,
        help="the `clear` command clears all metadata in the given `.docx` file.",
    )
    parser.add_argument(
        '--clear-all',
        action="store_true",
        default=False,
        help='the `clear-all` command clears all metadata in any `.docx` file in the current directory.',
    )
    parser.add_argument(
        '--update',
        nargs=1,
        metavar=".docx file",
        type=str,
        help="the `update` command updates the given .docx file's metadata according to the given .json config file."
    )
    parser.add_argument(
        '--update-all',
        action="store_true",
        default=False,
        help='the `update-all` command updates all metadata in any `.docx` file in the current directory according to the given .json config file.',
    )
    parser.add_argument(
        '--inplace',
        action="store_true",
        default=False,
        help="the `in_place` flag applies the changes directly to the original file."
    )
    parser.add_argument(
        '--config',
        nargs=1,
        metavar=".json config file",
        type=str,
        help="the `config` command specifies the way metadata in the .docx files get updated."
    )
    parser.add_argument(
        '--info',
        action="store_true",
        default=False,
        help="the `info` flag gives general information about DMeta library."
    )
    parser.add_argument(
        '--verbose',
        action="store_true",
        default=False,
        help="the `verbose` flag enables detailed output for debugging or information purposes."
    )
    parser.add_argument('--version', help="version", action='store_true', default=False)
    parser.add_argument('-v', help="version", action='store_true', default=False)
    args = parser.parse_known_args()[0]
    if args.version or args.v:
        print(DMETA_VERSION)
        return
    if args.info:
        tprint("DMeta")
        tprint("V:" + DMETA_VERSION)
        print(OVERVIEW)
        print(CLI_MORE_INFO)
        return
    run_dmeta(args)


if __name__ == "__main__":
    main()
