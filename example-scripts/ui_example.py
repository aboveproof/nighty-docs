@nightyScript(
    name="Native UI Example",
    author="rico",
    description="Demonstrates Nighty's native UI scripting framework",
    usage="Open the Native UI Example tab"
)
def native_ui_example():
    """
    NATIVE UI EXAMPLE

    Demonstrates containers, cards, groups, text, inputs, buttons,
    toggles, selects, checkboxes, tables, callbacks, and toasts.

    No external dependencies are required.
    """
    tab = Tab(name="Native UI Example", icon="star", gap=4)

    page = tab.create_container(
        type="rows",
        width="full",
        height="auto",
        gap=4
    )

    form_card = page.create_card(
        type="rows",
        width="full",
        height="auto",
        gap=3
    )
    form_card.create_ui_element(
        UI.Text,
        content="Profile",
        size="xl",
        weight="bold"
    )

    name_input = form_card.create_ui_element(
        UI.Input,
        label="Display name",
        placeholder="Enter a name",
        show_clear_button=True,
        required=True,
        full_width=True
    )

    role_select = form_card.create_ui_element(
        UI.Select,
        label="Role",
        items=[
            {"id": "member", "title": "Member"},
            {"id": "moderator", "title": "Moderator"},
            {"id": "administrator", "title": "Administrator"}
        ],
        selected_items=["member"],
        mode="single",
        full_width=True
    )

    notification_toggle = form_card.create_ui_element(
        UI.Toggle,
        label="Enable notifications",
        checked=True
    )
    confirmation = form_card.create_ui_element(
        UI.Checkbox,
        label="Confirm changes",
        checked=False
    )

    status_text = form_card.create_ui_element(
        UI.Text,
        content="No changes saved."
    )

    actions = form_card.create_group(
        type="columns",
        gap=2,
        full_width=True
    )
    save_button = actions.create_ui_element(
        UI.Button,
        label="Save",
        color="primary"
    )
    clear_button = actions.create_ui_element(
        UI.Button,
        label="Clear",
        variant="bordered",
        color="default"
    )

    def save_profile():
        name = str(name_input.value or "").strip()
        selected_roles = list(role_select.selected_items or [])

        name_input.invalid = not bool(name)
        name_input.error_message = "Enter a display name." if not name else ""
        confirmation.invalid = not bool(confirmation.checked)

        if not name or not confirmation.checked:
            status_text.content = "Complete the required fields."
            tab.toast("Not saved", "Check the highlighted fields.", "ERROR")
            return

        selected_role = selected_roles[0] if selected_roles else "none"
        notifications = "on" if notification_toggle.checked else "off"
        status_text.content = (
            f"Saved {name} as {selected_role}. Notifications are {notifications}."
        )
        tab.toast("Profile saved", name, "SUCCESS")

    def clear_profile():
        name_input.value = ""
        name_input.invalid = False
        name_input.error_message = ""
        role_select.selected_items = ["member"]
        notification_toggle.checked = True
        confirmation.checked = False
        confirmation.invalid = False
        status_text.content = "No changes saved."
        tab.toast("Cleared", "The form was reset.", "INFO")

    save_button.onClick = save_profile
    clear_button.onClick = clear_profile

    table_card = page.create_card(
        type="rows",
        width="full",
        height="auto",
        gap=3
    )
    table_card.create_ui_element(
        UI.Text,
        content="Accounts",
        size="xl",
        weight="bold"
    )

    account_table = table_card.create_ui_element(
        UI.Table,
        columns=[
            {"type": "text", "label": "Account"},
            {"type": "tag", "label": "Status"}
        ],
        rows=[
            {
                "id": "primary",
                "cells": [
                    {"text": "Primary", "subtext": "Main account"},
                    {"text": "Ready", "color": "green"}
                ]
            },
            {
                "id": "secondary",
                "cells": [
                    {"text": "Secondary", "subtext": "Backup account"},
                    {"text": "Idle", "color": "gray"}
                ]
            }
        ],
        search=True,
        items_per_page=10,
        selectable=True
    )

    selected_text = table_card.create_ui_element(
        UI.Text,
        content="No accounts selected."
    )

    def account_selection_changed(row_ids):
        selected = list(row_ids or [])
        selected_text.content = (
            f"Selected: {', '.join(selected)}"
            if selected
            else "No accounts selected."
        )

    account_table.onSelectionChange = account_selection_changed
    tab.render()


native_ui_example()
