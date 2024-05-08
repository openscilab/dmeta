"""DMeta main."""
import argparse
from art import tprint
from dmeta.functions import run_dmeta, dmeta_help
from dmeta.params import DMETA_VERSION


def main():
    """
    CLI main function.

    :return: None
    """
    tprint("DMeta")
    tprint("V:" + DMETA_VERSION)
    dmeta_help()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--clear',
        nargs=1,
        metavar=".docx file",
        type=str,
        help="the `clear` command clears all matadata in the given `.docx` file.",
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
        '--config',
        nargs=1,
        metavar=".json config file",
        type=str,
        help="the `config` command specifices the way metadata in the .docx files get updated."
    )
    # parse the arguments from the standard input
    args = parser.parse_args()
    run_dmeta(args)


if __name__ == "__main__":
    main()

# testcases:
# dmeta --clear "test.docx"
# dmeta --clear-all
# dmeta --update "test.docx" --config "cnf.json"
# dmeta --update-all --config "cnf.json"
