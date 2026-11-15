# Discord Components V2

`slashReply()` uses the active Nighty theme, including its Components V2
layout. Use it unless the command needs a custom container, button, select,
gallery, or section.

Custom layouts use `discord_bot.ui.LayoutView`. Nighty supplies `discord_bot` at
runtime, so scripts do not import it.

## Send a layout

Nighty defers slash commands after 1.5 seconds. This helper handles a fresh
interaction, a deferred thinking response, and later followups:

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

Direct layout responses do not apply Nighty's Force-private or Forward mode.
Pass `private` yourself when the command needs a fixed visibility setting.

## Build a layout

```python
class StatusView(discord_bot.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=300)

        container = discord_bot.ui.Container(accent_color=0x5865F2)
        container.add_item(
            discord_bot.ui.Section(
                discord_bot.ui.TextDisplay(
                    "## Nighty status\nGateway connected. Scripts ready."
                ),
                accessory=discord_bot.ui.Thumbnail(
                    str(bot.user.display_avatar.url)
                )
            )
        )
        container.add_item(discord_bot.ui.Separator())
        self.add_item(container)
```

Common layout classes include:

| Class | Purpose |
| --- | --- |
| `Container` | Groups components and sets an accent color. |
| `Section` | Pairs text with an accessory. |
| `TextDisplay` | Renders Markdown text. |
| `Thumbnail` | Adds a section thumbnail. |
| `MediaGallery` | Displays one or more media items. |
| `Separator` | Adds spacing or a divider. |
| `ActionRow` | Holds buttons and selects. |

## Buttons

```python
class CounterView(discord_bot.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=300)
        self.count = 0
        self.render()

    def render(self):
        self.clear_items()

        plus = discord_bot.ui.Button(
            label="+1",
            style=discord_bot.ButtonStyle.success
        )
        reset = discord_bot.ui.Button(
            label="Reset",
            style=discord_bot.ButtonStyle.secondary
        )
        plus.callback = self.on_plus
        reset.callback = self.on_reset

        container = discord_bot.ui.Container(accent_color=0x5865F2)
        container.add_item(
            discord_bot.ui.TextDisplay(f"## Counter: {self.count}")
        )
        container.add_item(discord_bot.ui.Separator())
        container.add_item(discord_bot.ui.ActionRow(plus, reset))
        self.add_item(container)

    async def on_plus(self, interaction):
        self.count += 1
        self.render()
        await interaction.response.edit_message(view=self)

    async def on_reset(self, interaction):
        self.count = 0
        self.render()
        await interaction.response.edit_message(view=self)
```

Button and select callbacks must respond within three seconds. Nighty's slash
command auto-defer does not cover component callbacks.

## Command example

```python
@slashCommand(name="counter", description="Counter with buttons")
async def counter(interaction: discord_bot.Interaction):
    await send_v2(interaction, CounterView())
```

## Use `slashReply()` for themed text

Custom layouts bypass some of Nighty's response handling. Prefer `slashReply()`
for text, titles, thumbnails, and one large image:

```python
await slashReply(
    interaction,
    "12 checks passed.",
    title="Build complete",
    image="https://example.com/report.png"
)
```

`slashReply()` handles the active theme, privacy settings, auto-defer, followups,
and long text.

## Example

See [`components_v2_example.py`](../example-scripts/components_v2_example.py).

## Official reference

[Custom Slash Commands: Components V2](https://docs.nighty.one/scripting/custom-slash-commands#components-v2)
