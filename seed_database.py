
import os
import sys
import random

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models.db_config import DatabaseManager, get_db_session
from backend.models.database import TravelContent, ContentTypeEnum


def seed_data():
    """Populate the database with sample travel content."""
    
    sample_destinations = [
        {
            "content_id": "dest_001",
            "title": "Goa, India",
            "description": "A paradise for beach lovers with a vibrant nightlife.",
            "location": "Goa, India",
            "tags": ["beach", "party", "relaxation"],
            "price_min": 20000,
            "price_max": 80000,
            "rating": 4.5,
            "primary_image_url": "https://example.com/goa.jpg"
        },
        {
            "content_id": "dest_002",
            "title": "Jaipur, India",
            "description": "The Pink City, known for its stunning forts and palaces.",
            "location": "Jaipur, Rajasthan, India",
            "tags": ["history", "culture", "architecture"],
            "price_min": 15000,
            "price_max": 60000,
            "rating": 4.7,
            "primary_image_url": "https://example.com/jaipur.jpg"
        }
    ]
    
    sample_accommodations = [
        {
            "content_id": "acc_001",
            "title": "Taj Exotica Resort & Spa, Goa",
            "description": "A luxurious beachfront resort with a private beach and spa.",
            "location": "Goa, India",
            "tags": ["luxury", "beachfront", "spa"],
            "price_min": 15000,
            "price_max": 30000,
            "rating": 4.8,
            "primary_image_url": "https://example.com/taj_goa.jpg"
        },
        {
            "content_id": "acc_002",
            "title": "The Oberoi Rajvilas, Jaipur",
            "description": "A stunning fort-style hotel with beautiful gardens and a pool.",
            "location": "Jaipur, Rajasthan, India",
            "tags": ["luxury", "heritage", "pool"],
            "price_min": 25000,
            "price_max": 50000,
            "rating": 4.9,
            "primary_image_url": "https://example.com/oberoi_jaipur.jpg"
        }
    ]
    
    sample_activities = [
        {
            "content_id": "act_001",
            "title": "Scuba Diving in Goa",
            "description": "Explore the vibrant underwater world of the Arabian Sea.",
            "location": "Goa, India",
            "tags": ["adventure", "water sports", "scuba diving"],
            "price_min": 3000,
            "price_max": 8000,
            "rating": 4.6,
            "primary_image_url": "https://example.com/scuba_goa.jpg"
        },
        {
            "content_id": "act_002",
            "title": "Hot Air Balloon Ride in Jaipur",
            "description": "Get a bird's-eye view of the Pink City and its surroundings.",
            "location": "Jaipur, Rajasthan, India",
            "tags": ["adventure", "scenic", "hot air balloon"],
            "price_min": 8000,
            "price_max": 15000,
            "rating": 4.8,
            "primary_image_url": "https://example.com/balloon_jaipur.jpg"
        }
    ]

    with get_db_session() as db:
        # Clear existing content
        db.query(TravelContent).delete()
        db.commit()
        print("Cleared existing travel content.")

        for dest_data in sample_destinations:
            content = TravelContent(
                content_id=dest_data["content_id"],
                content_type=ContentTypeEnum.DESTINATION,
                title=dest_data["title"],
                description=dest_data["description"],
                location=dest_data["location"],
                tags=dest_data["tags"],
                price_min=dest_data["price_min"],
                price_max=dest_data["price_max"],
                rating=dest_data["rating"],
                primary_image_url=dest_data["primary_image_url"],
                popularity_score=random.uniform(70, 95)
            )
            db.add(content)

        for acc_data in sample_accommodations:
            content = TravelContent(
                content_id=acc_data["content_id"],
                content_type=ContentTypeEnum.ACCOMMODATION,
                title=acc_data["title"],
                description=acc_data["description"],
                location=acc_data["location"],
                tags=acc_data["tags"],
                price_min=acc_data["price_min"],
                price_max=acc_data["price_max"],
                rating=acc_data["rating"],
                primary_image_url=acc_data["primary_image_url"],
                popularity_score=random.uniform(70, 95)
            )
            db.add(content)

        for act_data in sample_activities:
            content = TravelContent(
                content_id=act_data["content_id"],
                content_type=ContentTypeEnum.ACTIVITY,
                title=act_data["title"],
                description=act_data["description"],
                location=act_data["location"],
                tags=act_data["tags"],
                price_min=act_data["price_min"],
                price_max=act_data["price_max"],
                rating=act_data["rating"],
                primary_image_url=act_data["primary_image_url"],
                popularity_score=random.uniform(70, 95)
            )
            db.add(content)

        db.commit()
        print("Successfully seeded the database with sample travel content.")

if __name__ == "__main__":
    DatabaseManager.init_db()
    seed_data()
