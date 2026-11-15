@nightyScript(
    name="Components V2 Example",
    author="rico",
    description="Native Components V2 counter with buttons",
    usage="/counter"
)
def components_v2_example():
    """
    COMPONENTS V2 EXAMPLE

    COMMANDS:
    /counter - Open a private counter with increment and reset buttons
    """

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
                discord_bot.ui.Section(
                    discord_bot.ui.TextDisplay(
                        f"## Counter\nCurrent value: **{self.count}**"
                    ),
                    accessory=discord_bot.ui.Thumbnail(
                        str(bot.user.display_avatar.url)
                    )
                )
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

    @slashCommand(name="counter", description="Counter with buttons")
    async def counter(interaction: discord_bot.Interaction):
        await send_v2(interaction, CounterView())


components_v2_example()
