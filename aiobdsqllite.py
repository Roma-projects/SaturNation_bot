import aiosqlite


async def calculate_bonus(refcount):
    if refcount >= 1000:
        return 3
    elif refcount >= 800:
        return 2.5
    elif refcount >= 600:
        return 2
    elif refcount >= 300:
        return 0.9
    elif refcount >= 150:
        return 0.7
    elif refcount >= 100:
        return 0.6
    elif refcount >= 80:
        return 0.4
    elif refcount >= 40:
        return 0.35
    elif refcount >= 20:
        return 0.2
    elif refcount >= 10:
        return 0.1
    else:
        return 0


class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    async def connect(self):
        return await aiosqlite.connect(self.db_name)

    async def user_not_exists(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            async with db.execute('SELECT * FROM Users WHERE id = ?', (user_id,)) as cursor:
                ans = await cursor.fetchall()
                return len(ans) == 0

    async def add_user(self, user_id, referrer_id=None, refcount=0, minelvl0=0, balance_num=0, balance_usdt_num=0):
        async with aiosqlite.connect(self.db_name) as db:
            if referrer_id is not None:
                await db.execute(
                    "INSERT INTO Users ('id', 'referrerid', 'refcount', 'minelvl', 'balance', 'balance_usdt') "
                    "VALUES (?,?,?,?,?,?)",
                    (user_id, referrer_id, refcount, minelvl0, balance_num, balance_usdt_num)
                )
            else:
                await db.execute(
                    "INSERT INTO Users ('id','refcount', 'minelvl', 'balance', 'balance_usdt') VALUES (?,?,?,?,?)",
                    (user_id, refcount, minelvl0, balance_num, balance_usdt_num)
                )
            await db.commit()

    async def ref_counter(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute("SELECT COUNT(`id`) FROM Users WHERE `referrerid` = ?", (user_id,))
            ref_count = await cursor.fetchone()
            ref_count = ref_count[0] if ref_count is not None else 0
            await db.execute("UPDATE Users SET `refcount` = ? WHERE `id` = ?", (ref_count, user_id))
            await db.commit()
            return ref_count

    async def is_wallet_connected(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute("SELECT `address` FROM Users WHERE `id` = ?", (user_id,))
            address = await cursor.fetchone()
            if address is not None:
                address = address[0]
                return bool(address)
            else:
                return False

    async def save_wallet_address_check(self, user_id, wallet_address):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT * FROM Users WHERE address = ?', (wallet_address,))
            result = await cursor.fetchall()
            if not result:
                await db.execute("INSERT INTO Users (id, address) VALUES (?, ?)", (user_id, wallet_address))
                await db.commit()
                return True
            else:
                return False

    async def save_wallet_address(self, user_id, wallet_address):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE Users SET address = ? WHERE id = ?', (wallet_address, user_id))
            await db.commit()

    async def get_wallet_address(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT `address` FROM Users WHERE `id` = ?', (user_id,))
            wallet_address = await cursor.fetchone()
            return wallet_address[0] if wallet_address else 'Адрес кошелька не найден.'

    async def get_mine_lvl(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT `minelvl` FROM Users WHERE `id` = ?', (user_id,))
            lvl = await cursor.fetchone()
            return lvl[0]

    async def update_saturn_balance(self, user_id, saturn_balance=0):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE Users SET `balance` = ? WHERE `id` = ?', (saturn_balance, user_id))
            await db.commit()

    async def update_saturn_balance_in_usdt(self, user_id, saturn_balance_usdt=0):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE Users SET `balance_usdt` = ? WHERE `id` = ?', (saturn_balance_usdt, user_id))
            await db.commit()

    async def get_global_part(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT `Global_part` FROM Users WHERE `id` = ?', (user_id,))
            g_part = await cursor.fetchone()
            return g_part[0]

    async def get_local_part(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('SELECT `Local_part` FROM Users WHERE `id` = ?', (user_id,))
            l_part = await cursor.fetchone()
            return l_part[0]

    async def update_user_levels(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute("SELECT id, balance_usdt, refcount FROM Users")
            users = await cursor.fetchall()

            for user_id, balance_usdt, refcount in users:
                lvl = 0
                if balance_usdt >= 1000 and refcount >= 40:
                    lvl = 10
                elif balance_usdt >= 100 and refcount >= 25:
                    lvl = 9
                elif balance_usdt >= 80 and refcount >= 20:
                    lvl = 8
                elif balance_usdt >= 60 and refcount >= 15:
                    lvl = 7
                elif balance_usdt >= 40 and refcount >= 10:
                    lvl = 6
                elif balance_usdt >= 30 and refcount >= 8:
                    lvl = 5
                elif balance_usdt >= 20 and refcount >= 6:
                    lvl = 4
                elif balance_usdt >= 10 and refcount >= 4:
                    lvl = 3
                elif balance_usdt >= 5 and refcount >= 2:
                    lvl = 2
                elif balance_usdt >= 1:
                    lvl = 1
                await db.execute("UPDATE Users SET minelvl = ? WHERE id = ?", (lvl, user_id))
            await db.commit()

    async def update_global_part(self):
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute("SELECT id, refcount FROM Users WHERE minelvl > 0")
            users = await cursor.fetchall()
            users_list = list(users)
            total_bonus = sum([await calculate_bonus(user[1]) for user in users_list])
            base_part = (100 - total_bonus) / len(users_list) if users_list else 0
            for user in users_list:
                user_id, refcount = user
                bonus = await calculate_bonus(refcount)
                global_part = base_part + bonus
                await db.execute("UPDATE Users SET Global_part = ? WHERE id = ?", (global_part, user_id))
            await db.commit()

    async def update_or_check_status(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            sts = await db.execute('SELECT `Status` FROM Users WHERE `id` = ?', (user_id,))
            status = await sts.fetchone()
            new_status = 0
            if status[0] == 1:
                new_status = 1
            await db.execute('UPDATE Users SET `Status` = ? WHERE `id` = ?', (new_status, user_id))
            await db.commit()
            return new_status

    async def get_status(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            status_coroutine = await db.execute('SELECT `Status` FROM Users WHERE `id` = ?', (user_id,))
            status_result = await status_coroutine.fetchone()
            return status_result[0]

    async def update_local_part(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            result = await db.execute('SELECT `minelvl`,`Local_part` FROM Users WHERE `id` = ?', (user_id,))
            result = await result.fetchall()
            if result:
                (minelvl, local_part), = result
            else:
                raise ValueError(f"No user found with id {user_id}")
            minelvl_to_addition = {
                1: 0.068681,
                2: 0.078493,
                3: 0.137363,
                4: 0.183150,
                5: 0.274725,
                6: 0.329670,
                7: 0.412087,
                8: 0.549450,
                9: 0.824175,
                10: 3
            }
            addition = minelvl_to_addition.get(minelvl, 0)
            new_local_part = min(local_part + addition, 100)
            await db.execute("UPDATE Users SET `Local_part` = ? WHERE `id` = ?", (new_local_part, user_id))
            await db.commit()

    async def update_to_zero_status(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            new_status = 0
            await db.execute('UPDATE Users SET `Status` = ? WHERE `id` = ?', (new_status, user_id))
            await db.commit()

    async def get_saturn_balance(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            balance = await db.execute('SELECT `balance` FROM Users WHERE `id` = ?', (user_id,))
            balance = await balance.fetchone()
            return balance[0]

    async def check_user_rank(self, user_id):
        async with aiosqlite.connect(self.db_name) as db:
            top_users = await db.execute("""
                SELECT id, balance
                FROM Users
                ORDER BY balance DESC
                LIMIT 50
            """)
            top_users = await top_users.fetchall()
            user_ranks = {user[0]: rank + 1 for rank, user in enumerate(top_users)}
            user_rank = user_ranks.get(user_id, None)
            return user_rank if user_rank else "You're not in the top 50"

    async def update_to_true_status(self):
        new_status = 1
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE Users SET `Status` = ?', (new_status,))
            await db.commit()

    async def update_to_true_status_one(self, user_id):
        new_status = 1
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE Users SET `Status` = ? WHERE `id` = ?', (new_status, user_id))
            await db.commit()

    async def update_start_loc_p(self, user_id):
        new_local_part = 0
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute("UPDATE Users SET Local_part = ? WHERE id = ?", (new_local_part, user_id))
            await db.commit()
