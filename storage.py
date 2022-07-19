import pymongo
from constants import ALLOWED_FILTERS as ITERABLE_FILTERS
import config


class RSSFeed:
    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url

    def __str__(self) -> str:
        return f"[{self.name}]: {self.url}"

    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url
        }


class JobPostDB:
    def __init__(self) -> None:
        self.db_client = pymongo.MongoClient(config.db_connection)
        self.db = self.db_client[config.db_name]
        self.jobs = self.db["job_posts"]
        if "job_posts" not in self.db.list_collection_names():
            self._init_db()
            print("created collection")

    def _init_db(self):
        dummy = {
            "job_id": "1",
            "user_id": 1
        }
        self.jobs.insert_one(dummy)

    def job_exits(self, job_id, user_id):
        job = self.jobs.find_one({
            "job_id": job_id,
            "user_id": user_id
        })

        return job is not None

    def insert_job(self, job_id, user_id):
        self.jobs.insert_one({
            "job_id": job_id,
            "user_id": user_id
        })


class UsersDB:
    def __init__(self) -> None:
        self.db_client = pymongo.MongoClient(config.db_connection)
        self.db = self.db_client[config.db_name]
        self.users = self.db["users"]
        if "users" not in self.db.list_collection_names():
            self._init_db()
            print("created collection")

    def _init_db(self):
        dummy = {
            "rss": [],
            "settings": {},
            "filters": {},
            "state":1,
            "id": 1
        }
        self.users.insert_one(dummy)

    def get_all_users(self):
        for document in self.users.find():
            yield document

    def get_user(self, user_id):
        user = self.users.find_one({
            "id": user_id
        })
        if user is not None:
            return user
        self.users.insert_one(
            {
                "id": user_id,
                "state": 1,
                "rss": [],
                "settings": {
                    "chat": user_id,
                    "show_summary": "NO",
                    'timezone': 'UTC'
                },
                "filters": {
                    "exclude_countries": [],
                    "add_skills": [],
                }
            }
        )
        return self.users.find_one({
            "id": user_id
        })

    def _update_user(self, user_id, updated_user):
        self.users.find_one_and_replace(
            {
                "id": user_id
            },
            updated_user
        )

    def get_user_rss(self, user_id):
        user = self.get_user(user_id)
        return user["rss"]

    def add_user_rss(self, user_id, rss: RSSFeed):
        user = self.get_user(user_id)
        user["rss"].append(rss.to_dict())
        self._update_user(user_id, user)

    def delete_user_rss(self, user_id, rss_name):
        user = self.get_user(user_id)
        user["rss"] = [rss for rss in user["rss"]
                       if rss.get("name") == rss_name]
        self._update_user(user_id, user)

    def get_user_settings(self, user_id):
        user = self.get_user(user_id)
        return user["settings"]

    def set_user_settings(self, user_id, key, value):
        user = self.get_user(user_id)
        user["settings"][key] = value
        self._update_user(user_id, user)

    def get_user_filters(self, user_id):
        user = self.get_user(user_id)
        return user["filters"]

    def set_user_filter(self, user_id, key, value):
        user = self.get_user(user_id)
        if key in ITERABLE_FILTERS and key in user["filters"]:
            user["filters"][key].extend(value)
            user["filters"][key] = list(set(user["filters"][key]))
        else:
            user["filters"][key] = list(set(value))
        self._update_user(user_id, user)
        return user["filters"][key]

    def clear_user_filter(self, user_id, key):
        user = self.get_user(user_id)
        if key in user["filters"]:
            user["filters"].pop(key)
        self._update_user(user_id, user)

    def get_user_state(self, user_id):
        user = self.get_user(user_id)
        return user["state"]

    def set_user_state(self, user_id, value):
        user = self.get_user(user_id)
        user["state"] = value
        self._update_user(user_id, user)