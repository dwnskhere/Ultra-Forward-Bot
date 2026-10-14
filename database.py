# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper



from os import environ 
import uuid
from config import Config
import motor.motor_asyncio
from pymongo import MongoClient, ReturnDocument

async def mongodb_version():
    x = MongoClient(Config.DB_URL)
    mongodb_version = x.server_info()['version']
    return mongodb_version

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.bot = self.db.bots
        self.col = self.db.users
        self.nfy = self.db.notify
        self.chl = self.db.channels
        # Per-process owner token used by forwarding-task leases.
        self.worker_id = uuid.uuid4().hex
        
    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )
      
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_bots_count(self):
        bcount = await self.bot.count_documents({})
        count = await self.col.count_documents({})
        return count, bcount

    async def total_channels(self):
        count = await self.chl.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})
 
    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        b_users = [user['id'] async for user in users]
        return b_users

    async def update_configs(self, id, configs):
        await self.col.update_one({'id': int(id)}, {'$set': {'configs': configs}})
         
    async def get_configs(self, id):
        default = {
            'caption': None,
            'duplicate': True,
            'forward_tag': False,
            'file_size': 0,
            'size_limit': None,
            'extension': None,
            'keywords': None,
            'protect': None,
            'button': None,
            'db_uri': None,
            'filters': {
               'poll': True,
               'text': True,
               'audio': True,
               'voice': True,
               'video': True,
               'photo': True,
               'document': True,
               'animation': True,
               'sticker': True
            }
        }
        user = await self.col.find_one({'id':int(id)})
        if user:
            return user.get('configs', default)
        return default 
       
    async def add_bot(self, datas):
       if not await self.is_bot_exist(datas['user_id']):
          await self.bot.insert_one(datas)
    
    async def remove_bot(self, user_id):
       await self.bot.delete_many({'user_id': int(user_id)})
      
    async def get_bot(self, user_id: int):
       bot = await self.bot.find_one({'user_id': user_id})
       return bot if bot else None
                                          
    async def is_bot_exist(self, user_id):
       bot = await self.bot.find_one({'user_id': user_id})
       return bool(bot)
                                          
    async def in_channel(self, user_id: int, chat_id: int) -> bool:
       channel = await self.chl.find_one({"user_id": int(user_id), "chat_id": int(chat_id)})
       return bool(channel)
    
    async def add_channel(self, user_id: int, chat_id: int, title, username):
       channel = await self.in_channel(user_id, chat_id)
       if channel:
         return False
       return await self.chl.insert_one({"user_id": user_id, "chat_id": chat_id, "title": title, "username": username})
    
    async def remove_channel(self, user_id: int, chat_id: int):
       channel = await self.in_channel(user_id, chat_id )
       if not channel:
         return False
       return await self.chl.delete_many({"user_id": int(user_id), "chat_id": int(chat_id)})
    
    async def get_channel_details(self, user_id: int, chat_id: int):
       return await self.chl.find_one({"user_id": int(user_id), "chat_id": int(chat_id)})
       
    async def get_user_channels(self, user_id: int):
       channels = self.chl.find({"user_id": int(user_id)})
       return [channel async for channel in channels]
     
    async def get_filters(self, user_id):
       filters = []
       filter = (await self.get_configs(user_id))['filters']
       for k, v in filter.items():
          if v == False:
            filters.append(str(k))
       return filters
              
    async def add_frwd(self, user_id):
       return await self.nfy.insert_one({'user_id': int(user_id)})
    
    async def rmve_frwd(self, user_id=0, all=False):
       data = {} if all else {'user_id': int(user_id)}
       return await self.nfy.delete_many(data)
    
    async def get_all_frwd(self):
       return self.nfy.find({})
     
    # Durable forwarding task ledger. The legacy notify collection is only
    # for restart notices and must never be treated as task progress.
    @property
    def forwarding_tasks(self):
        return self.db.forwarding_tasks

    @property
    def forwarding_message_outcomes(self):
        return self.db.forwarding_message_outcomes

    async def ensure_forwarding_indexes(self):
        await self.forwarding_tasks.create_index("task_id", unique=True)
        await self.forwarding_tasks.create_index([("status", 1), ("updated_at", 1)])
        await self.forwarding_tasks.create_index([("status", 1), ("lease_expires_at", 1)])
        await self.forwarding_tasks.create_index([("owner_id", 1), ("created_at", -1)])
        await self.forwarding_message_outcomes.create_index(
            [("task_id", 1), ("source_message_id", 1)], unique=True
        )
        await self.forwarding_message_outcomes.create_index(
            [("task_id", 1), ("outcome", 1), ("source_message_id", -1)]
        )

    async def create_forwarding_task(self, task):
        """Create a durable task envelope before the first source message is processed."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        payload = dict(task)
        initial_cursor = int(payload.get("start_message_id", payload.get("skip", 0)) or 0)
        payload.update({
            "status": "running",
            "created_at": now,
            "updated_at": now,
            "heartbeat_at": now,
            "lease_owner": self.worker_id,
            "lease_expires_at": now + timedelta(seconds=180),
            "cursor_message_id": initial_cursor,
            "last_confirmed_message_id": initial_cursor,
            "counts": {"processed": 0, "forwarded": 0, "skipped": 0, "failed": 0},
            "attempt": 0,
        })
        await self.forwarding_tasks.update_one(
            {"task_id": str(payload["task_id"])}, {"$setOnInsert": payload}, upsert=True
        )
        return await self.forwarding_tasks.find_one({"task_id": str(payload["task_id"])})

    async def claim_forwarding_task(self, task_id):
        """Atomically claim an existing task when no other live lease owns it."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        query = {
            "task_id": str(task_id),
            "$or": [
                {"status": "interrupted"},
                {"status": "running", "lease_owner": self.worker_id},
                {"status": "running", "lease_expires_at": {"$lte": now}},
                {"status": "running", "lease_expires_at": {"$exists": False}},
                {"status": "recovering", "lease_expires_at": {"$lte": now}},
                {"status": "recovering", "lease_expires_at": {"$exists": False}},
            ],
        }
        claimed = await self.forwarding_tasks.find_one_and_update(
            query,
            {"$set": {
                "status": "running",
                "lease_owner": self.worker_id,
                "lease_expires_at": now + timedelta(seconds=180),
                "heartbeat_at": now,
                "updated_at": now,
            }},
            return_document=ReturnDocument.AFTER,
        )
        return claimed

    async def claim_next_recoverable_task(self, excluded_owner_ids=None):
        """Claim one interrupted task or one running task whose lease has expired."""

        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        query = {
            "$and": [
                {"attempt": {"$lt": 5}},
                {"$or": [
                    {"status": "interrupted"},
                    {"status": "recovering", "$or": [
                        {"lease_expires_at": {"$lte": now}},
                        {"lease_expires_at": {"$exists": False}},
                    ]},
                    {"status": "running", "lease_expires_at": {"$lte": now}},
                    {"status": "running", "lease_expires_at": {"$exists": False}},
                ]},
                {"$or": [
                    {"retry_after": {"$lte": now}},
                    {"retry_after": {"$exists": False}},
                ]},
            ]
        }
        excluded_owner_ids = [int(owner_id) for owner_id in (excluded_owner_ids or [])]
        if excluded_owner_ids:
            query["owner_id"] = {"$nin": excluded_owner_ids}
        return await self.forwarding_tasks.find_one_and_update(
            query,
            {"$set": {
                "status": "running",
                "lease_owner": self.worker_id,
                "lease_expires_at": now + timedelta(seconds=180),
                "heartbeat_at": now,
                "updated_at": now,
            }, "$inc": {"attempt": 1},
             "$unset": {"retry_after": ""}},
            sort=[("updated_at", 1)],
            return_document=ReturnDocument.AFTER,
        )

    async def defer_forwarding_task(self, task_id, delay_seconds=15):
        """Release a claimed task without charging a retry when its owner is busy."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        return await self.forwarding_tasks.update_one(
            {"task_id": str(task_id), "lease_owner": self.worker_id},
            {"$set": {
                "status": "interrupted",
                "retry_after": now + timedelta(seconds=max(1, int(delay_seconds))),
                "updated_at": now,
                "heartbeat_at": now,
            },
             "$inc": {"attempt": -1},
             "$unset": {"lease_owner": "", "lease_expires_at": ""}},
        )

    async def heartbeat_owned_tasks(self):
        """Renew all leases currently owned by this process."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        return await self.forwarding_tasks.update_many(
            {"status": "running", "lease_owner": self.worker_id},
            {"$set": {
                "heartbeat_at": now,
                "lease_expires_at": now + timedelta(seconds=180),
                "updated_at": now,
            }},
        )

    async def checkpoint_forwarding_message(self, task_id, source_message_id, outcome, error=None):
        """Persist one terminal outcome; duplicate writes never increment counters twice."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)
        message_id = int(source_message_id)
        key = {"task_id": str(task_id), "source_message_id": message_id}
        try:
            await self.forwarding_message_outcomes.insert_one({
                **key,
                "outcome": outcome,
                "error": str(error)[:1000] if error else None,
                "created_at": now,
            })
        except Exception as exc:
            # If the outcome insert succeeded just before a crash but its cursor
            # update did not, replaying this checkpoint repairs the cursor without
            # incrementing outcome counters twice.
            if getattr(exc, "code", None) == 11000:
                await self.forwarding_tasks.update_one(
                    {"task_id": str(task_id), "lease_owner": self.worker_id},
                    {"$max": {
                        "cursor_message_id": message_id,
                        "last_confirmed_message_id": message_id,
                    },
                     "$set": {
                         "updated_at": now,
                         "heartbeat_at": now,
                         "lease_expires_at": now + timedelta(seconds=180),
                     }},
                )
                return False
            raise

        count_key = (
            "forwarded" if outcome == "forwarded"
            else "failed" if outcome == "failed"
            else "skipped"
        )
        await self.forwarding_tasks.update_one(
            {"task_id": str(task_id), "lease_owner": self.worker_id},
            {"$max": {
                "cursor_message_id": message_id,
                "last_confirmed_message_id": message_id,
            },
             "$inc": {f"counts.{count_key}": 1, "counts.processed": 1},
             "$set": {
                 "updated_at": now,
                 "heartbeat_at": now,
                 "lease_expires_at": now + timedelta(seconds=180),
             }},
        )
        return True

    async def update_forwarding_task(self, task_id, fields):
        from datetime import datetime, timedelta, timezone

        payload = dict(fields)
        now = datetime.now(timezone.utc)
        payload["updated_at"] = now
        payload["heartbeat_at"] = now
        update = {"$set": payload}
        if payload.get("status") not in (None, "running", "recovering"):
            update["$unset"] = {"lease_owner": "", "lease_expires_at": ""}
        elif payload.get("status") in ("running", "recovering"):
            payload["lease_expires_at"] = now + timedelta(seconds=180)
            payload.setdefault("lease_owner", self.worker_id)
        await self.forwarding_tasks.update_one({"task_id": str(task_id)}, update)

    async def get_latest_forwarding_task(self, owner_id):
        return await self.forwarding_tasks.find_one(
            {"owner_id": int(owner_id)}, sort=[("created_at", -1)]
        )

    async def get_forwarding_task(self, task_id):
        return await self.forwarding_tasks.find_one({"task_id": str(task_id)})

    async def get_forwarding_message_outcome(self, task_id, source_message_id):
        return await self.forwarding_message_outcomes.find_one(
            {"task_id": str(task_id), "source_message_id": int(source_message_id)},
            {"_id": 0, "outcome": 1, "error": 1},
        )

    async def get_failed_message_ids(self, task_id, limit=10):
        cursor = self.forwarding_message_outcomes.find(
            {"task_id": str(task_id), "outcome": "failed"},
            {"_id": 0, "source_message_id": 1},
        ).sort("source_message_id", -1).limit(max(1, min(int(limit), 10)))
        return [doc["source_message_id"] async for doc in cursor]

    async def get_forwarding_outcome_counts(self, task_id):
        counts = {"forwarded": 0, "skipped": 0, "failed": 0}
        pipeline = [
            {"$match": {"task_id": str(task_id)}},
            {"$group": {"_id": "$outcome", "count": {"$sum": 1}}},
        ]
        async for row in self.forwarding_message_outcomes.aggregate(pipeline):
            if row["_id"] in counts:
                counts[row["_id"]] = row["count"]
        return counts

    async def get_node_for_task(self, owner_id, node_id):
        return await self.bot.find_one({"user_id": int(owner_id), "id": int(node_id)})

    async def mark_interrupted_forwarding_tasks(self):
        """Mark only tasks with expired/no lease; never interrupt a live worker."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        result = await self.forwarding_tasks.update_many(
            {"status": "running", "$or": [
                {"lease_expires_at": {"$lte": now}},
                {"lease_expires_at": {"$exists": False}},
            ]},
            {"$set": {
                "status": "interrupted",
                "updated_at": now,
                "recovery_note": "Worker lease expired; checkpoint retained for recovery.",
            }, "$unset": {"lease_owner": "", "lease_expires_at": ""}},
        )
        return result.modified_count

db = Database(Config.DB_URL, Config.DB_NAME)








# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper