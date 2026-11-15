# Native slash commands

Nighty scripts register application commands with `@slashCommand` and answer
them with `slashReply()`.

```python
@slashCommand(name="hello", description="Say hello")
async def hello(interaction: discord_bot.Interaction):
    await slashReply(interaction, f"Hello {bot.user.mention}!")
```

Nighty supplies `slashCommand`, `slashReply`, `discord_bot`, and `app_commands`.
Do not import them.

## Register a command

```python
@slashCommand(
    name="roll",
    description="Roll a die",
    group=None,
    group_description=None,
    nsfw=False
)
```

| Argument | Purpose |
| --- | --- |
| `name` | Lowercase name, 1 to 32 characters, with no spaces. |
| `description` | Command description, up to 100 characters. |
| `group` | Registers the command as `/group name`. |
| `group_description` | Sets the group description on its first subcommand. |
| `nsfw` | Restricts the command to age-restricted channels. |

When omitted, `name` defaults to the function name.

The callback must use `async def` and accept `interaction` as its first
parameter. Define commands while the script loads. Nighty rejects names already
used by Nighty or another script.

`@slashCommand` returns an `app_commands.Command`. Decorators such as
`app_commands.describe`, `app_commands.choices`, and `app_commands.rename` work
with it. Keep `@slashCommand` above the other decorators:

```python
@slashCommand(name="repeat", description="Repeat text")
@app_commands.describe(text="Text to repeat", times="Number of copies")
async def repeat(
    interaction: discord_bot.Interaction,
    text: str,
    times: app_commands.Range[int, 1, 5] = 1
):
    await slashReply(interaction, "\n".join([text] * times))
```

Parameters without defaults are required. Parameters with defaults are
optional. Put required parameters first.

Supported option types include:

- `str`, `int`, `float`, and `bool`
- `discord_bot.User`, `Member`, `Role`, `Attachment`, and guild channels
- `app_commands.Range[...]` and `app_commands.Choice[...]`
- `Literal[...]`

## Send a reply

Use `slashReply()` for normal command responses:

```python
ok = await slashReply(
    interaction,
    "Build finished.",
    title="Status",
    image=None,
    thumbnail=None,
    show_thumbnail=True
)
```

`slashReply()` uses the active theme, including its Components V2 layout. It
also applies Nighty's Private, Force-private, and Forward settings.

Nighty defers a command after 1.5 seconds. `slashReply()` replaces the thinking
response, sends later calls as followups, and splits text longer than 4,000
characters.

Bad arguments raise `TypeError` or `ValueError`. Nighty shows the error to the
user. Delivery failures return `False` and write an error to the console.

## Subcommands

Set `group` to register `/group command`:

```python
@slashCommand(
    name="add",
    description="Add a note",
    group="notes",
    group_description="Quick notes"
)
async def notes_add(interaction: discord_bot.Interaction, text: str):
    await slashReply(interaction, f"Saved: {text}")

@slashCommand(name="list", description="List notes", group="notes")
async def notes_list(interaction: discord_bot.Interaction):
    await slashReply(interaction, "No notes yet.", title="Notes")
```

Nighty supports one group level. A name cannot be both a group and a top-level
command.

## Choices

```python
@slashCommand(name="rps", description="Rock paper scissors")
@app_commands.choices(pick=[
    app_commands.Choice(name="Rock", value="rock"),
    app_commands.Choice(name="Paper", value="paper"),
    app_commands.Choice(name="Scissors", value="scissors")
])
async def rps(
    interaction: discord_bot.Interaction,
    pick: app_commands.Choice[str]
):
    await slashReply(interaction, f"You picked **{pick.value}**.")
```

## Autocomplete

Autocomplete handlers return up to 25 choices:

```python
FRUITS = ["Apple", "Banana", "Cherry", "Grape", "Mango"]

@slashCommand(name="fruit", description="Pick a fruit")
async def fruit(interaction: discord_bot.Interaction, name: str):
    await slashReply(interaction, f"You picked **{name}**.")

@fruit.autocomplete("name")
async def fruit_autocomplete(
    interaction: discord_bot.Interaction,
    current: str
):
    query = current.casefold()
    return [
        app_commands.Choice(name=fruit, value=fruit)
        for fruit in FRUITS
        if query in fruit.casefold()
    ][:25]
```

Keep autocomplete handlers fast. Discord waits for them before updating the
command menu.

## Components V2

`slashReply()` uses the current theme. Build a `discord_bot.ui.LayoutView` when
the command needs custom containers, buttons, selects, or media galleries.

Nighty may defer the command before the custom layout is ready. Use a helper
that handles the initial response, the deferred placeholder, and followups:

```python
async def send_v2(interaction, view, private=None):
    if private is None:
        private = bool(getConfigData().get("private"))

    if not interaction.response.is_done():
        return await interaction.response.send_message(
            view=view,
            ephemeral=private
        )

    deferred = (
        interaction.response.type
        == discord_bot.InteractionResponseType.deferred_channel_message
    )
    if deferred and not interaction.extras.get("v2_placeholder_used"):
        interaction.extras["v2_placeholder_used"] = True
        return await interaction.edit_original_response(view=view)

    return await interaction.followup.send(view=view, ephemeral=private)
```

Custom layouts must set their own privacy. Nighty's Force-private and Forward
settings do not apply to direct `LayoutView` responses. Button and select
callbacks must answer within three seconds.

Read [Discord Components V2](components-v2.md) for a full layout example.

## Runtime rules

- Keep imports and helpers inside the `@nightyScript` function.
- Let uncaught command errors reach Nighty. It logs them and sends an
  ephemeral error.
- Use `await asyncio.sleep()` or `await runBlocking(...)` for blocking work.
- Send modals before Nighty's 1.5-second auto-defer.
- Press `Ctrl+R` in Discord if a new command does not appear.

Nighty syncs changes a few seconds after the script loads. Scripts do not need a
manual tree sync or a copied command framework.

## Official reference

[Custom Slash Commands](https://docs.nighty.one/scripting/custom-slash-commands)
