"""
Example: List sharing groups from Leneda.

Environment variables:
    LENEDA_API_KEY: Your Leneda API key
    LENEDA_ENERGY_ID: Your Energy ID

Usage:
    python examples/sharing_groups.py
    python examples/sharing_groups.py --type CEL
    python examples/sharing_groups.py --all
    python examples/sharing_groups.py --page 1 --size 20
"""

import argparse
import asyncio
import logging
import os
import sys

from leneda import LenedaClient

SHARING_GROUP_TYPES = ["AIR", "AIN", "ACR", "AC1", "CEL", "APS", "CER", "CEN"]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="List Leneda sharing groups")

    parser.add_argument(
        "--api-key",
        help="Your Leneda API key, or set LENEDA_API_KEY",
    )
    parser.add_argument(
        "--energy-id",
        help="Your Energy ID, or set LENEDA_ENERGY_ID",
    )
    parser.add_argument(
        "--type",
        choices=SHARING_GROUP_TYPES,
        help="Filter by sharing group type",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page number to retrieve. Default: 1",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=10,
        help="Number of items per page. Default: 10",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Fetch all pages instead of only one page",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    return parser.parse_args()


def get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    """Get API credentials from arguments or environment variables."""
    api_key = args.api_key or os.environ.get("LENEDA_API_KEY")
    energy_id = args.energy_id or os.environ.get("LENEDA_ENERGY_ID")

    if not api_key:
        print("Error: API key not provided.")
        print("Use --api-key or set LENEDA_API_KEY.")
        sys.exit(1)

    if not energy_id:
        print("Error: Energy ID not provided.")
        print("Use --energy-id or set LENEDA_ENERGY_ID.")
        sys.exit(1)

    return api_key, energy_id


def print_group(group) -> None:
    """Print one sharing group."""
    print(
        f"{group.contract_number} | "
        f"{group.type} | "
        f"Owner={group.owner_energy_id} | "
        f"Manager={group.manager_energy_id} | "
        f"Start={group.start_date} | "
        f"End={group.end_date}"
    )


async def main() -> None:
    """Run the sharing groups example."""
    args = parse_arguments()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    api_key, energy_id = get_credentials(args)

    client = LenedaClient(
        api_key=api_key,
        energy_id=energy_id,
        debug=args.debug,
    )

    try:
        if args.all:
            groups = await client.list_sharing_groups(
                type=args.type,
                size=args.size,
            )

            print(f"Retrieved {len(groups)} sharing group(s).")

            if not groups:
                print("No sharing groups found for this Energy ID.")
                return

            print()
            for group in groups:
                print_group(group)

        else:
            page = await client.get_sharing_groups(
                page=args.page,
                size=args.size,
                type=args.type,
            )

            print(
                f"Page {page.number}/{page.total_pages} - "
                f"{len(page.content)} item(s) on this page, "
                f"{page.total_elements} total item(s)."
            )

            if not page.content:
                print("No sharing groups found on this page.")
                return

            print()
            for group in page.content:
                print_group(group)

    except Exception as exc:
        print(f"Error while retrieving sharing groups: {exc}")
        if args.debug:
            raise
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
