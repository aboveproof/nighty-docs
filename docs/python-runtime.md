# Python 3.14 runtime

Nighty 2.6.2 runs NightyScript on Python 3.14. Write and test scripts against
Python 3.14 even if an older Python version is installed separately on the
computer.

## Nighty 2.6.2

The release adds:

- Python 3.14 for the scripting runtime
- native custom slash commands
- PWA support in UI version 2026.6.0

PWA support is beta. It requires Nighty's web version, a domain, and HTTPS. It
does not add a separate NightyScript API. The reset-token fix and other minor
fixes in 2.6.2 do not change the scripting interface.

## Python 3.14 features

Scripts can use Python 3.14 language syntax and the standard-library modules
included in Nighty's build. Relevant additions include:

- template string literals, written with a `t` prefix
- deferred evaluation of annotations
- `annotationlib` for inspecting annotations
- `compression.zstd` and Zstandard archive support
- improved asyncio introspection
- `concurrent.interpreters`

A template string is not a normal `str`. Keep using f-strings when a Nighty or
Discord method expects text.

Python 3.14 defers annotations until they are inspected. Code that reads
annotations should use `annotationlib.get_annotations()` instead of reading a
class namespace directly. Native slash commands should use the option types in
[Native slash commands](slash-commands.md).

Some standard-library modules depend on the operating system or how Python was
built. Check an import in Nighty before depending on an optional module.

## Compatibility changes

Python 3.14 no longer creates an event loop when `asyncio.get_event_loop()` is
called without a current loop. Inside an async command, listener, or callback,
use:

```python
loop = asyncio.get_running_loop()
```

Do not call `asyncio.run()` from a Nighty command or listener. Nighty already
owns the running event loop.

Python 3.14 also removed several deprecated interfaces:

| Removed interface | Replacement |
| --- | --- |
| `ast.Num`, `ast.Str`, and related aliases | `ast.Constant` |
| `pkgutil.get_loader()` and `find_loader()` | `importlib.util.find_spec()` |
| `sqlite3.version` | `sqlite3.sqlite_version` |
| `sqlite3.version_info` | `sqlite3.sqlite_version_info` |
| `urllib.request.URLopener` | `urlopen()` or `build_opener()` |
| `urllib.request.FancyURLopener` | `urlopen()` or `build_opener()` |
| asyncio child-watcher APIs | asyncio subprocess APIs |

Avoid these newly deprecated interfaces in new scripts:

- `asyncio.iscoroutinefunction()`; use `inspect.iscoroutinefunction()`
- the asyncio event-loop policy system
- `codecs.open()`; use `open()`
- `os.popen()` and `os.spawn*()`; use `subprocess`
- `argparse.FileType`; open the selected path after parsing

Other behavior changes can affect older scripts:

- Linux now defaults to `forkserver` for `multiprocessing` and
  `ProcessPoolExecutor`; Windows and macOS still default to `spawn`.
- `pickle.dump()` and `pickle.dumps()` raise `PicklingError` for more failures.
- A regular-expression `\B` pattern can now match an empty input.
- `functools.partial` now behaves as a method descriptor when stored on a
  class; wrap it with `staticmethod()` to keep the previous behavior.

## Third-party packages

Python 3.14 support in Nighty does not guarantee that every package supports
Python 3.14.

- Pure-Python packages must declare or otherwise work with Python 3.14.
- Packages with compiled extensions need a compatible CPython 3.14 build for
  the operating system and CPU architecture.
- A package installed into another Python installation may not be visible to
  Nighty's embedded process.
- Installing `discord.py`, `discord.py-self`, or a package named `nighty` is not
  a replacement for Nighty's injected objects.

Check the package's Python support before adding it to a script. Document every
external dependency and fail with a clear message when an import is missing.

```python
try:
    import example_package
except ImportError:
    print(
        "This script requires example_package with Python 3.14 support.",
        type_="ERROR"
    )
    return
```

Python 3.14 offers optional free-threaded and experimental JIT builds. Nighty's
move to Python 3.14 does not by itself confirm that either mode is enabled. Do
not depend on free-threading or JIT behavior unless Nighty reports support for
it.

## Check a script locally

Use a Python 3.14 interpreter so the parser matches Nighty.

Windows:

```powershell
py -3.14 -m py_compile your_script.py
```

Linux:

```bash
python3.14 -m py_compile your_script.py
```

This catches syntax errors. It does not execute imports, supply Nighty's
injected globals, or prove that a package is installed in Nighty's environment.

To confirm the running version from a script:

```python
import sys

print(sys.version)
```

## References

- [What's new in Python 3.14](https://docs.python.org/3.14/whatsnew/3.14.html)
- [Python 3.14 library reference](https://docs.python.org/3.14/library/index.html)
- [Nighty custom slash commands](https://docs.nighty.one/scripting/custom-slash-commands)
