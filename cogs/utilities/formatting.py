import typing


def format_points(points: typing.Optional[float]) -> str:
    if points is None:
        return '0'

    return "{:,}".format(points).rstrip("0").rstrip(".")
