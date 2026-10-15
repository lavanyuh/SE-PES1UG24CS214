
"""Address book application with contact management and safe backups."""

import csv
import hashlib
import json
import re

contacts: dict[str, dict[str, str]] = {}


def add_contact(
    full_name: str,
    phone: str,
    email: str = "",
    city: str = "Unknown",
) -> bool:
    """Add a contact after validating the phone number."""
    if not re.fullmatch(r"[0-9]{10}", phone):
        print("Invalid phone number for", full_name)
        return False

    contacts[full_name] = {
        "phone": phone,
        "email": email,
        "city": city,
    }
    return True


def contact_id(full_name: str) -> str:
    """Return a short SHA-256-based identifier for a contact name."""
    return hashlib.sha256(full_name.encode("utf-8")).hexdigest()[:6]


def search_contacts(text: str) -> list[str]:
    """Find contacts by matching a name or phone number."""
    found = []
    for name, info in contacts.items():
        if text.lower() in name.lower() or text in info["phone"]:
            found.append(name)
    return found


def update_city(full_name: str, city: str) -> bool:
    """Update a contact's city, returning False if the contact is absent."""
    contact = contacts.get(full_name)
    if contact is None:
        print("No contact named", full_name)
        return False

    contact["city"] = city
    return True


def contacts_by_city() -> dict[str, list[str]]:
    """Group contact names by city."""
    grouped: dict[str, list[str]] = {}
    for name, info in contacts.items():
        grouped.setdefault(info["city"], []).append(name)
    return grouped


def print_directory() -> None:
    """Print contacts in alphabetical order."""
    names = sorted(contacts)
    for index, name in enumerate(names, start=1):
        print(index, name, contacts[name]["phone"])


def export_csv(file_name: str = "contacts.csv") -> None:
    """Export all contacts to a UTF-8 CSV file."""
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for name, info in contacts.items():
            writer.writerow(
                [name, info["phone"], info["email"], info["city"]]
            )


def backup_book(file_name: str = "contacts.json") -> None:
    """Save contacts in JSON format instead of unsafe pickle format."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(contacts, file, indent=4)


def restore_book(
    file_name: str = "contacts.json",
) -> dict[str, dict[str, str]]:
    """Restore contacts from a JSON backup."""
    with open(file_name, "r", encoding="utf-8") as file:
        restored = json.load(file)

    if not isinstance(restored, dict):
        raise ValueError("Invalid backup: expected a contact dictionary.")

    for name, info in restored.items():
        if (
            not isinstance(name, str)
            or not isinstance(info, dict)
            or not all(
                isinstance(info.get(key), str)
                for key in ("phone", "email", "city")
            )
        ):
            raise ValueError("Invalid backup: malformed contact data.")

    return restored


def main() -> None:
    """Demonstrate address book functionality."""
    add_contact("Neha Sharma", "9876543210", "neha@example.com", "Bengaluru")
    add_contact("Rahul Verma", "9123456780", "rahul@example.com", "Mysuru")
    add_contact("Test User", "12345")
    add_contact("Kavya Nair", "9988776655", city="Bengaluru")

    update_city("Rahul Verma", "Chennai")
    update_city("Nobody", "Delhi")

    print_directory()
    print("Search 'ra':", search_contacts("ra"))
    print("By city:", contacts_by_city())
    print("Id for Neha:", contact_id("Neha Sharma"))

    export_csv()
    backup_book()
    restored = restore_book()
    print(
        "Contacts restored:",
        len(restored),
        "| first:",
        sorted(restored)[0],
    )
    print(
        "Restored contacts match the in-memory address book:",
        restored == contacts,
    )


if __name__ == "__main__":
    main()
