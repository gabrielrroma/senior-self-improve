import unittest

from services.progress_service import (
    build_weekly_stats,
    sync_achievements,
    sync_weekly_goal_bonus,
)


class ProgressServiceTest(unittest.TestCase):
    def test_builds_weekly_stats_from_history_and_archived_tasks(self):
        history = [
            {
                "date": "2026-06-29",
                "completed_tasks": 2,
                "total_tasks": 3,
                "points_earned": 30,
                "completion_percentage": 66,
            },
            {
                "date": "2026-06-30",
                "completed_tasks": 1,
                "total_tasks": 1,
                "points_earned": 20,
                "completion_percentage": 100,
            },
        ]
        archived_days = [
            {
                "date": "2026-06-29",
                "tasks": [
                    {"id": "a", "done": True, "category": "Saude", "completed_at": "2026-06-29"},
                    {"id": "b", "done": True, "category": "Estudos", "completed_at": "2026-06-29"},
                ],
            }
        ]
        tasks = [
            {"id": "c", "done": True, "category": "Saude", "completed_at": "2026-06-30"},
        ]
        gamification = {
            "weekly_goal_tasks": 3,
            "weekly_goal_bonus_points": 50,
            "weekly_goal_awards": [],
        }

        stats = build_weekly_stats(history, archived_days, tasks, "2026-06-30", gamification)

        self.assertEqual(stats["week_start"], "2026-06-29")
        self.assertEqual(stats["week_end"], "2026-07-05")
        self.assertEqual(stats["completed_tasks"], 3)
        self.assertEqual(stats["points_earned"], 50)
        self.assertEqual(stats["completion_percentage"], 75)
        self.assertEqual(stats["top_category"]["name"], "Saude")
        self.assertTrue(stats["goal_complete"])

    def test_weekly_bonus_is_awarded_once_and_revoked_when_goal_drops(self):
        gamification = {"weekly_goal_awards": []}
        complete_stats = {
            "week_start": "2026-06-29",
            "goal_complete": True,
            "bonus_points": 50,
        }

        points, changed, messages = sync_weekly_goal_bonus(
            gamification, complete_stats, "2026-06-30", 20
        )

        self.assertTrue(changed)
        self.assertEqual(points, 70)
        self.assertEqual(len(gamification["weekly_goal_awards"]), 1)
        self.assertIn("Meta semanal concluida", messages[0])

        points, changed, _ = sync_weekly_goal_bonus(gamification, complete_stats, "2026-06-30", points)

        self.assertFalse(changed)
        self.assertEqual(points, 70)

        incomplete_stats = {
            "week_start": "2026-06-29",
            "goal_complete": False,
            "bonus_points": 50,
        }
        points, changed, messages = sync_weekly_goal_bonus(
            gamification, incomplete_stats, "2026-06-30", points
        )

        self.assertTrue(changed)
        self.assertEqual(points, 20)
        self.assertEqual(gamification["weekly_goal_awards"], [])
        self.assertIn("Bonus semanal removido", messages[0])

    def test_syncs_phase_five_achievements(self):
        week_dates = [
            "2026-06-22",
            "2026-06-23",
            "2026-06-24",
            "2026-06-25",
            "2026-06-26",
            "2026-06-27",
            "2026-06-28",
        ]
        history = [
            {
                "date": week_dates[0],
                "completed_tasks": 94,
                "total_tasks": 94,
                "points_earned": 400,
                "completion_percentage": 100,
            },
            *[
                {
                    "date": entry_date,
                    "completed_tasks": 1,
                    "total_tasks": 1,
                    "points_earned": 20,
                    "completion_percentage": 100,
                }
                for entry_date in week_dates[1:]
            ],
        ]
        gamification = {
            "best_streak": 7,
            "streak_count": 0,
            "unlocked_achievements": [],
        }

        changed, messages = sync_achievements(gamification, history, 500, "2026-06-28", 7)

        unlocked_ids = {achievement["id"] for achievement in gamification["unlocked_achievements"]}
        self.assertTrue(changed)
        self.assertEqual(len(messages), 5)
        self.assertEqual(
            unlocked_ids,
            {
                "first_task_completed",
                "seven_day_streak",
                "hundred_tasks_completed",
                "first_perfect_week",
                "five_hundred_points",
            },
        )


if __name__ == "__main__":
    unittest.main()
