from uuid import uuid4

from date_utils import today_key, to_int


MIN_REWARD_COST = 1


def normalize_reward_cost(value, default=10):
    return max(MIN_REWARD_COST, to_int(value, default))


def normalize_reward_image_url(value):
    return str(value or "").strip()


def create_reward(title, cost, description="", image_url=""):
    return {
        "id": uuid4().hex,
        "title": title,
        "description": description,
        "image_url": normalize_reward_image_url(image_url),
        "cost": normalize_reward_cost(cost),
        "created_at": today_key(),
    }


def update_reward(reward, title, cost, description="", image_url=""):
    reward["title"] = title
    reward["description"] = description
    reward["image_url"] = normalize_reward_image_url(image_url)
    reward["cost"] = normalize_reward_cost(cost, reward.get("cost", 10))


def find_reward(rewards, reward_id):
    for reward in rewards:
        if reward["id"] == reward_id:
            return reward
    return None


def delete_reward(rewards, reward):
    return [item for item in rewards if item["id"] != reward["id"]]


def get_available_points(points_total, points_spent):
    return max(0, to_int(points_total) - to_int(points_spent))


def can_redeem_reward(reward, points_total, points_spent):
    return get_available_points(points_total, points_spent) >= normalize_reward_cost(reward.get("cost"))


def redeem_reward(reward, points_spent):
    cost = normalize_reward_cost(reward.get("cost"))
    redemption = {
        "id": uuid4().hex,
        "reward_id": reward["id"],
        "reward_title": reward["title"],
        "cost": cost,
        "redeemed_at": today_key(),
    }
    return to_int(points_spent) + cost, redemption


def sort_rewards(rewards):
    return sorted(rewards, key=lambda reward: (normalize_reward_cost(reward.get("cost")), reward["title"].lower()))


def sort_redemptions(redemptions):
    return sorted(redemptions, key=lambda redemption: redemption["redeemed_at"], reverse=True)
