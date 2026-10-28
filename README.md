<a id="top"></a>

<div align="center">

<h1>NightyScript Documentation</h1>

<h3>Version 5.0</h3>

<p>Public reference for Nighty scripts, native slash commands, Discord Components V2, and custom Nighty tabs.</p>

<p>
  <img alt="Documentation version" src="https://img.shields.io/badge/docs-v5.0-5865F2?style=for-the-badge">
  <img alt="Slash commands" src="https://img.shields.io/badge/slash_commands-supported-2EA44F?style=for-the-badge">
  <img alt="Components V2" src="https://img.shields.io/badge/Components-V2-EB459E?style=for-the-badge">
  <img alt="CUI" src="https://img.shields.io/badge/CUI-documented-0EA5E9?style=for-the-badge">
</p>

<p>
  <a href="#quick-start"><strong>Quick start</strong></a>
  ·
  <a href="#documentation"><strong>Documentation</strong></a>
  ·
  <a href="#example-scripts"><strong>Examples</strong></a>
  ·
  <a href="#troubleshooting"><strong>Troubleshooting</strong></a>
</p>

<p><strong>Maintained by:</strong> <u>rico</u> · <code>1361736124858630274</code></p>

<p><strong>Made with:</strong> <a href="https://manus.im">manus.im</a> · <a href="https://claude.ai">Claude</a> · <a href="https://openai.com/codex/">OpenAI Codex</a></p>

</div>

---

> [!NOTE]
> Nighty injects its scripting objects at runtime. Do not install or import `nighty` or `discord.py` inside a NightyScript.

## Documentation

| Guide | Covers |
| --- | --- |
| [Native slash commands](docs/slash-commands.md) | Typed options, command groups, autocomplete, contexts, and sync |
| [Discord Components V2](docs/components-v2.md) | Containers, sections, text displays, media, separators, and callbacks |
| [CUI and custom tabs](docs/cui.md) | Custom HTML elements, callbacks, pagination, and browser reloads |
| [Reload-safe scripts](docs/reload-safety.md) | Tasks, listeners, sockets, cleanup, and shared runtime state |
| [Troubleshooting](docs/troubleshooting.md) | Common load, interaction, CUI, storage, and event-loop failures |
| [Example scripts](#example-scripts) | Complete files ready to inspect and adapt |

## Quick start

### 1. Understand the runtime

Nighty runs scripts inside its own Python process. Nighty supplies `bot`, `bot_app`, `nightyScript`, `Tab`, `UI`, configuration helpers, theme helpers, and Discord objects.

Do not import Nighty or Discord packages:

```python
# Unsupported
import discord
import nighty
from discord import *
from nighty import *
```

Use standard-library imports and dependencies documented by the script. Keep imports inside the decorated function when Nighty callbacks need them. Nighty may execute a script with separate global and local namespaces.

### 2. Start with the script wrapper

```python
@nightyScript(
    name="Channel Notes",
    author="rico",
    description="Save a note for the current channel",
    usage="<p>channelnote <text>"
)
def channel_notes():
    """
    CHANNEL NOTES

    COMMANDS:
    <p>channelnote <text> - Save a note for the current channel
    """

    @bot.command(
        name="channelnote",
        usage="<text>",
        description="Save a note for the current channel"
    )
    async def channel_note(ctx, *, text: str):
        await ctx.message.delete()
        updateConfigData(f"channel_note_{ctx.channel.id}", text.strip())
        await ctx.send("Saved the channel note.", silent=True)

channel_notes()
```

Call the decorated function at the end of the file. Nighty will not register the script until that call runs.

### 3. Pick the right interface

- Use `@bot.command` for prefix commands.
- Use [nighty-slash-api](docs/slash-commands.md) for native application commands.
- Use `Tab`, `UI`, and [CUI](docs/cui.md) for Nighty settings pages.
- Use [Components V2](docs/components-v2.md) for structured Discord interaction responses.

---

## Core reference

### Configuration

Use Nighty's configuration store for booleans, strings, and numbers:

```python
enabled = getConfigData().get("channel_notes_enabled", True)
updateConfigData("channel_notes_enabled", False)
```

Prefix keys with the script name. This prevents collisions with other scripts.

### JSON storage

Use a JSON file for lists and nested data:

```python
from pathlib import Path
import json

DATA_DIR = Path(getScriptsPath()) / "json"
DATA_FILE = DATA_DIR / "channel_notes.json"

def load_notes():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {"notes": {}}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"notes": {}}

def save_notes(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    except OSError as error:
        print(f"[Channel Notes] Save error: {error}", type_="ERROR")
        return False
```

Store tokens and webhook URLs outside source files. Do not commit runtime JSON files.

### Prefix commands

```python
@bot.command(
    name="quote",
    aliases=["q"],
    usage="<message>",
    description="Send a quoted message"
)
async def quote_command(ctx, *, message: str):
    await ctx.message.delete()
    message = message.strip()
    if not message:
        await ctx.send("Add a message to quote.", silent=True)
        return
    await ctx.send(f"> {message}")
```

`<p>` in usage text represents the prefix set in Nighty. Scripts do not parse the prefix.

Use one command with subcommands when the actions share a purpose:

```python
@bot.command(name="notes", usage="<add|list|clear> [text]")
async def notes_command(ctx, *, args: str = ""):
    await ctx.message.delete()
    action, _, value = args.strip().partition(" ")
    action = action.lower()

    if action == "add" and value.strip():
        await ctx.send(f"Saved: {value.strip()}", silent=True)
    elif action == "list":
        await ctx.send("No saved notes.", silent=True)
    elif action == "clear":
        await ctx.send("Cleared saved notes.", silent=True)
    else:
        await ctx.send("Use `notes add`, `notes list`, or `notes clear`.", silent=True)
```

### Event listeners

```python
@bot.listen("on_message")
async def message_listener(message):
    if message.author.id == bot.user.id:
        return
    if getattr(message.author, "bot", False):
        return
    if "good morning" in message.content.lower():
        await message.channel.send("Good morning.", silent=True)
```

Filter events before network calls or file access. A listener runs for each matching Discord event.

Nighty keeps the Python process alive during script reloads. Scripts with listeners, tasks, or Socket.IO callbacks need cleanup code. Read [Reload-safe scripts](docs/reload-safety.md).

---

## Messages

### Plain text

```python
await ctx.send("Saved.", silent=True)
await message.channel.send("New event received.", silent=True)
```

### Legacy Nighty embed

Nighty does not support `discord.Embed` in standard scripts. Use `forwardEmbedMethod`:

```python
await forwardEmbedMethod(
    channel_id=ctx.channel.id,
    title="Build report",
    content="**Status:** Passed\n**Checks:** 12",
    image="https://example.com/report.png"
)
```

Supported arguments are `channel_id`, `title`, `content`, and `image`.

### Components V2

Components V2 supports containers, text displays, sections, media, and separators. Slash interactions can send V2 payloads through Discord's interaction callback. Read [Discord Components V2](docs/components-v2.md).

## Native slash commands

[nighty-slash-api](https://github.com/lord-m1nx/nighty-slash-api) registers commands on Nighty's `bot_app` tree. It supports typed options, groups, autocomplete, context menus, ephemeral responses, and hash-based synchronization.

```python
# Paste the Slash API framework block inside this script function first.
slash = SlashAPI(label="StatusTools")

@slash.command(description="Show the script status")
async def status(ctx):
    await ctx.send("Status: ready", ephemeral=True)

slash.autosync()
```

The API enables guild, direct-message, and private-channel contexts when the installed Nighty build exposes those decorators. Read [Native slash commands](docs/slash-commands.md) before adding the framework block.

## CUI and custom tabs

Nighty's native UI uses this hierarchy:

```text
Tab
└── CardContainer
    └── Card
        ├── Group
        └── UI element
```

```python
tab = Tab(name="Task Queue", icon="inbox", gap=4)
container = tab.create_container(type="rows", width="full", height="auto", gap=4)
card = container.create_card(type="rows", width="full", height="auto", gap=3)

card.create_ui_element(UI.Text, content="Task Queue", size="lg", weight="bold")
task_input = card.create_ui_element(
    UI.Input,
    label="Task",
    placeholder="Enter a task",
    full_width=True
)
save_button = card.create_ui_element(UI.Button, label="Save", color="primary")

async def save_task():
    value = str(task_input.value or "").strip()
    if not value:
        tab.toast("Task required", "Enter a task name.", "ERROR")
        return
    tab.toast("Task saved", value, "SUCCESS")

save_button.onClick = save_task
tab.render()
```

CUI adds custom HTML elements and callable overlays without changing the parent creation rules. Read [CUI and custom tabs](docs/cui.md).

---

## Runtime safety

### Async work

Use `aiohttp` for network requests:

```python
import aiohttp

async def fetch_json(url):
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
```

Move blocking libraries to an executor:

```python
async def run_blocking(function, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: function(*args))
```

Use `asyncio.sleep()` inside async functions. `time.sleep()` blocks Nighty's event loop.

### Logging

```python
print("[Task Queue] Loaded 12 tasks", type_="INFO")
print("[Task Queue] Save failed", type_="ERROR")
print("[Task Queue] Sync complete", type_="SUCCESS")
```

Include the script name and the failed operation. Keep tokens, cookies, and webhook URLs out of logs.

## Example scripts

### v5 examples

- [`slash_command_example.py`](example-scripts/slash_command_example.py): typed commands, groups, autocomplete, and contexts
- [`components_v2_example.py`](example-scripts/components_v2_example.py): themed Components V2 interaction responses
- [`cui_custom_element_example.py`](example-scripts/cui_custom_element_example.py): custom CUI element and callback
- [`reload_safe_worker.py`](example-scripts/reload_safe_worker.py): task and listener cleanup across reloads

### Existing examples

The [`example-scripts`](example-scripts) directory also covers JSON storage, configuration, event listeners, API clients, webhooks, selectors, tables, voice-message downloads, and browser automation.

## Limits

- Nighty scripts cannot build a complete cross-server user database.
- User and member access depends on Discord cache state and channel access.
- Native slash commands depend on Nighty's `bot_app` connection and Discord registration.
- CUI runs in Nighty's browser page. A browser refresh creates a new JavaScript window.
- Discord rate limits apply to messages, command syncs, and interaction callbacks.

<a id="troubleshooting"></a>

## Troubleshooting

Start with the dedicated [troubleshooting guide](docs/troubleshooting.md). It covers script load failures, missing slash commands, expired interactions, raw CUI placeholders, browser refresh problems, JSON write errors, and event-loop failures.

When reporting a bug, include:

- the full Nighty console error;
- the action that caused it;
- whether the script was freshly loaded or reloaded;
- whether Nighty Desktop or the web interface was used;
- the smallest script that still reproduces it.

---

## Credits

- [lord-m1nx/nighty-slash-api](https://github.com/lord-m1nx/nighty-slash-api) for the native slash-command framework
- cpores for CUI
- nes at Nighty for the Components V2 theme builder and schema
- [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) for the writing rules used in v5
- thatdudepyro for the Nighty UI scripting reference

## License

Released under the [GNU General Public License v3.0](LICENSE).

<div align="center">
  <sub>NightyScript Documentation v5.0</sub>
  <br>
  <a href="#top"><strong>Back to top</strong></a>
</div>
