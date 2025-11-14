import logging
import os
from dotenv import load_dotenv
from tabulate import tabulate

from dtek import DtekApi


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    city = os.environ.get("CITY")
    street = os.environ["STREET"]
    house = os.environ["HOUSE"]
    data = DtekApi.get_shutdowns(city=city, street=street, house=house)

    print()
    if city:
        print(f"City: {city}")
    print(f"Street: {street}")
    print(f"House: {house}")
    print()
    print(f"Group: {data.group}")

    state_map = {
        "yes": "++",
        "second": "+_",
        "no": "__",
        "first": "_+",
    }

    for fact, day_human in [
        (data.today, "Today"),
        (data.tomorrow, "Tomorrow"),
    ]:
        print()
        print(f"{day_human}:")
        print()
        print(
            tabulate(
                [[state_map[status] for status in fact.values()]],
                headers=list(fact.keys()),
                tablefmt="plain",
            )
        )
        print()


if __name__ == "__main__":
    load_dotenv()
    main()
