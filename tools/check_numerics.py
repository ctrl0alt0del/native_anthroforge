"""Verify optional compiled dependencies actually import, not just metadata."""

from importlib import import_module

PACKAGES = ("numpy", "scipy", "skimage", "pyinstantmeshes", "pytetwild")


def main() -> None:
    for name in PACKAGES:
        import_module(name)
        print(f"{name}: imported")


if __name__ == "__main__":
    main()
