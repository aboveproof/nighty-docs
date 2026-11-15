# Troubleshooting

Start with the Nighty console. Record the script name, failed action, exception type, and Discord HTTP status. Remove tokens and interaction URLs before sharing logs.

## Script does not load

Check these items:

- The decorated function has a call at the end of the file.
- The script does not import `discord` or `nighty`.
- Imports required by callbacks live inside the script function.
- Python indentation remains inside the decorated function.
- The Nighty console shows no syntax error.

Run a local syntax check with Python 3.14:

```powershell
py -3.14 -m py_compile your_script.py
```

On Linux, use `python3.14 -m py_compile your_script.py`. An older interpreter
can reject valid 3.14 syntax or miss compatibility problems. This check cannot
supply Nighty's injected globals. See [Python 3.14 runtime](python-runtime.md).

## Package stopped importing after the Python update

Nighty 2.6.2 uses Python 3.14. Confirm that the package supports Python 3.14
and, for compiled packages, provides a compatible CPython 3.14 build. A package
installed into another Python installation may not be visible to Nighty.

Do not install `discord.py`, `discord.py-self`, or a package named `nighty` to
replace Nighty's injected objects.

## `There is no current event loop in thread`

Nighty called the function from a worker thread. Queue the coroutine on the bot loop:

```python
def run_async(coroutine):
    try:
        return bot.loop.create_task(coroutine)
    except Exception:
        try:
            coroutine.close()
        except Exception:
            pass
        raise
```

Use `asyncio.create_task()` only from a coroutine running on an event-loop thread.

## Prefix command does not run

- Confirm the command decorator sits inside the script function.
- Confirm the script function runs at the end of the file.
- Check for another command with the same name.
- Delete or rename legacy commands during a migration to slash commands.

## Slash command does not appear

- Confirm that `@slashCommand` is the top decorator.
- Define the command while the script loads, inside the script function.
- Check the console for a duplicate name or invalid command option.
- Refresh Discord after the sync.

Nighty syncs changes a few seconds after the script loads.

## `interaction already acknowledged`

The handler sent two initial responses. Use `slashReply()` for normal replies:

```python
await slashReply(interaction, "Done")
```

Nighty auto-defers slash commands after 1.5 seconds. A custom layout must replace
the deferred response or send a followup. Use the `send_v2()` helper in
[Discord Components V2](components-v2.md).

## Components V2 callback fails

- Respond to button and select interactions within three seconds.
- Call `interaction.response.edit_message(view=view)` after changing a layout.
- Rebuild the view before editing the message.
- Use `slashReply()` when the command only needs themed text or images.

## CUI shows raw `__CUI__` text

The browser runtime did not replace the placeholder.

- Run `evaluate_js(JS_CUI)` after the tab renders.
- Register custom templates with `window.cUIData.updateTemplates(...)`.
- Run the placeholder scan after registration.
- Reinstall CUI after Socket.IO connects.
- Disconnect the previous mutation observer before installing a replacement.

## CUI works after restarting Nighty but fails after page refresh

The browser page lost `window.cUIData` while Python stayed loaded. Add a Socket.IO connect handler that reinstalls CUI and its templates.

Keep the installer idempotent. A refresh can reuse the same Socket.IO session in some embedded browsers.

## CUI callback does not fire

Check four points:

1. `_init_params` includes the callback name.
2. `self.funcs` includes the callback.
3. The HTML uses `${callback_name}`.
4. `callback_store.register(_cui_cb)` runs during tab render.

CUI sends the browser element's value as text. Convert numbers and booleans in Python.

## Card width collapses

A hidden custom element may report no width during CUI measurement.

- Set the card width to `full`.
- Give sibling cards the same flex basis.
- Use `disallow_shrink=True` for narrow content-width cards.
- Avoid measuring a page before CUI injects its custom elements.

## Cards move when a pager changes page

The pager wrapper follows the active page height. Measure all pages and hold the wrapper at the tallest page height. Recalculate that value from a `ResizeObserver` after responsive width changes.

## JSON save returns `WinError 5`

Windows denied file replacement. Common causes include antivirus scanning, sync software, and another process holding the JSON file.

- Use a process lock around writes.
- Write a unique temporary file.
- Keep the original file when replacement fails.
- Report the file path and permission error.
- Close editors or sync tools that hold the file.

Do not clear stored tokens after a save error.

## Discord gateway closes with code 1006

Code 1006 reports an abnormal transport closure. It does not prove the token is invalid.

- Check the network, VPN, proxy, and firewall.
- Use Discord's gateway heartbeat from the HELLO payload.
- Disable aiohttp's separate WebSocket ping timer for Discord gateway sessions.
- Add capped reconnect backoff.
- Start saved accounts with spacing between IDENTIFY requests.
- Stop retrying after Discord rejects authentication or account verification.

Explain account requirements in the UI when Discord reports phone, email, or verification limits.

## Managed token cannot join a voice channel

Check the account before changing gateway code:

- The account belongs to the server.
- The account can view and connect to the channel.
- The account completed Discord verification requirements.
- The token represents the expected account.
- Discord accepted the gateway session.

Show the account-specific error in the managed-account row. A single generic toast does not identify the failing token.

## Blocking request freezes Nighty

Use `aiohttp` for HTTP calls. Move synchronous libraries to an executor:

```python
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(None, blocking_function)
```

Replace `time.sleep()` with `await asyncio.sleep()` inside async functions.

## Share a useful bug report

Include:

- Nighty version
- script version
- browser or private-tab environment
- action that failed
- sanitized console error
- whether the failure survives a Nighty restart

Remove account tokens, webhook URLs, cookies, interaction tokens, and private channel data.
