"""
Deterministic data generation using Faker.
All test sites use seed=42 for reproducibility.
"""
import os
from typing import List, Dict, Any
from faker import Faker


class DataGenerator:
    """
    Base data generator for test sites.
    Override generate_all() method for site-specific data.
    """

    def __init__(self, seed: int = 42):
        """Initialize Faker with seed for deterministic data."""
        self.fake = Faker()
        Faker.seed(seed)
        self.seed = seed
        self.data_size = int(os.getenv("DATA_SIZE", "100"))

    def generate_all(self) -> List[Dict[str, Any]]:
        """
        Generate all site data.
        Override this method in site-specific implementations.
        """
        # Default: Generate generic items
        return [
            {
                "id": i,
                "name": self.fake.name(),
                "email": self.fake.email(),
                "description": self.fake.text(max_nb_chars=200),
                "created_at": self.fake.date_time_this_year().isoformat(),
                "updated_at": self.fake.date_time_this_month().isoformat()
            }
            for i in range(1, self.data_size + 1)
        ]

    def generate_users(self, count: int) -> List[Dict[str, Any]]:
        """Generate user data."""
        return [
            {
                "id": i,
                "username": self.fake.user_name(),
                "email": self.fake.email(),
                "full_name": self.fake.name(),
                "phone": self.fake.phone_number(),
                "address": {
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "state": self.fake.state(),
                    "zip": self.fake.zipcode(),
                    "country": self.fake.country()
                },
                "created_at": self.fake.date_time_this_year().isoformat(),
                "is_active": self.fake.boolean(chance_of_getting_true=80)
            }
            for i in range(1, count + 1)
        ]

    def generate_posts(self, count: int) -> List[Dict[str, Any]]:
        """Generate blog/social post data."""
        return [
            {
                "id": i,
                "title": self.fake.sentence(nb_words=6),
                "content": self.fake.text(max_nb_chars=1000),
                "author_id": self.fake.random_int(min=1, max=50),
                "created_at": self.fake.date_time_this_year().isoformat(),
                "updated_at": self.fake.date_time_this_month().isoformat(),
                "views": self.fake.random_int(min=0, max=10000),
                "likes": self.fake.random_int(min=0, max=1000),
                "published": self.fake.boolean(chance_of_getting_true=90)
            }
            for i in range(1, count + 1)
        ]

    def generate_products(self, count: int) -> List[Dict[str, Any]]:
        """Generate e-commerce product data."""
        categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Toys"]
        return [
            {
                "id": i,
                "name": self.fake.catch_phrase(),
                "description": self.fake.text(max_nb_chars=500),
                "price": round(self.fake.random.uniform(9.99, 999.99), 2),
                "category": self.fake.random_element(elements=categories),
                "sku": self.fake.bothify(text='???-#####'),
                "stock": self.fake.random_int(min=0, max=500),
                "rating": round(self.fake.random.uniform(1.0, 5.0), 1),
                "reviews_count": self.fake.random_int(min=0, max=1000),
                "created_at": self.fake.date_time_this_year().isoformat()
            }
            for i in range(1, count + 1)
        ]

    def generate_comments(self, count: int, post_count: int) -> List[Dict[str, Any]]:
        """Generate comment data."""
        return [
            {
                "id": i,
                "post_id": self.fake.random_int(min=1, max=post_count),
                "user_id": self.fake.random_int(min=1, max=100),
                "content": self.fake.text(max_nb_chars=300),
                "created_at": self.fake.date_time_this_year().isoformat(),
                "likes": self.fake.random_int(min=0, max=100)
            }
            for i in range(1, count + 1)
        ]

    def generate_companies(self, count: int) -> List[Dict[str, Any]]:
        """Generate company data."""
        return [
            {
                "id": i,
                "name": self.fake.company(),
                "description": self.fake.catch_phrase(),
                "industry": self.fake.bs(),
                "website": self.fake.url(),
                "email": self.fake.company_email(),
                "phone": self.fake.phone_number(),
                "address": {
                    "street": self.fake.street_address(),
                    "city": self.fake.city(),
                    "state": self.fake.state(),
                    "zip": self.fake.zipcode()
                },
                "founded": self.fake.date_between(start_date='-30y', end_date='today').isoformat(),
                "employees": self.fake.random_int(min=10, max=10000)
            }
            for i in range(1, count + 1)
        ]
