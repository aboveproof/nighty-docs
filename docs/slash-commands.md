# Native slash commands

Nighty exposes two Discord clients:

- `bot` runs the user account connection and prefix commands.
- `bot_app` owns the application-command tree used by slash commands.

[lord-m1nx/nighty-slash-api](https://github.com/lord-m1nx/nighty-slash-api) wraps `bot_app.tree` with command decorators, response handling, state storage, and hash-based synchronization.

## Choose the correct command type

| Task | API |
|---|---|
| Create a text command that uses the Nighty prefix | `@bot.command` |
| Register your own `/command` | `@slash.command` |
| Run a slash command owned by another Discord application | `exec_slash` |

`exec_slash` does not register commands. The Slash API does not invoke commands owned by other bots.

## Install the framework block

1. Open [`slashapi.py`](https://github.com/lord-m1nx/nighty-slash-api/blob/main/slashapi.py).
2. Copy the code between the `SLASH API START` and `SLASH API END` markers.
3. Paste that block inside your `@nightyScript` function.
4. Create one `SlashAPI` instance with a label unique to the script.
5. Define commands below the framework block.
6. Call `slash.autosync()` after the command definitions.

Do not import `discord`, `app_commands`, or `bot_app`. Nighty injects those names.

```python
@nightyScript(
    name="Status Tools",
    author="rico",
    description="Native status slash commands",
    usage="UI and slash commands"
)
def status_tools():
    # Paste the Slash API framework block here.

    slash = SlashAPI(label="StatusTools")

    @slash.command(description="Show the current status")
    async def status(ctx):
        await ctx.send("Status: ready", ephemeral=True)

    slash.autosync()

status_tools()
```

## Unique labels

The label separates command ownership and saved fingerprints:

```python
slash = SlashAPI(label="StatusTools")
```

Do not reuse a label in another script. A collision can overwrite the active instance and its saved command state.

The framework stores its state in `json/slashapi_state.json`.

## Typed options

Function annotations define Discord option types:

```python
from typing import Literal

@slash.command(
    description="Create a reminder",
    describe={
        "minutes": "Delay in minutes",
        "visibility": "Choose who can see the response"
    }
)
async def remind(
    ctx,
    minutes: int,
    visibility: Literal["private", "public"] = "private"
):
    await ctx.send(
        f"Reminder set for {minutes} minutes.",
        ephemeral=visibility == "private"
    )
```

Place required parameters before parameters with defaults. Discord rejects a command when an optional parameter appears before a required parameter.

Common annotations include:

- `str`
- `int`
- `float`
- `bool`
- `Literal[...]`
- Nighty-injected Discord types such as `discord.User`, `discord.Member`, `discord.Role`, `discord.TextChannel`, and `discord.Attachment`

## Command names and descriptions

Discord command names use lowercase letters, numbers, hyphens, and underscores. Descriptions must fit Discord's 100-character limit.

```python
@slash.command(
    name="user-info",
    description="Show a user's account details",
    describe={"user": "User to inspect"}
)
async def user_info(ctx, user: discord.User):
    await ctx.send(f"User ID: `{user.id}`", ephemeral=True)
```

## Groups and subcommands

```python
tools = slash.group("tools", "Utility commands")

@tools.command(name="ping", description="Measure command response")
async def tools_ping(ctx):
    await ctx.send("Pong", ephemeral=True)

@tools.command(name="echo", description="Repeat text")
async def tools_echo(ctx, text: str):
    await ctx.send(text, ephemeral=True)
```

Discord does not run a group by itself. Users choose one of its subcommands.

## Autocomplete

Autocomplete handlers return up to 25 choices:

```python
CHANNEL_NAMES = ["general", "support", "updates", "voice"]

@slash.command(description="Select a saved channel name")
async def channel(ctx, name: str):
    await ctx.send(f"Selected `{name}`", ephemeral=True)

@channel.autocomplete("name")
async def channel_name_autocomplete(ctx, current: str):
    query = current.casefold()
    return [
        name for name in CHANNEL_NAMES
        if query in name.casefold()
    ][:25]
```

Keep autocomplete handlers fast. Discord waits for the suggestions before it updates the command menu.

## Context menus

```python
@slash.menu("Copy Message ID", target="message")
async def copy_message_id(ctx, message: discord.Message):
    await ctx.send(f"`{message.id}`", ephemeral=True)

@slash.menu("Show User ID", target="user")
async def show_user_id(ctx, user: discord.User):
    await ctx.send(f"`{user.id}`", ephemeral=True)
```

Context-menu names appear under Discord's Apps menu.

## Guilds, DMs, and group chats

Current Slash API builds apply these decorators when Nighty's application-command library exposes them:

```python
app_commands.allowed_contexts(
    guilds=True,
    dms=True,
    private_channels=True
)

app_commands.allowed_installs(
    guilds=True,
    users=True
)
```

User-installed commands can run in servers where the Nighty application bot has no guild cache. Use `ctx.selfbot_guild` when you need the user account's cached guild:

```python
guild = ctx.guild or ctx.selfbot_guild
if not guild:
    await ctx.error("This command needs a server.")
    return
```

DM-safe handlers should treat `ctx.guild`, `ctx.guild_id`, and `ctx.selfbot_guild` as optional.

## Response lifecycle

### Initial response

```python
await ctx.send("Saved.", ephemeral=True)
```

### Work that may exceed three seconds

```python
await ctx.defer(ephemeral=True)
result = await fetch_report()
await ctx.send(result, ephemeral=True)
```

### Error response

```python
if amount < 1:
    await ctx.error("Amount must be greater than zero.")
    return
```

The context wrapper tracks the initial response, deferred state, and follow-ups. Pass the ephemeral setting on the first response or defer call.

## Components V2 responses

The upstream Slash API ships themed embed helpers. Scripts can also send Components V2 through the raw interaction callback. Read [Discord Components V2](components-v2.md) and the [Components V2 example](../example-scripts/components_v2_example.py).

## Hash synchronization

`slash.autosync()` fingerprints the command definitions. It contacts Discord when the command shape changes.

Changes that affect the fingerprint include:

- command names and descriptions
- option types, order, defaults, and descriptions
- groups, autocomplete handlers, and context menus

Keep `slash.autosync()` after all decorators. Moving it above a command leaves that command out of the registration pass.

## Development sync

Global command registration may take time to appear in Discord. Guild-scoped registration appears sooner and suits development. Check the upstream API version before passing a guild option because the supported constructor and decorator arguments may change.

Refresh Discord after a sync. Discord caches the command menu.

## Error handling

```python
@slash.error
async def slash_error(ctx, error):
    print(f"[Status Tools] Slash error: {error}", type_="ERROR")
    await ctx.error("The command failed. Check the Nighty console.")
```

Keep user-facing errors short. Put tracebacks and response bodies in the Nighty console.

## Reload behavior

A script reload may leave old commands in the in-memory tree until the framework reconciles its state. Use a stable label and the framework's management command to inspect or prune stale registrations.

Do not bulk-clear `bot_app.tree`. Another Nighty script may own commands in the same tree.

## Troubleshooting

### Command does not appear

- Confirm that `slash.autosync()` runs after the decorators.
- Check the Nighty console for an HTTP 400 response.
- Confirm that the label differs from labels in other scripts.
- Refresh Discord's client after the sync.

### Discord returns HTTP 400

Check the command name, description length, parameter order, annotations, and choice count.

### Reply becomes public

Pass `ephemeral=True` to the first `ctx.send()` or `ctx.defer()` call. Discord fixes response visibility when the interaction starts.

### Commands disappear after another script loads

Check labels for collisions. Search other scripts for code that clears or replaces the full application-command tree.

## Source

- [Slash API repository](https://github.com/lord-m1nx/nighty-slash-api)
- [Slash API developer manual](https://github.com/lord-m1nx/nighty-slash-api/blob/main/Documentation.md)
