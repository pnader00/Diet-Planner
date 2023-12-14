import ast
from datetime import date
import numpy as np
from decimal import Decimal

import food
import sql


class User:
    """class to manange diet planning kcal and nutritions intake"""
    # TODO zmiana parametrow change login w main
    intake_calc = sql.config(filename='database.ini', section='daily_intake_calculator')
    user_db = sql.config(filename='database.ini', section='food_options')

    def __init__(self, connect, login=None, new=False, name=None, password=None, age=None, sex=None,
                 height=None, weight=None, wact=None, pact=None, loss_ratio=None, schedule=None,
                 carbohydrates=None, proteins=None, lipids=None, fiber=None):
        self.connect = connect
        self.new = new
        self.login = login
        self.name = name
        self.password = password
        self.age = age
        self.sex = sex
        self.height = height
        self.weight = weight
        self.wact = wact
        self.pact = pact
        self.loss_ratio = loss_ratio
        self.schedule = schedule
        self.carbohydrates = carbohydrates
        self.proteins = proteins
        self.lipids = lipids
        self.fiber = fiber

    def __str__(self):
        s = f"new: {self.new}\n"\
            f"login: {self.login}\n" \
            f"name: {self.name}\n" \
            f"pswrd: {self.password}\n" \
            f"age: {self.age}\n" \
            f"sex: {self.sex}\n" \
            f"height: {self.height}\n" \
            f"weight: {self.weight}\n"\
            f"wact: {self.wact}\n" \
            f"pact: {self.pact}\n" \
            f"base_intake: {self.base_intake}\n"\
            f"loss ratio: {self.loss_ratio}\n" \
            f"daily_intake: {self.daily_intake}\n"\
            f"schedule: {self.schedule}\n"\
            f"carb = {self.carbohydrates}\n"\
            f"proteins = {self.proteins}\n"\
            f"lipids = {self.lipids}\n"\
            f"fiber = {self.fiber}\n"
        return s

    @property
    def connect(self):
        return self._connect

    @connect.setter
    def connect(self, connect):
        """psycopg sql connect obj"""
        self._connect = connect

    @property
    def new(self):
        """bool, tells if it's new user"""
        return self._new

    @new.setter
    def new(self, new):
        if type(new) is bool:
            self._new = new
        else:
            raise TypeError("New has to be bool type")

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, login):
        # TODO zmiana loginu ???
        if self.new and login is not None:
            i = len(login)
            if 0 >= i or i > 255:
                raise ValueError("Login has to be from 1 to 256 character long")
            if login in self.login_list:
                raise ValueError("Login already exists. Choose another login")
        else:
            if login not in self.login_list and login is not None:
                raise ValueError("Login not valid")

        self._login = login

    @property
    def login_list(self):
        """returns list of logins from users db"""
        q = f"select login from {User.user_db['users']}"
        login_lst = sql.read_query(self.connect, q)
        return [i[0] for i in login_lst]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        try:
            q = f"SELECT user_name FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.name_valid(name):
                self._name = name
            return
        if val_read != name and name is not None:
            if User.name_valid(name):
                self._name = name
        else:
            self._name = val_read

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        try:
            q = f"SELECT user_password FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.pswrd_valid(password):
                self._password = password
            return
        if val_read != password and password is not None:
            if User.pswrd_valid(password):
                self._password = password
        else:
            self._password = val_read

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, age):
        try:
            q = f"SELECT age FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.age_valid(age):
                self._age = age
            return
        if val_read != age and age is not None:
            if User.age_valid(age):
                self._age = age
        else:
            self._age = val_read

    @property
    def sex(self):
        return self._sex

    @sex.setter
    def sex(self, sex):
        try:
            q = f"SELECT sex FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.sex_valid(sex):
                self._sex = sex
            return
        if val_read != sex and sex is not None:
            if User.sex_valid(sex):
                self._sex = sex
        else:
            self._sex = val_read

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        try:
            q = f"SELECT height FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.height_valid(height):
                self._height = height
            return
        if val_read != height and height is not None:
            if User.height_valid(height):
                self._height = height
        else:
            self._height = val_read

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, weight):
        try:
            q = f"SELECT weight FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.weight_valid(weight):
                self._weight = weight
            return
        if val_read != weight and weight is not None:
            if User.weight_valid(weight):
                self._weight = weight
        else:
            self._weight = val_read

    @property
    def wact(self):
        """work activity"""
        return self._wact

    @wact.setter
    def wact(self, wact):
        """work activity level
        wact - int 0 - 3"""
        try:
            q = f"SELECT wact FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.act_valid(wact):
                self._wact = wact
            return
        if val_read != wact and wact is not None:
            if User.act_valid(wact):
                self._wact = wact
        else:
            self._wact = val_read

    @property
    def pact(self):
        """physical activity level"""
        return self._pact

    @pact.setter
    def pact(self, pact):
        """physical activity level
                pact - int 0 - 3"""
        try:
            q = f"SELECT pact FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.act_valid(pact):
                self._pact = pact
            return
        if val_read != pact and pact is not None:
            if User.act_valid(pact):
                self._pact = pact
        else:
            self._pact = val_read

    @property
    def base_intake(self):
        """return daily calories' base_intake calculated with Miffin formula"""
        if self.login is None:
            return None
        if self.sex == 0:
            const = iter(ast.literal_eval(User.intake_calc['miffin'])['female'])
            bmr = (next(const) * self.weight) + (next(const) * self.height) - (next(const) * self.age) - next(const)
        else:
            const = iter(ast.literal_eval(User.intake_calc['miffin'])['male'])
            bmr = (next(const) * self.weight) + (next(const) * self.height) - (next(const) * self.age) + next(const)
        pal = ast.literal_eval(User.intake_calc['activity_matrix'])[self.pact][self.wact]
        return round(bmr * pal)

    @property
    def schedule(self):
        """schedule of meals, dict date  obj: day obj"""
        return self._schedule

    @schedule.setter
    def schedule(self, schedule):
        """creates schedule dict out of input tuple
        schedule - tuple: (list of date objs, list of tuples: (meal_id, amount))"""
        if self.new:
            self._schedule = self.new_schedule(schedule)
        elif self.login is None:
            self._schedule = schedule
        else:
            self._schedule = self.read_schedule()

    @property
    def loss_ratio(self):
        """weight to lose per week in kg"""
        return self._loss_ratio

    @loss_ratio.setter
    def loss_ratio(self, loss_ratio):
        """weight to lose per week in kg"""
        try:
            q = f"SELECT loss_ratio FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            if User.loss_valid(loss_ratio):
                self._loss_ratio = loss_ratio
            return
        if val_read != loss_ratio and loss_ratio is not None:
            if User.loss_valid(loss_ratio):
                self._loss_ratio = loss_ratio
        else:
            self._loss_ratio = val_read

    @property
    def daily_intake(self):
        """daily intake of kcal considering loss_ratio
        kcal deficit per day to lose loss_ratio amount of kilograms per week
        7 - days in week"""
        try:
            cal_loss = (self.loss_ratio * int(User.intake_calc['kcal_burn'])) / 7  # loss of kcal for 1 day
            return self.base_intake - cal_loss
        except TypeError:
            return None

    @property
    def carbohydrates(self):
        """percent of carbohydrates in daily kcal intake"""
        return self._carbohydrates

    @carbohydrates.setter
    def carbohydrates(self, carbohydrates):
        """sets carbohydrates to default value if no value can be read from db"""
        try:
            q = f"SELECT carbohydrates_percent FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            val_read = User.intake_calc["carbohydrates_percent"]
        if val_read != carbohydrates and carbohydrates is not None:
            if User.macro_valid(carbohydrates):
                self._carbohydrates = carbohydrates
        else:
            self._carbohydrates = val_read

    @property
    def proteins(self):
        """percent of proteins in daily kcal intake"""
        return self._proteins

    @proteins.setter
    def proteins(self, proteins):
        """sets proteins to default value if no value can be read from db"""
        try:
            q = f"SELECT protein_percent FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            val_read = User.intake_calc["proteins_percent"]
        if val_read != proteins and proteins is not None:
            if User.macro_valid(proteins):
                self._proteins = proteins
        else:
            self._proteins = val_read

    @property
    def lipids(self):
        """percent of lipids in daily kcal intake"""
        return self._lipids

    @lipids.setter
    def lipids(self, lipids):
        """sets lipids to default value if no value can be read from db"""
        try:
            q = f"SELECT lipid_percent FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            val_read = User.intake_calc["lipid_percent"]
        if val_read != lipids and lipids is not None:
            if User.macro_valid(lipids):
                self._lipids = lipids
        else:
            self._lipids = val_read

    @property
    def fiber(self):
        """mass (g) of fiber in daily intake"""
        return self._fiber

    @fiber.setter
    def fiber(self, fiber):
        """sets fiber to default value if no value can be read from db"""
        try:
            q = f"SELECT fiber_mass FROM {User.user_db['users']} WHERE login = '{self.login}'"
            val_read = sql.read_query(self.connect, q)[0][0]
        except IndexError:
            val_read = User.intake_calc["fiber_mass"]
        if val_read != fiber and fiber is not None:
            if User.fiber_valid(fiber):
                self._fiber = fiber
        else:
            self._fiber = val_read

    def kcal_diff(self, kcal):
        """returns difference calculated daily intake and given kcal intake"""
        return self.daily_intake - kcal

    def balance(self, period, dv=False):
        """add column with % balance of nutrients to day object nutrients dataframe +(nutrients property)
        period: day or week object
        dv - if true add daily reference value of nutrients balance for grown person
             if false add personal balance of nutrients"""
        bal = period.nutrients.copy(deep=True)
        if dv:
            intake = [None, self.base_intake, float(User.intake_calc["proteins_percent"]),
                      float(User.intake_calc["carbohydrates_percent"]), None,
                      float(User.intake_calc["lipid_percent"]), None]
        else:
            intake = [None, self.daily_intake, self.proteins, self.carbohydrates, None, self.lipids, None]
        bal["balance"] = intake

        return bal

    def week_balance(self, week, year=date.today().year, dv=False):
        # TODO error handling for missing days in week
        """add column with % balance of nutrients to week object nutrients dataframe +(nutrients property)
                period: day or week object
                dv - if true add daily reference value of nutrients balance for grown person
                     if false add personal balance of nutrients"""
        dates = [date.fromisocalendar(year, week, day) for day in range(1, 8)]
        days = {d: self.schedule[d] for d in dates}
        bal = self.balance(Week(self.connect, days), dv=dv)
        bal["balance"][1] = bal["balance"][1] * 7
        return bal

    def read_schedule(self):
        """read schedule data from database and return schedule dictionary"""
        q = f"SELECT date_data, meal_id, amount FROM {User.user_db['schedule']} WHERE login = '{self.login}'"
        schedule_read = sql.read_query(self.connect, q)
        sch = {}
        for rec in schedule_read:
            day, meal_id, amount = rec
            if day in sch.keys():
                sch[day].add_meal(meal_id=meal_id, amount=amount)
            else:
                sch[day] = Day(self.connect, [(meal_id, amount)])
        return sch

    def new_schedule(self, schedule):
        """returns dict date object: day object
        schedule - tuple(listo of day objects, list with lists of tuples(meal id, portion) """
        sch = {}
        if schedule is not None:
            days, meals = schedule
            for count, day in enumerate(days):
                sch[day] = Day(self.connect, meals[count])
        return sch

    def add_meal(self, day, meal_id, amount, index=None):
        """add meal to day object in schedule
        day - date object, key in schedule dict
        index - position of the meal in Day.meals obj to insert new meal"""
        if day not in self.schedule:
            self.schedule[day] = Day(self.connect, [(meal_id, amount)])
            return 0
        if index is None:
            index = len(self.schedule[day].meals)
        self.schedule[day].add_meal(meal_id, amount, index)
        return 0

    def replace_meal(self, day, index, meal_id, amount):
        """replace meal to day object in schedule
        day - date object, key in schedule dict
        index - position of the meal in Day.meals obj to replace meal"""
        try:
            self.schedule[day].replace_meal(index, meal_id, amount)
        except KeyError:
            print('No such day in calendar')

    def remove_meal(self, day, index):
        """remove meal to day object in schedule
        day - date object, key in schedule dict
        index - position of the meal in Day.meals obj to remove meal"""
        try:
            self.schedule[day].remove_meal(index)
        except KeyError:
            print('No such day in calendar')

    def remove_day(self, day):
        """remove day from schedule
        day - date obj"""
        try:
            del self.schedule[day]
        except KeyError:
            print('No such day in calendar')

    def update_schedule(self):
        """update schedule in database"""
        if self.schedule is None:
            raise ValueError("Please create schedule before update")

        for date, days in self.schedule.items():
            date_str = date.isoformat()
            # TODO usuwanie punktowe zapisów które się zmieniają
            q = f"DELETE FROM {User.user_db['schedule']} WHERE login = '{self.login}' AND date_data = '{date_str}'"
            sql.execute_query(self.connect, q)
            # print(date_str)
            for meal in days.meals:
                q1 = f"INSERT INTO {User.user_db['schedule']} (login, date_data, meal_id, amount) " \
                    f"VALUES ('{self.login}', '{date_str}', '{meal[0].id}', '{meal[1]}')"
                sql.execute_query(self.connect, q1)

    def update_user(self):
        """update user info in database"""
        q = f"INSERT INTO {User.user_db['users']} (login, user_password, user_name, age, sex, height, weight, " \
            f"wact, pact, intake, loss_ratio, carbohydrates_percent, protein_percent, lipid_percent, fiber_mass)\
        VALUES ('{self.login}', '{self.password}', '{self.name}', '{self.age}', '{self.sex}', '{self.height}'," \
            f"'{self.weight}', '{self.wact}', '{self.pact}', '{self.base_intake}', '{self.loss_ratio}'," \
            f"'{self.carbohydrates}', '{self.proteins}', '{self.lipids}', '{self.fiber}')\
        ON CONFLICT (login)\
        DO\
        UPDATE SET  user_password = EXCLUDED.user_password, user_name = EXCLUDED.user_name," \
            f"age = EXCLUDED.age, sex = EXCLUDED.sex, height = EXCLUDED.height, weight = EXCLUDED.weight," \
            f"wact = EXCLUDED.wact, pact = EXCLUDED.pact, intake = EXCLUDED.intake, loss_ratio = EXCLUDED.loss_ratio," \
            f"carbohydrates_percent = EXCLUDED.carbohydrates_percent, protein_percent = EXCLUDED.protein_percent, " \
            f"lipid_percent = EXCLUDED.lipid_percent, fiber_mass = EXCLUDED.fiber_mass;"
        sql.execute_query(self.connect, q)

    def update(self):
        self.update_user()
        self.update_schedule()

    @staticmethod
    def name_valid(name):
        try:
            if 0 < len(name) <= 255:
                return True
            else:
                raise ValueError("Name has to be from 1 to 256 character long")
        except TypeError:
            return True

    @staticmethod
    def age_valid(age):
        if age is None:
            return True
        if 18 <= age <= 99:
            return True
        raise ValueError('Age has to be between 18 and 99')

    @staticmethod
    def sex_valid(sex):
        if sex in [None, 0, 1]:
            return True
        raise ValueError('Sex should be 0 or 1')

    @staticmethod
    def pswrd_valid(pswrd):
        if pswrd is None:
            return True
        if len(pswrd) < 2:
            return True
        raise ValueError("Password can be maximum 256 char long")

    @staticmethod
    def height_valid(height):
        if height is None:
            return True
        if 0 <= height <= 250:
            return True
        raise ValueError("Height has to be between 0 and 250")

    @staticmethod
    def weight_valid(weight):
        if weight is None:
            return True
        if 0 <= weight <= 250:
            return True
        raise ValueError("Weight has to be between 0 and 250")

    @staticmethod
    def act_valid(act):
        """check if wact or pact is valid input"""
        if act in [None, 0, 1, 2, 3]:
            return True
        raise ValueError("Activity should be in [0, 1, 2, 3]")

    @staticmethod
    def loss_valid(loss):
        if loss is None:
            return True
        if loss >= 0:
            return True
        raise ValueError("Loss ratio has to be >= 0")

    @staticmethod
    def macro_valid(macro):
        if 0 <= macro <= 1:
            return True
        raise ValueError("Macro value has to be between 0 and 1")

    @staticmethod
    def fiber_valid(fiber):
        if fiber >= 0:
            return True
        raise ValueError("Fiber has to be > 0")

    @staticmethod
    def delete_user(connect, login):
        if login not in User(connect).login_list:
            raise ValueError("Login does not exist.")
        q1 = f"DELETE FROM {User.user_db['users']} WHERE login = '{login}'"
        q2 = f"DELETE FROM {User.user_db['schedule']} WHERE login = '{login}'"
        sql.execute_query(connect, q1)
        sql.execute_query(connect, q2)


class Day:
    """manage meals eaten within one day"""
    user_db = sql.config(filename='database.ini', section='food_options')

    def __init__(self, connect, meals):
        """meals - list of tuples (meal_id, amount)"""
        self.connect = connect
        self.meals = meals
        self.nutrients = self.meals

    def __str__(self):
        s = ""
        for m in self.meals:
            meal, amount = m
            s += f"{meal.name}: {amount}g.\n"
        s += self.nutrients.to_string()
        return s

    @property
    def meals(self):
        return self._meals

    @meals.setter
    def meals(self, meals):
        """ returns list of tuples(food obj, portion of meal)
        meals - list of tuples (meal_id, amount)"""
        m = []
        for meal in meals:
            meal_id, amount = meal
            m.append((food.Ingredient(connect=self.connect, id=meal_id), amount))
        self._meals = m

    @property
    def nutrients(self):
        return self._nutrients

    @nutrients.setter
    def nutrients(self, meals):
        """return df with sum of nutrients for all meals"""
        nutrients = None
        for m in meals:
            meal, amount = m
            if nutrients is None:
                nutrients = meal.portion_df(amount)
            else:
                old = nutrients["amount"]
                old.index = nutrients["nutrient_id"]
                nutrients["amount"] = old.add(meal.get_portion(amount)).values

        nutrients["energy_p"] = Day.calculate_energy_percent(nutrients["amount"])
        self._nutrients = nutrients

    @property
    def energy_kcal(self):
        """return daily energy in kcal"""
        id = self.get_nutrient_id('Energy', 'kcal')
        return float(self.nutrients[self.nutrients['nutrient_id'] == id]['amount'].values)

    @property
    def protein(self):
        """return daily proteins in g"""
        id = self.get_nutrient_id('Protein')
        return float(self.nutrients[self.nutrients['nutrient_id'] == id]['amount'].values)

    @property
    def total_lipid(self):
        """return daily lipids in g"""
        id = self.get_nutrient_id('Total lipid (fat)')
        return float(self.nutrients[self.nutrients['nutrient_id'] == id]['amount'].values)

    @property
    def carbohydrates(self):
        """return daily carbohydrates in g"""
        id = self.get_nutrient_id('Carbohydrate, by difference')
        return float(self.nutrients[self.nutrients['nutrient_id'] == id]['amount'].values)

    @property
    def sugars(self):
        """return daily Sugars, total including NLEA in g"""
        id = self.get_nutrient_id('Sugars, total including NLEA')
        return float(self.nutrients[self.nutrients['nutrient_id'] == id]['amount'].values)

    @property
    def fiber(self):
        """return daily fiber in g"""
        id = self.get_nutrient_id('Fiber, total dietary')
        return float(self.nutrients[self.nutrients['nutrient_id'] == id]['amount'].values)

    @staticmethod
    def calculate_energy_percent(amount):
        """ returns percentage energy that comes from each nutrition in form of pandas series
        amount - pd series with weight of each nutrition in daily intake"""
        ratio = [None, None, Decimal(User.intake_calc["proteins_ratio"]),
                 Decimal(User.intake_calc["carbohydrates_ratio"]),
                 None, Decimal(User.intake_calc["lipid_ratio"]), Decimal(User.intake_calc["fiber_ratio"])]

        energy = amount * np.array(ratio)
        e_sum = energy.sum()
        energy = energy / e_sum
        energy = energy.astype(float)
        energy = energy.round(2)
        return energy

    def get_nutrient_id(self, name, unit=None):
        """ get nutrient id from database"""
        q = f"SELECT nutrient_id FROM {Day.user_db['nutr_name_db']} WHERE name = '{name}'"
        if name == 'Energy':
            q += f" and unit = '{unit}'"
        return sql.read_query(self.connect, q)[0][0]

    def add_meal(self, meal_id, amount, index=None):
        """create food obj and add it to self.meals
        index - place on meal list to insert new meal. if None add meal at the end of list"""
        if amount < 0:
            raise ValueError("Amount of food has to be greater than 0")
        if index is None:
            index = len(self.meals)
        self.meals.insert(index, (food.Ingredient(connect=self.connect, id=meal_id), amount))

    def replace_meal(self, index, meal_id, amount):
        """create food obj and replace other meal in self.meals
               index - place on meal list to be replaced by new meal. if None add meal at the end of list"""
        if amount < 0:
            raise ValueError("Amount of food has to be greater than 0")
        try:
            self.meals[index] = (food.Ingredient(connect=self.connect, id=meal_id), amount)
        except IndexError:
            print(f"Index has to be between 0 and {len(self.meals)}")

    def remove_meal(self, index):
        """remove meal from self.meals
               index - place on meal list to be removed."""
        try:
            removed = self.meals.pop(index)
            print(f"{removed[0].name}, {removed[1]}g has been removed. ")
        except IndexError:
            print(f"Index has to be between 0 and {len(self.meals)}")


class Week(Day):
    def __init__(self, connect, days):
        self.connect = connect
        self.meals = days
        self.nutrients = days

    @property
    def meals(self):
        return self._meals

    @meals.setter
    def meals(self, days):
        """days - dict (date: day_obj)"""
        self._meals = days

    @property
    def nutrients(self):
        return self._nutrients

    @nutrients.setter
    def nutrients(self, days):
        """return df with sum of nutrients for all meals"""
        nutrients = None
        for day in days.values():
            if nutrients is None:
                nutrients = day.nutrients
            else:
                old = nutrients["amount"]
                old.index = nutrients["nutrient_id"]
                new = day.nutrients["amount"]
                new.index = nutrients["nutrient_id"]
                nutrients["amount"] = old.add(new).values
        nutrients["energy_p"] = Day.calculate_energy_percent(nutrients["amount"])
        self._nutrients = nutrients


def make_days():
    dates = [date(2023, 10, 2), date(2023, 10, 3), date(2023, 10, 4), date(2023, 10, 5), date(2023, 10, 6),
             date(2023, 10, 7), date(2023, 10, 8)]
    days = [[9749, 8033, 3675, 7606], [185, 8033, 5875, 7606], [9642, 8033, 93601, 7606],
            [9749, 8033, 3675, 7606], [185, 8033, 5875, 7606], [9642, 8033, 93601, 7606],
            [9642, 5875, 93601, 8947]]
    amount = 200
    days = [zip(day, [amount, amount, amount, amount]) for day in days]

    return dates, days


if __name__ == '__main__':
    params = sql.config()
    conn = sql.connect(params)
    try:
        # NEWUSER
        # schedule = make_days()
        # user = User(connect=conn, login="q", new=True, name="sd", password="0", sex=0, age=35, height=188, weight=76,
        #                wact=1, pact=1, loss_ratio=0.5, schedule=None)
        #
        # print(user)

        user = User(connect=conn, login='p')
        # user = User(connect=conn)
        # user.update()
        # l = [date(2023, 10, 2), date(2023, 10, 3)]
        # days = {k: user.schedule[k] for k in l}
        # w = Week(conn, days)
        # print(w.meals)
        print(user.schedule[date(2023, 10, 2)].nutrients)

        # day = user.schedule[date(2023, 10, 2)]
        # print(day.nutrients)
        # balance = user.dv_balance(day)
        # nutrients = day.nutrients

        # print(nutrients[nutrients["nutrient_id"] == 1008]["energy"].values)


        # day = user.schedule[date(2023, 10, 2)]
        # kcal = float(day[day['nutrient_id'] == 1008]['amount'].values)
        # print(user.daily_intake)
        # print(user.schedule[date(2023, 10, 2)].energy_kcal)
        # print(user.kcal_diff(user.schedule[date(2023, 10, 2)].energy_kcal))
        # print(day.protein)
        # print(day.nutrients )

        # day = date(2023, 10, 2)
        # print(day.isocalendar())
        # print(date.fromisocalendar(2023, 40, 1))


        # Check add remove replace:
        # day = date(2023, 10, 3)
        # print('day:')
        # print(user.schedule[day])
        # print("remove")
        # user.remove_meal(day, index=1)
        # print(user.schedule[day])
        # print("replace")
        # user.replace_meal(day, index=1, meal_id=8947, amount=100)
        # print(user.schedule[day])
        # print("add")
        # user.add_meal(day, meal_id=8947, amount=100)
        # print(user.schedule[day])

    finally:
        conn.close()
