import argparse
import configparser
from dataclasses import dataclass
import pathlib
import sqlite3
from datetime import datetime
import requests

get_chest_empty_events_sql = \
    """
SELECT DISTINCT 
    co_user.user, 
    x, 
    z, 
    co_container.time, 
    main.co_material_map.material, 
    amount
FROM co_container
    JOIN co_user ON co_container.user = co_user.id
    JOIN co_material_map ON co_container.type = co_material_map.id
WHERE rolled_back = 0 AND
      action = 0 AND
      x BETWEEN ? AND ? AND
      z BETWEEN ? AND ? AND
      co_user.user NOT LIKE "#%" AND
      co_container.time > strftime('%s', 'now') - ?
ORDER BY co_container.time ASC;
"""


@dataclass
class Base:
    x1: int
    x2: int
    z1: int
    z2: int
    allowed_players: list[str]
    name: str


@dataclass
class ChestRemoveEvent:
    player: str
    x: int
    z: int
    time: int
    item: str
    amount: int


def get_bases(base_db_path: str) -> list[Base]:
    bases: list[Base] = []
    base_config = configparser.ConfigParser()
    base_config.read(base_db_path)
    for base in base_config.sections():
        allowed_players = base_config[base]["allowedplayers"]
        bases.append(Base(int(base_config[base]["x1"]),
                          int(base_config[base]["x2"]),
                          int(base_config[base]["z1"]),
                          int(base_config[base]["z2"]),
                          allowed_players.split(","),
                          base))
    return bases


def get_chest_remove_events(dbpath: str, b: Base) -> list[ChestRemoveEvent]:
    x = []
    db = sqlite3.connect(dbpath)
    for row in db.execute(get_chest_empty_events_sql, (b.x1, b.x2, b.z1, b.z2, 100000 * 60)):
        x.append(ChestRemoveEvent(row[0], row[1], row[2], row[3], row[4], row[5]))
    return x


def main():
    parser = argparse.ArgumentParser(description='Detect base breakins with coreprotect database.')
    parser.add_argument('--config', dest='configpath')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(pathlib.PurePath(args.configpath))

    bases = get_bases(str(pathlib.Path(config["paths"]["basedb"])))

    output = ""

    for base in bases:
        for event in get_chest_remove_events(config["paths"]["db"], base):
            if event.player not in base.allowed_players:
                output += f"""Possible stealing detected: {base.name} {datetime.utcfromtimestamp(event.time).strftime('%Y-%m-%d %H:%M:%S')} {event.player} {event.item.split(":")[1]} {event.amount}\n"""

    if output != "":
        print(output)
        session = requests.Session()
        session.auth = (config["webhook"]["user"], config["webhook"]["password"])
        params = dict(text="```\n" + output + "\n```")
        r = session.post(config["webhook"]["url"], output, params=params)
        if not r.ok:
            print(r.text)
        print(r.content)


if __name__ == '__main__':
    main()
