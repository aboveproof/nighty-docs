@nightyScript(
    name="Reload Safe Worker",
    author="rico",
    description="Track a worker task and listener across script reloads",
    usage="<p>workerstatus"
)
def reload_safe_worker():
    """
    RELOAD SAFE WORKER

    COMMANDS:
    <p>workerstatus - Show the worker tick count

    NOTES:
    Nighty can reload this script without restarting its Python process.
    This example cancels the previous task and removes its listener.
    """
    import asyncio

    runtime_key = "_docs_reload_safe_worker"
    previous = getattr(bot, runtime_key, None)

    if isinstance(previous, dict):
        previous["closed"] = True
        for task in list(previous.get("tasks", set())):
            try:
                if task and not task.done():
                    task.cancel()
            except Exception:
                pass
        for event_name, handler in previous.get("listeners", []):
            try:
                bot.remove_listener(handler, event_name)
            except Exception:
                pass

    runtime = {
        "closed": False,
        "tasks": set(),
        "listeners": [],
        "ticks": 0
    }
    setattr(bot, runtime_key, runtime)

    def create_tracked_task(coroutine):
        try:
            task = bot.loop.create_task(coroutine)
        except Exception as error:
            try:
                coroutine.close()
            except Exception:
                pass
            print(f"[Reload Safe Worker] Task error: {error}", type_="ERROR")
            return None

        runtime["tasks"].add(task)
        task.add_done_callback(runtime["tasks"].discard)
        return task

    async def worker():
        try:
            while not runtime["closed"]:
                runtime["ticks"] += 1
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            return
        except Exception as error:
            print(f"[Reload Safe Worker] Worker error: {error}", type_="ERROR")

    async def message_listener(message):
        if runtime["closed"]:
            return
        if message.author.id == bot.user.id:
            return

    bot.add_listener(message_listener, "on_message")
    runtime["listeners"].append(("on_message", message_listener))

    @bot.command(
        name="workerstatus",
        description="Show the reload-safe worker status"
    )
    async def worker_status(ctx):
        await ctx.message.delete()
        await ctx.send(
            f"Worker ticks: {runtime['ticks']}",
            silent=True
        )

    create_tracked_task(worker())


reload_safe_worker()
