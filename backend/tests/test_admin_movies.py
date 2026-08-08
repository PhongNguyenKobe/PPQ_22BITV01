import unittest

from pydantic import ValidationError

from app.schemas.admin import MovieDraftPayload


class AdminMoviePayloadTests(unittest.TestCase):
    def test_normalizes_manual_movie_text_and_genres(self):
        payload = MovieDraftPayload(
            title="  Phim thử nghiệm  ",
            duration_min=120,
            genres=[" Hành động ", "Hành động"],
        )
        self.assertEqual(payload.title, "Phim thử nghiệm")
        self.assertEqual(payload.genres, ["Hành động"])

    def test_rejects_unrealistic_duration(self):
        with self.assertRaises(ValidationError):
            MovieDraftPayload(title="Phim quá dài", duration_min=601, genres=["Kỳ ảo"])


if __name__ == "__main__":
    unittest.main()
