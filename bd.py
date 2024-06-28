import sqlite3


def calculate_bonus(refcount):
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
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def user_not_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,)).fetchall()
            if len(result) == 0:
                return True
            else:
                return False

    def add_user(self, user_id, referrer_id=None, refcount=0, minelvl0=0):
        with self.connection:
            if referrer_id is not None:
                return self.cursor.execute("INSERT INTO Users ('id', 'referrerid', 'refcount', 'minelvl') VALUES (?,?,?,?)", (user_id, referrer_id, refcount, minelvl0))
            else:
                return self.cursor.execute("INSERT INTO Users ('id','refcount', 'minelvl') VALUES (?,?,?)", (user_id, refcount, minelvl0))

    def ref_counter(self, user_id):
        with self.connection:
            a = self.cursor.execute(" SELECT COUNT(`id`) FROM Users WHERE `referrerid` = ?", (user_id,)).fetchone()[0]
            self.cursor.execute(" UPDATE Users SET `refcount` = ? WHERE `id` = ?", (a, user_id))
            return a

    def is_wallet_connected(self, user_id):
        with self.connection:
            res = self.cursor.execute("SELECT `address` FROM Users WHERE `id` = ?", (user_id,)).fetchone()[0]
            return bool(res)

    def save_wallet_address_check(self, user_id, wallet_address):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM Users WHERE address = ?', (wallet_address,)).fetchall()
            if len(result) == 0:
                self.cursor.execute("INSERT INTO Users (id, address) VALUES (?, ?)", (user_id, wallet_address))
                return True
            else:
                return False

    def save_wallet_address(self, user_id, wallet_address):
        with self.connection:
            return self.cursor.execute('UPDATE Users SET address = ? WHERE id = ?', (wallet_address, user_id))

    def get_wallet_address(self, user_id):
        with self.connection:
            wallet_address = self.cursor.execute('SELECT `address` FROM Users WHERE `id` = ?', (user_id,)).fetchone()
            if wallet_address:
                return wallet_address[0]
            else:
                return 'Адрес кошелька не найден.'

    def get_mine_lvl(self, user_id):
        with self.connection:
            lvl = self.cursor.execute('SELECT `minelvl` FROM Users WHERE `id` = ?', (user_id,)).fetchone()[0]
            return lvl

    def update_saturn_balance(self, user_id, saturn_balance=0):
        with self.connection:
            return self.cursor.execute('UPDATE Users SET `balance` = ? WHERE `id` = ?', (saturn_balance, user_id))

    def update_saturn_balance_in_usdt(self, user_id, saturn_balance_usdt=0):
        with self.connection:
            return self.cursor.execute('UPDATE Users SET `balance_usdt` = ? WHERE `id` = ?', (saturn_balance_usdt, user_id))

    def get_global_part(self, user_id):
        with self.connection:
            g_part = self.cursor.execute('SELECT `Global_part` FROM Users WHERE `id` = ?', (user_id,)).fetchone()[0]
            return g_part

    def get_local_part(self, user_id):
        with self.connection:
            l_part = self.cursor.execute('SELECT `Local_part` FROM Users WHERE `id` = ?', (user_id,)).fetchone()[0]
            return l_part

    def update_user_levels(self):
        with self.connection:
            users = self.cursor.execute("SELECT id, balance_usdt, refcount FROM Users").fetchall()
            for user in users:
                id, balance_usdt, refcount = user
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
                self.cursor.execute("UPDATE Users SET minelvl = ? WHERE id = ?", (lvl, id))

    def update_global_part(self):
        with self.connection:
            users = self.cursor.execute("SELECT id, refcount FROM Users WHERE minelvl > 0").fetchall()

            total_bonus = sum(calculate_bonus(user[1]) for user in users)

            base_part = (100 - total_bonus) / len(users) if users else 0

            for user in users:
                id, refcount = user
                bonus = calculate_bonus(refcount)

                global_part = base_part + bonus
                self.cursor.execute("UPDATE Users SET Global_part = ? WHERE id = ?", (global_part, id))

    def update_or_check_status(self, user_id):
        with self.connection:
            sts = self.cursor.execute('SELECT `Status` FROM Users WHERE `id` = ?', (user_id,)).fetchone()[0]
            new_status = 0
            if sts == 1:
                new_status = 1
            self.cursor.execute('UPDATE Users SET `Status` = ? WHERE `id` = ?', (new_status, user_id))
            return new_status

    def get_status(self, user_id):
        with self.connection:
            return self.cursor.execute('SELECT `Status` FROM Users WHERE `id` = ?', (user_id,)).fetchone()[0]

    def update_local_part(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT `minelvl`,`Local_part` FROM Users WHERE `id` = ?',
                                         (user_id,)).fetchall()
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
            return self.cursor.execute("UPDATE Users SET Local_part = ? WHERE id = ?", (new_local_part, user_id))

    def update_to_zero_status(self, user_id):
        with self.connection:
            new_status = 0
            return self.cursor.execute('UPDATE Users SET `Status` = ? WHERE `id` = ?', (new_status, user_id))

    def get_saturn_balance(self, user_id):
        with self.connection:
            balance = self.cursor.execute('SELECT `balance` FROM Users WHERE `id` = ?', (user_id,)).fetchone()[0]
            return balance

    def check_user_rank(self, user_id):
        top_users = self.cursor.execute("""
            SELECT id, balance
            FROM Users
            ORDER BY balance DESC
            LIMIT 50
        """).fetchall()

        user_ranks = {user[0]: rank + 1 for rank, user in enumerate(top_users)}
        user_rank = user_ranks.get(user_id, None)
        if user_rank:
            return user_rank
        else:
            return "Ты не входишь в топ 50"

    def update_to_true_status(self):
        with self.connection:
            new_status = 1
            return self.cursor.execute('UPDATE Users SET `Status` = ?', (new_status,))

    def update_to_true_status_one(self, user_id):
        with self.connection:
            new_status = 1
            return self.cursor.execute('UPDATE Users SET `Status` = ? WHERE `id` = ?', (new_status, user_id))

    def update_start_loc_p(self, user_id):
        with self.connection:
            new_local_part = 0
            return self.cursor.execute("UPDATE Users SET Local_part = ? WHERE id = ?", (new_local_part, user_id))


