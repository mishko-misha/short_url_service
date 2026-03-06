import datetime
import random
import string


class Shortener:
    @staticmethod
    async def create_short_url(urls_collection, long_url: str, user_id: int = None):
        available_chars = string.ascii_letters + string.digits

        short_url = ''.join(random.choices(available_chars, k=7))
        while await urls_collection.find_one({"short_url": short_url}) is not None:
            short_url = ''.join(random.choices(available_chars, k=7))

        final_document = {"short_url": short_url, "long_url": long_url, "clicks": 0,
                          "created_at": datetime.datetime.now(), "user_id": user_id}

        await urls_collection.insert_one(final_document)

        return short_url
