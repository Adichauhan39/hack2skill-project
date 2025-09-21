from collections import Counter
from typing import List, Dict, Any

from base_agent import BaseAgent
# from backend.models import Group, UserSwipeProfile

class GroupAgent(BaseAgent):
    """
    An agent that analyzes group preferences to find consensus on destinations,
    accommodations, and activities.
    """

    def execute(self, group_id: int, member_swipes: Dict[int, List[Dict]]) -> Dict[str, Any]:
        """
        Calculates the best options for a group based on collective swipes.

        Args:
            group_id: The ID of the group.
            member_swipes: A dictionary where keys are user_ids and values are lists
                           of their swipe data.
                           e.g., {user_1: [{'item_id': 1, 'liked': True}, ...], user_2: [...]}

        Returns:
            A dictionary containing consensus results, including top-ranked items
            and a consensus score.
        """
        if not member_swipes:
            return {"error": "No member swipe data provided."}

        all_liked_items = [
            item for swipes in member_swipes.values() for item in swipes if item.get('liked')
        ]

        if not all_liked_items:
            return {"message": "No items have been liked by the group yet.", "top_items": []}

        like_counts = Counter(item['item_id'] for item in all_liked_items)

        # In a real app, you'd fetch full item details from your database.
        # We build a complete map of all items from all members' swipes to avoid losing
        # details for items that might only appear in one user's list.
        all_items_in_swipes = (item for swipes in member_swipes.values() for item in swipes)
        all_items_db = {item['item_id']: item for item in all_items_in_swipes}

        sorted_items = sorted(like_counts.items(), key=lambda x: x[1], reverse=True)

        top_items = []
        total_members = len(member_swipes)
        for item_id, count in sorted_items:
            item_details = all_items_db.get(item_id, {})
            top_items.append({
                "item_id": item_id,
                "name": item_details.get("name", f"Item {item_id}"),
                "category": item_details.get("category"),
                "likes": count,
                "approval_score_percent": round((count / total_members) * 100, 2)
            })

        return {"group_id": group_id, "total_members": total_members, "top_items": top_items}