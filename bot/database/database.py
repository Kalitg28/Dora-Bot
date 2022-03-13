# (c) @MrPurple902

import os
import re
import motor.motor_asyncio
from pymongo.cursor import Cursor # pylint: disable=import-error
from bot import DB_URI
import random
import string

import pymongo
from pymongo import MongoClient
from pymongo.collection import InsertOneResult

DB_NAME = os.environ.get("DB_NAME", "Adv_Auto_Filter")
FSUB = {}

cluster = MongoClient(DB_URI)
db = cluster[DB_NAME]
ucol = db["Users"]
mcol = db["Manual_Filters"]
ccol = db["Connections"]
main = db["Main"]
fcol = db["Filter_Collection"]

def_config = dict(
                accuracy=0.70,
                max_pages=20,
                max_results=50,
                max_per_page=10,
                pm_fchat=True,
                show_invite_link=True,
                fsub=False
            )

class Database:

    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.db = self._client[DB_NAME]
        self.col = self.db["Main"]
        self.acol = self.db["Active_Chats"]
        self.fcol = self.db["Filter_Collection"]
        
        self.acache = {}
        self.fcache = {}
        self.ucache = {}


    async def create_index(self):
        """
        Create text index if not in db
        """
        await self.fcol.create_index([("file_name", "text")])


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


    async def status(self, group_id: int):
        """
        Get the total filters, total connected
        chats and total active chats of a chat
        """
        group_id = int(group_id)
        
        total_filter = await self.tf_count(group_id)
        
        chats = await self.find_chat(group_id)
        chats = chats.get("chat_ids")
        total_chats = len(chats) if chats is not None else 0
        
        achats = await self.find_active(group_id)
        if achats not in (None, False):
            achats = achats.get("chats")
            if achats == None:
                achats = []
        else:
            achats = []
        total_achats = len(achats)
        
        return total_filter, total_chats, total_achats


    async def find_group_id(self, channel_id: int):
        """
        Find all group id which is connected to a channel 
        for add a new files to db
        """
        data:dict = self.col.find({})
        group_list = []

        for group_id in await data.to_list(length=50): # No Need Of Even 50
            grp_data = group_id.get("chat_ids", None)
            if not grp_data : return None
            for y in group_id["chat_ids"]:
                if int(y["chat_id"]) == int(channel_id):
                    group_list.append(group_id["_id"])
                else:
                    continue
        return group_list

    # Related TO Finding Channel(s)
    async def find_chat(self, group_id: int):
        """
        A funtion to fetch a group's settings
        """

        connections = await self.col.find_one({'_id': group_id})
        
        if connections:

            return connections
        else: 
            return self.new_chat(None, None, None)

        
    async def add_chat(self, group_id: int, channel_id: int, channel_name):
        """
        A funtion to add/update a chat document when a new chat is connected
        """
        new = self.new_chat(group_id, channel_id, channel_name)
        update_d = {"$push" : {"chat_ids" : {"chat_id": channel_id, "chat_name" : channel_name}}}
        prev = await self.col.find_one({'_id':group_id})
        
        if prev:
            await self.col.update_one({'_id':group_id}, update_d)
            await self.update_active(group_id, channel_id, channel_name)
            
            return True
        
        
        await self.col.insert_one(new)
        await self.add_active(group_id, channel_id, channel_name)
        
        return True


    async def del_chat(self, group_id: int, channel_id: int):
        """
        A Funtion to delete a channel and its files from db of a chat connection
        """
        group_id, channel_id = int(group_id), int(channel_id) # group_id and channel_id Didnt type casted to int for some reason
        
        prev = self.col.find_one({"_id": group_id})
        
        if prev:
            
            await self.col.update_one(
                {"_id": group_id}, 
                    {"$pull" : 
                        {"chat_ids" : 
                            {"chat_id":
                                channel_id
                            }
                        }
                    }
            )

            await self.del_active(group_id, channel_id)

            return True

        return False


    async def in_db(self, group_id: int, channel_id: int):
        """
        Check whether if the given channel id is in db or not...
        """
        
        connections = await self.col.find_one({'_id': group_id})
        
        check_list = []
        
        if connections:
            for x in connections["chat_ids"]:
                check_list.append(int(x.get("chat_id")))

            if int(channel_id) in check_list:
                return True
        
        return False


    async def update_settings(self, group_id: int, settings):
        """
        A Funtion to update a chat's filter types in db
        """
        group_id = int(group_id)
        prev = await self.col.find_one({"_id": group_id})
        
        if prev:
            try:
                await self.col.update_one({"_id": group_id}, {"$set": {"types": settings}})
                return True
            
            except Exception as e:
                print (e)
                return False

        print("You Should First Connect To A Chat To Use This Funtion..... 'databse.py/#201' ")
        return False


    async def update_configs(self, group_id: int, configs):
        """
        A Funtion to update a chat's configs in db
        """
        prev = await self.col.find_one({"_id": group_id})

        if prev:
            try:
                await self.col.update_one(prev, {"$set":{"configs": configs}})
                return True

            except Exception as e:
                print (e)
                return False
                
        else :
            try :
                await self.col.insert_one({"_id": group_id, "configs": configs})
                return True

            except Exception as e:
                print (e)
                return False

        print("You Should First Connect To A Chat To Use This")
        return False


    async def delete_all(self, group_id: int):
        """
        A Funtion to delete all documents related to a
        chat from db
        """
        prev = await self.col.find_one({"_id": group_id})
        if prev:
            await self.delall_active(group_id)
            await self.delall_filters(group_id)
            await self.del_main(group_id)
            
        return


    async def del_main(self, group_id: int):
        """
        A Funtion To Delete the chat's main db document
        """
        await self.col.delete_one({"_id": group_id})
        
        return True



    # Related To Finding Active Channel(s)
    async def add_active(self, group_id: int, channel_id: int, channel_name):
        """
        A Funtion to add a channel as an active chat the a connected group 
        (This Funtion will be used only if its the first time)
        """
        templ = {"_id": group_id, "chats":[{"chat_id": channel_id, "chat_name": channel_name}]}
        
        try:
            await self.acol.insert_one(templ)
            await self.refresh_acache(group_id)
        except Exception as e:
            print(e)
            return False
        
        return True


    async def del_active(self, group_id: int, channel_id: int):
        """
        A funtion to delete a channel from active chat colletion in db
        """
        templ = {"$pull": {"chats": dict(chat_id = channel_id)}}
        
        try:
            await self.acol.update_one({"_id": group_id}, templ)
        except Exception as e:
            print(e)
            pass
        
        await self.refresh_acache(group_id)
        return True


    async def update_active(self, group_id: int, channel_id: int, channel_name):
        """
        A Funtion to add a new active chat to the connected group
        """
        group_id, channel_id = int(group_id), int(channel_id)
        
        prev = await self.acol.find_one({"_id": group_id})
        templ = {"$push" : {"chats" : dict(chat_id = channel_id, chat_name = channel_name)}}
        in_c = await self.in_active(group_id, channel_id)
        
        if prev:
            if not in_c:
                await self.acol.update_one({"_id": group_id}, templ)
            else:
                return False
        else:
            await self.add_active(group_id, channel_id, channel_name)
        return True


    async def find_active(self, group_id: int):
        """
        A Funtion to find all active chats of
        a group from db
        """
        if self.acache.get(str(group_id)):
            self.acache.get(str(group_id))
        
        connection = await self.acol.find_one({"_id": group_id})

        if connection:
            return connection
        return False


    async def in_active(self, group_id: int, channel_id: int):
        """
        A Funtion to check if a chat id is in the active
        chat id list in db
        """
        prev = await self.acol.find_one({"_id": group_id})
        
        if prev:
            for x in prev["chats"]:
                if x["chat_id"] == channel_id:
                    return True
            
            return False
        
        return False


    async def delall_active(self, group_id: int):
        """
        A Funtion to Delete all active chats of 
        a group from db
        """
        await self.acol.delete_one({"_id":int(group_id)})
        await self.refresh_acache(group_id)
        return


    async def refresh_acache(self, group_id: int):
        """
        A Funtion to refresh a active chat's chase data
        in case of update in db
        """
        if self.acache.get(str(group_id)):
            self.acache.pop(str(group_id))
        
        prev = await self.acol.find_one({"_id": group_id})
        
        if prev:
            self.acache[str(group_id)] = prev
        return True

    # Related To Finding Filter(s)
    async def add_filters(self, data):
        """
        A Funtion to add document as
        a bulk to db
        """
        try:
            await self.fcol.insert_many(data)
        except Exception as e:
            print(e)
        
        return True

    async def add_filters_reverse(self, data):
        """
        A Funtion to add document as
        a bulk in reverse to db
        """
        try:
            await self.fcol.insert_many(data, upsert=True)
        except Exception as e:
            print(e)
            await self.fcol.insert_many(data)
        
        return True


    async def del_filters(self, group_id: int, channel_id: int):
        """
        A Funtion to delete all filters of a specific
        chat and group from db
        """
        group_id, channel_id = int(group_id), int(channel_id)
        
        try:
            await self.fcol.delete_many({"chat_id": channel_id, "group_id": group_id})
            print(await self.cf_count(group_id, channel_id))
            return True
        except Exception as e:
            print(e) 
            return False


    async def delall_filters(self, group_id: int):
        """
        A Funtion To delete all filters of a group
        """
        await self.fcol.delete_many({"group_id": int(group_id)})
        return True


    async def get_filters(self, group_id: int, keyword: str):
        """
        A Funtion to fetch all similar results for a keyowrd
        from using text index
        """
        await self.create_index()

        chat = await self.find_chat(group_id)
        chat_accuracy = float(chat["configs"].get("accuracy", 0.70))
        achats = await self.find_active(group_id)
        
        achat_ids=[]
        if not achats:
            return False
        
        for chats in achats["chats"]:
            achat_ids.append(chats.get("chat_id"))
        
        filters = []
                
        pipeline= {
            'group_id': int(group_id), '$text':{'$search': keyword}
        }
        
        
        db_list = self.fcol.find(
            pipeline, 
            {'score': {'$meta':'textScore'}} # Makes A New Filed With Match Score In Each Document
        )

        db_list.sort([("score", {'$meta': 'textScore'})]) # Sort all document on the basics of the score field
        
        for document in await db_list.to_list(length=600):
            if document["score"] < chat_accuracy:
                continue
            
            if document["chat_id"] in achat_ids:
                filters.append(document)
            else:
                continue

        return filters


    async def get_file(self, unique_id: str):
        """
        A Funtion to get a specific files using its
        unique id
        """
        file = await self.fcol.find_one({"unique_id": unique_id})
        file_id = None
        file_type = None
        file_name = None
        file_caption = None
        
        if file:
            file_id = file.get("file_id")
            file_name = file.get("file_name")
            file_type = file.get("file_type")
            file_caption = file.get("file_caption")
        return file_id, file_name, file_caption, file_type


    async def cf_count(self, group_id: int, channel_id: int):
        """
        A Funtion To count number of filter in channel
        w.r.t the connect group
        """
        return await self.fcol.count_documents({"chat_id": channel_id, "group_id": group_id})
    
    
    async def tf_count(self, group_id: int):
        """
        A Funtion to count total filters of a group
        """
        return await self.fcol.count_documents({"group_id": group_id})

    async def user_count(self):
        """
        A Function To Count The Total Number Of Users Of The Bot
        """

        return await ucol.find().count()


    async def get_conn(self, user_id):

        try:
            cached = self.ucache.get(str(user_id))

            if  cached:

                return cached

            else :

                conn = ccol.find_one({"_id": user_id})
                conn = conn.get('chat')

                if not conn :

                    return False

                else :
                    self.ucache[str(user_id)] = conn
                    return conn

        except AttributeError :

            return False

        except Exception as e :

            print(e)
            return False
    
    async def conn_user(self, user_id: int, group_id: int):

        try:
                if ccol.find_one({"_id": user_id}):
                    ccol.delete_one({"_id": user_id})
                ccol.insert_one({"_id": user_id,'chat': group_id})
                if self.ucache.get(str(user_id)):
                    self.ucache.pop(str(user_id))
                self.ucache[str(user_id)] = group_id
                return True

        except Exception as e:
            print(e)
            return False

    async def del_conn(self, user_id):

        try :
             ccol.delete_one({"_id": user_id})
        except Exception as e :
            return False

        if self.ucache.get(str(user_id)):

            self.ucache.pop(str(user_id))
        return True

        return True

    async def all_connected(self):
        return ccol.find()

    async def add_mfilter(self, id, group_id, text, content, file, buttons, alert, sticker: bool, edits) :

        check = mcol.find_one({"group_id": group_id, "text": text})

        if check:
            
            mcol.delete_one({"_id": check["_id"]})

        try :

            unique_id = id
            length = len(text)

            document = {
                "_id": unique_id,
                "group_id": group_id,
                "text": text,
                "content": content,
                "file": file,
                "buttons": str(buttons),
                "alert": alert,
                "sticker": sticker,
                "edits": edits,
                "length": length
            }

            mcol.insert_one(document)
            self.fcache[unique_id] = alert

        except Exception as e:
            print(e)
        
    async def find_mfilter(self, group_id, query):
      try :

        filters:Cursor = mcol.aggregate([{'$match':{"group_id": group_id}},
        {'$sort': {"length": -1}}])
        if filters :

            for filter in filters:

                pattern = r"( |^|[^\w])" + filter["text"] + r"( |$|[^\w])"
                result = re.search(pattern, query, flags=re.IGNORECASE)
                self.fcache[filter["_id"]] = filter["alert"]

                if result :

                    content = filter["content"]
                    file_id = filter["file"]
                    buttons = filter["buttons"]
                    sticker = filter["sticker"]

                    return {"content":content, "file_id":file_id, "buttons":buttons, "sticker":bool(sticker)}

            return False

                

        else : return False
      except Exception as e :
          print(e)

    async def del_mfilter(self, group_id, text):

        check = mcol.find_one({"group_id": group_id, "text": text})

        if check :

            mcol.delete_one({"_id": check["_id"]})
            return True

        else :
            return False

    async def all_mfilter(self, chat_id):

        filters = []

        try :

            results = mcol.aggregate([{'$match':{"group_id": chat_id}},{'$project': {
            "text": 1,
            "field_length": { '$strLenCP': "$text" }
        }},
        {'$sort': {"field_length": 1}},
        {'$project': {"field_length": 0}}])

            if results:

                for result in results:

                    print(result)
                    filters.append(result["text"])
                    self.fcache[result["_id"]] = result.get("alert")

                return filters

            else :

                return False

        except Exception as e :
            print(e)
            return False

    async def add_user(self, user_id):

        if not ucol.find_one({"_id": user_id}) :
            ucol.insert_one({"_id": user_id})

    async def get_alert(self, id, index):

        try:
            alert = self.fcache.get(id)
            if alert :
                return alert[int(index)]
            alert = mcol.find_one({"_id": id}).get("alert")
            if not alert:
                return False
            else :
                return alert[int(index)]
        except Exception as e:
            print(e)

    async def get_edit(self, id, index):

        result = mcol.find_one({'_id': id})
        if result:
            doc = result['edits'][index]
            return doc['text'], doc['buttons']
        else :
            return False, False

    async def set_fsub(self, group_id, channel_id, title):

        try :
            doc = {'id': channel_id, 'title': title}
            prev = main.find_one({'_id':group_id})
            if prev:
                main.update_one({'_id': group_id}, {'$set':{'fsub': doc}})
            else :
                main.insert_one(
                    {
                        "_id": group_id,
                        'configs': def_config,
                        'fsub': doc
                    }
                )

        except Exception as e :
            print(e)

    async def del_fsub(self, group_id):

        try :
            main.update_one({'_id': group_id}, {'$set':{'fsub': False}})


        except Exception as e :
            print(e)

    async def set_main(self, id, key, value):

        try:
            if main.find_one({'_id': id}):
                main.update_one({'_id': id}, {'$set':{key: value}})
            else :
                main.insert_one(
                   { '_id': id,
                    'configs': def_config,
                    key: value}
                )
        except Exception as e :
            print(e)

    async def del_main(self, id, key):

        try:
            main.update_one({'_id': id}, {'$set':{key: False}})

        except Exception as e :
            print(e)
        
    async def all_users(self):

        try:
            result = ucol.find()
            return result
        except Exception as e:
            print(e)

    async def get_stats(self):

        try:
            files = fcol.find().count()
            users = ucol.find().count()
            filters = mcol.find().count()
            used = db.__sizeof__()
            chats = main.find().count()
            con_users = ccol.find().count()

            result = {'files': files,
            'users': users,
            'filters': filters,
            'used': used,
            'chats': chats,
            "conn": con_users}
            print(result)
            return result
            
        except Exception as e:
            print(e)

    async def del_filter(link):

        doc = fcol.find_one_and_delete({"file_link": link})
        print(doc)

    async def search_media(self, query, max_results):

        if ' ' in query:
            query = query.replace(' ', r'.*[\s\.\+\-_]')
        pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
        regex = re.compile(pattern, flags=re.IGNORECASE)

        results: list = fcol.find({'file_name': regex})

        if not results :
            return False
        else:
            results = list(results)
            
        results.reverse()

        return results[:max_results]

    async def get_mfilter(self, id):

        filter = fcol.find_one({'_id': id})
        return filter

    async def clear_predvd(self):

        pattern = re.compile(r'predvd|camrip|hdts|hdcam|cam', re.IGNORECASE)
        cleared = fcol.delete_many({'file_name': pattern})
        return cleared.deleted_count

    async def del_file(self, file_id: str):

        return fcol.delete_one({'file_id': file_id})


def getLen(e):

        return(len(e["text"]))

    