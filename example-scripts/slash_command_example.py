@nightyScript(
    name="Slash Command Example",
    author="rico",
    description="Native slash commands, options, groups, and autocomplete",
    usage="/account id, /tools echo, /color"
)
def slash_command_example():
    """
    SLASH COMMAND EXAMPLE

    COMMANDS:
    /account id - Show the invoking account ID
    /account context - Show the current Discord context
    /tools echo - Repeat text
    /color - Choose a color with autocomplete
    """
    @slashCommand(
        name="id",
        description="Show your Discord account ID",
        group="account",
        group_description="Account details"
    )
    async def account_id(interaction: discord_bot.Interaction):
        await slashReply(
            interaction,
            f"Your account ID is `{interaction.user.id}`.",
            title="Account ID"
        )

    @slashCommand(
        name="context",
        description="Show where this command is running",
        group="account"
    )
    async def account_context(interaction: discord_bot.Interaction):
        guild = interaction.guild
        if guild:
            text = f"Server: **{guild.name}**\nServer ID: `{guild.id}`"
        else:
            text = "Direct message or group chat."
        await slashReply(interaction, text, title="Context")

    @slashCommand(
        name="echo",
        description="Repeat text",
        group="tools",
        group_description="Text tools"
    )
    @app_commands.describe(text="Text to repeat")
    async def tools_echo(
        interaction: discord_bot.Interaction,
        text: str
    ):
        await slashReply(interaction, text[:4000], show_thumbnail=False)

    colors = ["blue", "green", "orange", "red", "violet"]

    @slashCommand(name="color", description="Choose a saved color")
    async def color(interaction: discord_bot.Interaction, name: str):
        await slashReply(interaction, f"Selected **{name}**.")

    @color.autocomplete("name")
    async def color_autocomplete(
        interaction: discord_bot.Interaction,
        current: str
    ):
        query = current.casefold()
        return [
            app_commands.Choice(name=name.title(), value=name)
            for name in colors
            if query in name.casefold()
        ][:25]


slash_command_example()
