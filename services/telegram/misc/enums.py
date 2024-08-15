import enum


class TestStatus(enum.IntEnum):
    on_home = 1
    waiting = 2
    started = 3
    test_ending = 4
    result_sent = 5
    failed = 6
    completed = 7


class Sender(enum.IntEnum):
    user = 0
    admin = 1