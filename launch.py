"""Distribution entry point: desktop by default, numerical CLI with --cli."""

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        from anthroforge.cli import main as cli_main

        return cli_main(sys.argv[2:])
    from anthroforge.desktop.app import main as desktop_main

    return desktop_main()


if __name__ == "__main__":
    raise SystemExit(main())
