import sql
import ast
from random import randint
import pandas as pd


class Food:
    """class for managing database of food and meals"""
    nutr_columns = ['nutrient_id', 'nutrient_name', 'unit', 'amount']
    standard_serving = 100
    db = sql.config(filename='database.ini', section='food_options')

    def __init__(self, connect, id=None):
        self.connect = connect
        self.id = id

    def __str__(self):
        s = f"class: {self.__class__.__name__}\n"\
            f"id: {self.id}, name: {self.name}, category: {self.category}\n"\
            f"nutrients:\n{self.nutrients}\n"\
            f"ingredients: {self.ingredients}\n"

        return s

    @property
    def connect(self):
        """psycopg sql connect obj"""
        return self._connect

    @connect.setter
    def connect(self, connect):
        self._connect = connect

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        if id in self.id_list or id is None:
            self._id = id
        else:
            raise ValueError("Id not valid")

    @property
    def name(self):
        return None

    @property
    def category(self):
        return None

    @property
    def nutrients(self):
        return None

    @property
    def ingredients(self):
        """ingredients of a meal if meal is simple food ingredients are None"""
        return None

    @property
    def id_list(self):
        """returns sorted list of food id from db"""
        q = f"select ndbnumber from {Food.db['info_db']}"
        id_lst = sql.read_query(self.connect, q)
        return sorted([i[0] for i in id_lst])

    @property
    def nutrients_id(self):
        """returns list of base nutrients id from database
        base nutrients - energy, proteins, carbohydrates, lipids, fiber"""
        q = f"SELECT nutrient_id fROM {self.db['nutr_name_db']}"
        i = sql.read_query(self.connect, q)
        return [j[0] for j in i]

    def get_portion(self, serving):
        """returns pd series with nutrients for not standard serving in grams"""
        portion = self.nutrients["amount"].apply(lambda x: round(x * serving / Food.standard_serving, 1))
        portion.index = self.nutrients["nutrient_id"].tolist()
        return portion

    def portion_df(self, serving):
        """returns df with nutritions info for not standard serving"""
        nutr = self.nutrients
        nutr["amount"] = self.get_portion(serving).values
        return nutr

    def get_weight(self):
        """returns summed weight of all ingredients or 0 if there is no ingredients"""
        try:
            return sum(self.ingredients.values())
        except AttributeError:
            return 0

    def get_ingredients(self):
        """returns df with ingredients names and amount"""
        try:
            df = pd.DataFrame(columns=['id', 'name', 'weight'])
            for id, weight in self.ingredients.items():
                q = f"SELECT description FROM {Food.db['info_db']} WHERE ndbnumber = {id}"
                name = sql.read_query(self.connect, q)[0][0]
                df.loc[len(df)] = [id, name, weight]
            return df
        except AttributeError:
            return None

    def _update_info(self):
        """update database with basic information about food """
        q = f"INSERT INTO {Food.db['info_db']} (ndbnumber, description, category, ingredients)\
        VALUES ({self.id}, '{self.name}', '{self.category}', '{self.ingredients}')\
        ON CONFLICT (ndbnumber)\
        DO\
        UPDATE SET description = EXCLUDED.description, category = EXCLUDED.category, ingredients = EXCLUDED.ingredients;"
        sql.execute_query(self.connect, q)

    def _update_nutritions(self):
        """update database with information obout food nutririons"""
        for index, row in self._nutrients.iterrows():
            nutr_id = row['nutrient_id']
            amount = row['amount']
            q = f"select amount from {Food.db['nutr_amount_db']} where ndbnumber = {self.id} and nutrient_id = {nutr_id}"
            record = sql.read_query(self.connect, q)
            if len(record) == 0:
                q1 = f"INSERT INTO {Food.db['nutr_amount_db']} (ndbnumber, nutrient_id, amount) \
                                        VALUES ({self.id}, {nutr_id}, {amount})"
                sql.execute_query(self.connect, q1)
            elif record[0][0] != amount:
                q2 = f"UPDATE {Food.db['nutr_amount_db']} \
                        SET amount = {amount} \
                        WHERE ndbnumber = {self.id} and nutrient_id = {nutr_id}"
                sql.execute_query(self.connect, q2)

    def update_db(self):
        self._update_info()
        self._update_nutritions()

    @staticmethod
    def delete_food(id, connect):
        if id not in Food(connect).id_list:
            raise ValueError("Id does not exist.")
        q1 = f"DELETE FROM {Food.db['info_db']} WHERE ndbnumber = {id}"
        q2 = f"DELETE FROM {Food.db['nutr_amount_db']} WHERE ndbnumber = {id}"

        sql.execute_query(connect, q1)
        sql.execute_query(connect, q2)


class Ingredient(Food):
    """creates Ingredient object from existing fod record from database by food id"""
    def __init__(self, id, connect):
        Food.__init__(self, id=id, connect=connect)

    @property
    def name(self):
        q = f"SELECT description FROM {Food.db['info_db']} WHERE ndbnumber = {self.id}"
        return sql.read_query(self.connect, q)[0][0]

    @property
    def category(self):
        q = f"SELECT category FROM {Food.db['info_db']} WHERE ndbnumber = {self.id}"
        return sql.read_query(self.connect, q)[0][0]

    @property
    def nutrients(self):
        """ returns data frame with basic nutrients for food id """
        q = f"SELECT fn.nutrient_id, nb.name, nb.unit, amount FROM {Food.db['nutr_amount_db']} fn \
                    INNER JOIN {Food.db['nutr_name_db']} nb \
                        ON fn.nutrient_id = nb.nutrient_id \
                    WHERE ndbnumber = {self.id} ORDER BY nb.unit DESC"
        data = sql.read_query(self.connect, q)
        df = pd.DataFrame(data)
        df.columns = Food.nutr_columns
        return df

    @property
    def ingredients(self):
        """returns dictionary of ingredients from db"""
        try:
            q = f"SELECT ingredients FROM {Food.db['info_db']} WHERE ndbnumber = {self.id}"
            return ast.literal_eval(sql.read_query(self.connect, q)[0][0])
        except ValueError:
            return None


class NewIngredient(Food):
    """creates new ingredient"""
    def __init__(self, name, nutrients, category, connect):
        Food.__init__(self, connect=connect)
        self.name = name
        self.category = category
        self.nutrients = nutrients

    @Food.id.setter
    def id(self, *args):
        while True:
            n = randint(0, 9999)
            if n not in self.id_list:
                break
        self._id = n

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        self._category = category

    @property
    def nutrients(self):
        return self._nutrients

    @nutrients.setter
    def nutrients(self, nutrients):
        """returns df with nutrients info
        nutrients - dict nutrient id: amount(g)"""
        try:
            nutr_keys = list(nutrients.keys())
            q = f"SELECT name, unit FROM {Food.db['nutr_name_db']} \
                        WHERE nutrient_id in {"(" + str(nutr_keys)[1:-1] + ")"}"
            data = sql.read_query(self.connect, q)
            res = []
            for count, rec in enumerate(data):
                name, unit = rec
                id = nutr_keys[count]
                res.append((id, name, unit, nutrients[id]))

            df = pd.DataFrame(res)
            df.columns = Food.nutr_columns
            self._nutrients = df
        except AttributeError:
            self._nutrients = None


class NewMeal(NewIngredient):
    """creates new meal from existing ingredients"""
    def __init__(self, name, ingredients, connect, category='Custom Meal'):
        """ingredients - dict ingredients id: amount(g)"""
        self.ingredients = ingredients
        NewIngredient.__init__(self, name=name, nutrients=self.ingredients, category=category, connect=connect)

    @property
    def ingredients(self):
        return self._ingredients

    @ingredients.setter
    def ingredients(self, ingredients):
        self._ingredients = ingredients

    @NewIngredient.nutrients.setter
    def nutrients(self, ingredients):
        """returns nutrition per 100 g of meal input: ingredients dict"""
        total_weight = self.get_weight()
        amount = None
        for id, weight in ingredients.items():
            i = Ingredient(id=id, connect=self.connect)
            portion = i.get_portion(weight)

            if amount is None:
                amount = portion
            else:
                for index in portion.index:
                    amount[index] += portion[index]

        amount = amount * Food.standard_serving / total_weight  # wartosci odżywcze na 100g dania

        # create df from sql table with basic nutrition names and units
        q = f"SELECT * FROM {Food.db['nutr_name_db']} ORDER BY unit DESC"
        data = sql.read_query(self.connect, q)
        df = pd.DataFrame(data)
        df.insert(3, 'amount', 0, True)  # insert amount col with 0 value
        df.columns = Food.nutr_columns

        # change value of amount col for values for each nutrient
        for index in list(amount.index):
            df.loc[df.nutrient_id == index, 'amount'] = round(amount[index], 1)
        self._nutrients = df


if __name__ == '__main__':
    params = sql.config()
    conn = sql.connect(params)
    try:
        f = Food(conn)
        # print(f.id_list)
        # food = Ingredient(id=9749, connect=conn)
        #
        # n = food.nutrients
        # print(n)
        # old = n["amount"]
        # old.index = n["nutrient_id"]
        # print(food.get_portion(50))
        # print(old)
        # print(old.add(food.get_portion(50)))
        # n["amount"] = old.add(food.get_portion(50)).values
        # print(n)

        # print(type(n))

        # print(food.portion_df(50))
        # print(food)
        # food = Ingredient(id=3315, connect=conn)
        # print(food)
        # 1062: 1,
        # new = NewIngredient(connect=conn, name='okiuj', nutrients={1062: 1, 1008: 76}, category='custom food')
        # print(new)

        # ingr = {1026: 100, 8200: 30, 9040: 100, 1152: 30, 19165: 5, 16398: 10}
        # meal = NewMeal(connect=conn, name="owsianka z bananem i maslem orzechowym", ingredients=ingr)
        #
        # print(meal)
        # meal.update_db()
    finally:
        conn.close()
        print("closed")

    # Custom Meal database
    # names = ["owsianka z bananem i maslem orzechowym", "salatka z kurczakiem i pomidorami", "kanapka z hummusem", \
    #          "kanapka z halloumi", "owsianka poranna", "ryzanka proteinowa", "salatka makaron, feta, cukinia", \
    #          "omlet z mozzarella bez warzyw", "makaron, cukinia, pesto orzechowe"]
    # ingr = [{1026: 100, 8200: 30, 9040: 100, 1152: 30, 19165: 5, 16398: 10}, \
    #         {20036: 10, 5746: 100, 4053: 100, 11250: 30, 11529: 100}, \
    #         {18075: 70, 16158: 60, 11529: 100, 11250: 100}, \
    #         {18075: 70, 1157: 60, 11529: 100, 11250: 100}, \
    #         {8200: 50, 9050: 100, 16398: 40, 1152: 100},
    #         {20036: 30, 1152: 150, 14555: 100, 9501: 150, 1027: 80, 1287: 50}, \
    #         {1019: 50, 20124: 30, 11477: 150, 11821: 100, 4053: 5},
    #         {1123: 100, 20064: 30, 1026: 50, 4053: 5},
    #         {20124: 200, 11477: 200, 12155: 50, 1032: 50, 1152: 120, 4053: 60}]
