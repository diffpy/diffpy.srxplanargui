import argparse

from diffpy.srxplanargui.version import __version__  # noqa


def main():
    parser = argparse.ArgumentParser(
        prog="diffpy.srxplanargui",
        description=(
            "xPDFsuite, a software for PDF transformation"
            " and visualization.\n\n For more information, visit: "
            "https://github.com/diffpy/diffpy.srxplanargui/"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the program's version number and exit",
    )

    args = parser.parse_args()

    if args.version:
        print(f"diffpy.srxplanargui {__version__}")
    else:
        # Default behavior when no arguments are given
        parser.print_help()


if __name__ == "__main__":
    main()
