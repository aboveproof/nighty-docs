# Reload-safe Nighty scripts

Nighty can replace a script without restarting its Python process. Tasks, listeners, gateway clients, callback registrations, and browser state may survive the old script instance.

Reload-safe code gives each script load an owner and closes work owned by the previous load.

## Runtime state

Store runtime ownership on `bot` with a script-specific key:

```python
RUNTIME_KEY = "_channel_notes_runtime"
previous = getattr(bot, RUNTIME_KEY, None)

runtime = {
    "tasks": set(),
    "listeners": [],
    "closed": False
}
setattr(bot, RUNTIME_KEY, runtime)
```

Do not use a generic key such as `_runtime`. Another script could replace it.

## Close tasks from the previous load

```python
if isinstance(previous, dict):
    previous["closed"] = True
    for task in list(previous.get("tasks", set())):
        try:
            if task and not task.done():
                task.cancel()
        except Exception:
            pass
```

A cancelled task must stop without restarting itself.

## Create tracked tasks

CUI callbacks may run on worker threads. Use Nighty's bot loop instead of `asyncio.create_task()` when the caller may lack a current loop.

```python
def create_tracked_task(coroutine):
    try:
        task = bot.loop.create_task(coroutine)
    except Exception as error:
        try:
            coroutine.close()
        except Exception:
            pass
        print(f"[Channel Notes] Task error: {error}", type_="ERROR")
        return None

    runtime["tasks"].add(task)
    task.add_done_callback(runtime["tasks"].discard)
    return task
```

Close an unstarted coroutine when task creation fails. Python will otherwise warn that the coroutine was never awaited.

## Worker loop

```python
async def refresh_worker():
    try:
        while not runtime["closed"]:
            await refresh_state()
            await asyncio.sleep(15)
    except asyncio.CancelledError:
        return
    except Exception as error:
        print(f"[Channel Notes] Worker error: {error}", type_="ERROR")

create_tracked_task(refresh_worker())
```

Use a bounded delay and catch errors at the worker boundary. Do not run a tight retry loop after a network failure.

## Listener ownership

Remove listeners from the previous load before registering replacements:

```python
if isinstance(previous, dict):
    for event_name, handler in previous.get("listeners", []):
        try:
            bot.remove_listener(handler, event_name)
        except Exception:
            pass

async def handle_message(message):
    if runtime["closed"]:
        return
    if message.author.id == bot.user.id:
        return
    # Handle the event.

bot.add_listener(handle_message, "on_message")
runtime["listeners"].append(("on_message", handle_message))
```

`@bot.listen` remains useful for short scripts. Long-lived scripts benefit from explicit listener ownership because the cleanup code has a handler reference.

## Gateway and HTTP clients

Store clients in runtime state and close them during replacement:

```python
runtime["clients"] = set()

async def close_previous_clients():
    if not isinstance(previous, dict):
        return
    for client in list(previous.get("clients", set())):
        try:
            await client.close()
        except Exception as error:
            print(f"[Channel Notes] Client close error: {error}", type_="ERROR")

create_tracked_task(close_previous_clients())
```

Create `aiohttp.ClientSession` inside an async function and close it in `finally` or an async context manager.

## Socket.IO handlers

UI scripts can leave Socket.IO connect handlers after reloads. Mark handlers with an owner value or keep a registry:

```python
SOCKET_OWNER = "channel-notes-v1"

@socketio.on("connect")
def restore_channel_notes_ui():
    evaluate_js(CHANNEL_NOTES_JS)

restore_channel_notes_ui._nighty_owner = SOCKET_OWNER
```

If the Socket.IO wrapper supports a handler registry, remove handlers with the same owner before registering the new handler. Do not clear handlers owned by other scripts.

## Browser state

Python state and browser state have separate lifetimes:

- A script reload replaces Python definitions.
- A tab refresh replaces `window`, observers, injected styles, and custom elements.
- A Nighty restart replaces both.

Reinstall browser helpers after tab render and Socket.IO connect. Keep installation idempotent:

```javascript
(function () {
    if (window.channelNotesObserver) {
        window.channelNotesObserver.disconnect();
    }

    const oldStyle = document.getElementById('channel-notes-style');
    if (oldStyle) oldStyle.remove();

    const style = document.createElement('style');
    style.id = 'channel-notes-style';
    style.textContent = '.channel-note { font-size: 13px; }';
    document.head.appendChild(style);

    window.channelNotesObserver = new MutationObserver(function () {
        // Restore dynamic UI state.
    });
    window.channelNotesObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
})();
```

Idempotent installation removes the old observer and style before adding replacements.

## UI repaint order

Render static UI first. Restore cached data before starting slow gateway or HTTP work.

```python
tab.render()
update_cached_rows()
create_tracked_task(start_network_clients())
```

This order keeps a private tab from waiting on secondary account logins or remote APIs.

## JSON writes on Windows

Antivirus software and sync tools may hold the destination file during `Path.replace()`. Use a process lock and preserve the old file if a save fails.

```python
import json
import threading
import uuid

save_lock = threading.RLock()

def save_json(path, data):
    temp_path = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    path.parent.mkdir(parents=True, exist_ok=True)

    with save_lock:
        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
                file.flush()
            temp_path.replace(path)
            return True
        except OSError as error:
            print(f"[Storage] Save error: {error}", type_="ERROR")
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
            return False
```

Do not replace valid token data with an empty default after a read error. Return the read error to the UI and keep the source file unchanged.

## Retry limits

Use capped backoff for network reconnects:

```python
delay = 2
for attempt in range(5):
    try:
        await connect_gateway()
        break
    except Exception as error:
        print(f"[Gateway] Attempt {attempt + 1} failed: {error}", type_="ERROR")
        await asyncio.sleep(delay)
        delay = min(delay * 2, 30)
```

Stop retries when the runtime closes. Separate permanent failures, such as an invalid token, from transport failures.

## Checklist

- Store tasks and listeners under a script-specific runtime key.
- Cancel tasks from the previous load.
- Remove listeners from the previous load.
- Close gateway and HTTP clients.
- Queue thread callbacks on `bot.loop`.
- Reinstall browser code after page reconnects.
- Make JavaScript installation idempotent.
- Render cached UI before slow network startup.
- Bound retries and request timeouts.
- Keep valid storage data after a failed save.

## Example

See [`reload_safe_worker.py`](../example-scripts/reload_safe_worker.py).
