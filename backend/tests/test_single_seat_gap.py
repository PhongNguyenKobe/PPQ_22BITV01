from unittest import TestCase
from uuid import UUID

from app.crud.booking import leaves_new_single_seat_gap


def seat_id(number: int) -> UUID:
    return UUID(int=number)


def row_seats(numbers: list[int], row: str = "A") -> list[tuple[UUID, str, int]]:
    return [(seat_id(number), row, number) for number in numbers]


class SingleSeatGapTests(TestCase):
    def test_rejects_single_gap_created_at_row_edge(self):
        seats = row_seats([1, 2, 3, 4])

        self.assertTrue(
            leaves_new_single_seat_gap(seats, set(), {seat_id(2), seat_id(3), seat_id(4)})
        )

    def test_rejects_single_gap_between_unavailable_seats(self):
        seats = row_seats([1, 2, 3, 4, 5])

        self.assertTrue(
            leaves_new_single_seat_gap(
                seats,
                {seat_id(1)},
                {seat_id(3), seat_id(4), seat_id(5)},
            )
        )

    def test_allows_contiguous_remaining_group(self):
        seats = row_seats([1, 2, 3, 4, 5])

        self.assertFalse(
            leaves_new_single_seat_gap(seats, set(), {seat_id(3), seat_id(4), seat_id(5)})
        )

    def test_allows_booking_elsewhere_when_single_gap_already_exists(self):
        seats = row_seats([1, 2, 3, 4, 5, 6])

        self.assertFalse(
            leaves_new_single_seat_gap(
                seats,
                {seat_id(2)},
                {seat_id(5), seat_id(6)},
            )
        )

    def test_numbering_gap_is_treated_as_an_aisle(self):
        seats = row_seats([1, 2, 5, 6, 7])

        self.assertFalse(
            leaves_new_single_seat_gap(seats, set(), {seat_id(1), seat_id(2)})
        )
