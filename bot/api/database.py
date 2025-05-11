# (c) @Jisin0
import os
import re

from pymongo import MongoClient

DB_NAME = os.environ.get("DB_NAME", "Cluster0")
DB_URI = os.environ.get("DB_URI")


class Database:

    def __init__(self):

        cluster = MongoClient(DB_URI)
        db = cluster[DB_NAME]
        self.bcol = db["ClonedBots"]
        self.main = db["Main"]
        self.fcol = db["Filter_Collection"]
        self.owner = 6004928770

    async def add_user(self, botid, userid):
        self.bcol.update_one(
            {'_id': botid},
            {'$addToSet': {'users': userid}}
        )

        self.bcol.aggregate([
    { "$addFields": { "usercount": { "$size": "$users" } } },
    { "$out": "ClonedBots" }])

    async def set_bot_settings(self, botid, key, value):
        self.bcol.update_one(
            {'_id': botid},
            {'$set': {key: value}}
        )
    async def get_bot_setting(self, botid, key, default=None):
        doc:dict = self.bcol.find_one(
            {'_id': botid},
            {key: 1}
        )
        if doc:
            return doc.get(key, default)
        else:
            return default

    async def get_all_users(self, botid):

        users = self.bcol.find_one(
            {'_id': botid},
            {'users': 1}
        ).get('users',[])

        return users

    async def get_admins(self, botid):

        admins = self.bcol.find_one(
            {'_id': botid},
            {'admins': 1}
        ).get('admins',[])

        admins.append(self.owner)

        return admins

    async def search_media(self, query, max_results):

        if ' ' in query:
            query = query.replace(' ', r'.*[\s\.\+\-_]')
        pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        regex = re.compile(pattern, flags=re.IGNORECASE)

        results: list = self.fcol.find({'file_name': regex})

        if not results :
            return False
        else:
            results = list(results)
            
        results.reverse()

        return results[:max_results]
    
    async def get_config(self, group_id: int):
        """
        A funtion to fetch a group's settings
        """

        connections = self.main.find_one({'_id': group_id})
        
        if connections:

            return connections
        else: 
            return self.new_chat(None, None, None)

    def new_chat(self, group_id, channel_id, channel_name):
        """
        Create a document in db if the chat is new
        """
        try:
            group_id, channel_id = int(group_id), int(channel_id)
        except:
            pass
        
        return dict(
            _id = group_id,
            chat_ids = [{
                "chat_id": channel_id,
                "chat_name": channel_name
                }],
            types = dict(
                audio=False,
                document=True,
                video=True
            ),
            fsub=False,
            configs = dict(
                accuracy=0.70,
                max_pages=20,
                max_results=50,
                max_per_page=10,
                pm_fchat=True,
                show_invite_link=True
            )
        )

    async def get_file(self, unique_id: str):
        """
        A Funtion to get a specific files using its
        unique id
        """
        file = self.fcol.find_one({"unique_id": unique_id})
        file_id = None
        file_type = None
        file_name = None
        file_caption = None
        copy_message_id = None
        
        if file:
            file_id = file.get("file_id")
            file_name = file.get("file_name")
            file_type = file.get("file_type")
            file_caption = file.get("file_caption")
            copy_message_id = file.get("copy_message_id")
        return file_id, file_name, file_caption, file_type, copy_message_id

    async def get_autofilter_settings(self, botid):

        res = self.bcol.find_one(
            {'_id': botid},
            {
            '_id': 1,
            'btemp': 1,
            'result_template': 1
            }
        )
        return res
        
    async def finished_request(self, botid):
        self.bcol.update_one(
            {'_id': botid},
            {'$inc': {'requests': 1}}
        )
    
    async def get_bot_stats(self, botid):
        doc:dict = self.bcol.find_one(
            {'_id': botid},
            {
            'start_photo': 1,
            'start_text': 1,
            'requests': 1,
            'usercount': 1,
            'username': 1,
            'created': 1,
            'active': 1
            }
        )
        return doc

    async def update_copy_id(self, unique_id, chat_id, message_id):
        self.fcol.update_one(
            {"unique_id": unique_id},
            {'$set': {
                "copy_chat_id": chat_id,
                "copy_message_id": message_id
            }}
        )
