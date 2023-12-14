import sql
import food
import user
import datetime


class App:
    """application to manage diet"""
    def __init__(self):
        self.params = sql.config()
        self.connect = sql.connect(self.params)
        self.running = True

    def get_columns(self, table_name):
        """returns column name for given table name"""
        q = f"SELECT column_name FROM information_schema.columns \
             WHERE table_name = '{table_name}' \
               ORDER BY ordinal_position;"
        return sql.read_query(self.connect, q)

    def get_categories(self):
        """return categories of food from food database"""
        q = f"SELECT DISTINCT category FROM {user.User(connect=self.connect).user_db["info_db"]}"
        categories = sql.read_query(self.connect, q)
        return [i[0] for i in categories]

    def find_food(self):
        """find food in food database
        name - na,e of the food
        category - category of the food"""
        # TODO case insensitive search for categories
        name = input("Enter food name: ")
        category = input("Enter category name(optional): ")

        q = f"SELECT * FROM {food.Food.db['info_db']} WHERE description LIKE '%{name}%'"

        # check if cat input is valid category name
        if category in self.get_categories():
            q += f" AND category = '{category}'"

        col = self.get_columns(food.Food.db['info_db'])
        foods = sql.read_query(self.connect, q)

        if len(foods) == 0:
            print("No food found")
            return None

        f = zip(*foods)
        ids, description, cat, ingr = list(f)
        ids = list(map(str, ids))  # convert int to str
        # convert None to string "-" to for later checking of field width
        ingr = ["-" if i is None else i for i in ingr]

        # find longest string for each column
        data_list = [ids, description, cat, ingr]

        # addd column name to column values to check the longest string
        data_list = [[val[0]] + list(data_list[count]) for count, val in enumerate(col)]
        fields_width = [max(map(len, i)) for i in data_list]

        # print column names
        for tup in zip(fields_width, [c[0] for c in col]):
            print(f"%-{tup[0]}s |" % tup[1], end='')
        print()
        # print frame
        for w in fields_width:
            print(f"%-{w}s |" % ("-" * w), end='')
        print()
        # print food records
        for ids, description, cat, ingr in foods:
            print(f"%-{fields_width[0]}s |%-{fields_width[1]}s |%-{fields_width[2]}s |%-{fields_width[3]}s |" % (ids, description, cat, ingr))

        return None

    def get_food(self):
        """print info about food"""
        id = self.get_id("Enter food ID: ")
        print(food.Ingredient(id, self.connect))

    def add_ingredient(self):
        """add basic food to database"""
        name = input("Enter name:")
        cat = input("Enter category:")
        nutrients = self.collect_components(nutrients=True)
        res = food.NewIngredient(connect=self.connect, name=name, nutrients=nutrients, category=cat)
        res.update_db()
        print(f"{res}\nUpdated!")

    def add_meal(self):
        """add meal (consisting of simple foods) to database"""
        name = input("Enter name:")
        ingredients = self.collect_components(nutrients=False)
        res = food.NewMeal(connect=self.connect, name=name, ingredients=ingredients)
        res.update_db()
        print(f"{res}\nUpdated!")

    def collect_components(self, nutrients=True):
        """returns dictionary from input values
        if nutrients = True returns dict of nutrients:amount otherwise dictionary of food: amount"""
        res = {}
        if nutrients:
            msg = 'Enter nutrient ID: '
        else:
            msg = 'Enter ingredient ID: '

        while True:
            id = self.get_id(msg, nutrients=nutrients)
            amount = self.get_amount()

            res[id] = amount
            n = input("Enter next ingredient? y/n: ")
            if n == "n":
                break
        return res

    def get_date(self):
        while True:
            try:
                day = input("Date: ")
                return datetime.datetime.strptime(day, '%Y-%m-%d').date()
            except ValueError:
                print("Date must be in YYYY-mm-dd format")

    def get_id(self, msg, nutrients=False):
        if nutrients:
            id_list = food.Food(self.connect).nutrients_id
        else:
            id_list = food.Food(self.connect).id_list

        while True:
            try:
                meal_id = int(input(f"{msg}"))
                if meal_id not in id_list:
                    print("ID not found!")
                    continue
                return meal_id
            except ValueError:
                print("ID has to be a number")

    def get_index(self):
        while True:
            try:
                index = input("Index: ")
                if index == "":
                    index = None
                else:
                    index = int(index)
                return index
            except ValueError:
                print("Index has to be a number")

    def get_amount(self):
        while True:
            try:
                amount = int(input("Amount: "))
                if amount <= 0:
                    raise ValueError
                return amount
            except ValueError:
                print("Amount has to be a positive number")

    def get_login(self):
        while True:
            login = input("Enter Login: ")
            if login in user.User(self.connect).login_list:
                print("Login already exists")
            else:
                return login

    def get_sex(self):
        while True:
            try:
                sex = int(input("Enter sex: "))
                if sex in [0, 1]:
                    return sex
                raise ValueError
            except ValueError:
                print("Sex has to be 0 for female or 1 for male")

    def get_age(self):
        while True:
            try:
                age = int(input("Enter age: "))
                if 18 <= age <= 99:
                    return age
                raise ValueError
            except ValueError:
                print("Age has to be between 18 and 99")

    def get_height(self):
        while True:
            try:
                height = int(input("Enter height: "))
                if 0 <= height <= 250:
                    return height
                raise ValueError
            except ValueError:
                print("Height has to be between 0 and 250")

    def get_weight(self):
        while True:
            try:
                w = int(input("Enter weight: "))
                if 0 <= w <= 250:
                    return w
                raise ValueError
            except ValueError:
                print("Weight has to be between 0 and 250")

    def get_wact(self):
        while True:
            try:
                wact = int(input("Enter your work activity level: "))
                if int(wact) in [0, 1, 2, 3]:
                    return wact
                raise ValueError
            except ValueError:
                print("Work activity should be in [0, 1, 2, 3]")

    def get_pact(self):
        while True:
            try:
                pact = int(input("Enter your physical activity level: "))
                if pact in [0, 1, 2, 3]:
                    return pact
                raise ValueError
            except ValueError:
                print("Physical activity should be in [0, 1, 2, 3]")

    def get_loss_ratio(self):
        while True:
            try:
                ratio = float(input("Enter how many kg you wish to lose per week: "))
                if ratio >= 0:
                    return ratio
                raise ValueError
            except ValueError:
                print("Loss ratio should >= 0")

    def get_macro(self, macro):
        """take input from user and check if input is valid for macronutrient
        if input value is "" return default maronutrient value
        macro: carbohydrates, proteins, lipids, fiber"""
        if macro not in ['carbohydrates', 'proteins', 'lipid', 'fiber']:
            raise ValueError('Invalid macro parameter')
        if macro == "fiber":
            macro_name = "fiber_mass"
        else:
            macro_name = f"{macro}_percent"
        while True:
            try:
                if macro == "fiber":
                    i = input(f"Enter mass of {macro} (g) in daily intake: ")
                else:
                    i = input(f"Enter percent of {macro} in daily kcal intake: ")
                if i == "":
                    return user.User.intake_calc[macro_name]
                i = float(i)
                if macro == "fiber":
                    i = int(i)
                    valid = user.User.fiber_valid(i)
                else:
                    i = float(i)
                    valid = user.User.macro_valid(i)

                if valid:
                    return i
            except ValueError:
                print("Macro value has to be between 0 and 1")

    def get_week(self):
        while True:
            try:
                week = int(input("Enter week: "))
                if 0 < week < 53:
                    return week
                raise ValueError
            except ValueError:
                print("Week should be between 1 and 52")

    def get_dv(self):
        dv = input("Reference daily values? (y/n): ")
        if dv == "y":
            return True
        return False

    def delete_food(self):
        """delete food/meal from database"""
        id = self.get_id("Enter food ID: ")
        food.Food.delete_food(id, self.connect)
        print("Deleted!")

    def show_schedule(self, usr):
        """print meal schedule of user"""
        for day, meals in usr.schedule.items():
            print(day)
            print(meals)

    def show_day(self, usr):
        """show daily meal schedule"""
        day = self.get_date()
        try:
            day = usr.schedule[day]
            print(day)
            diff = usr.kcal_diff(day.energy_kcal)
            if diff >= 0:
                print(f"You are {diff} kcal short.")
            else:
                print(f"You ate {diff*(-1)} kcal too much.")

        except KeyError:
            print("No such day in calendar")

    def add_meal_usr(self, usr):
        """add meal to user schedule"""
        day = self.get_date()
        meal_id = self.get_id("Meal ID: ")
        amount = self.get_amount()
        index = self.get_index()

        usr.add_meal(day, meal_id, amount, index)

    def replace_meal_usr(self, usr):
        """replace meal in schedule"""
        day = self.get_date()
        meal_id = self.get_id("Meal ID: ")
        amount = self.get_amount()
        index = self.get_index()

        usr.replace_meal(day, index, meal_id, amount)

    def remove_meal_usr(self, usr):
        """remove meal from user schedule"""
        day = self.get_date()
        index = self.get_index()

        usr.remove_meal(day, index)

    def remove_day(self, usr):
        """ remove whole day from user schedule"""
        day = self.get_date()
        usr.remove_day(day)

    def set_macronutrients(self, usr):
        """set daily macornutrients percent"""
        usr.carbohydrates = self.get_macro("carbohydrates")
        usr.proteins = self.get_macro("proteins")
        usr.lipids = self.get_macro("lipid")
        usr.fiber = self.get_macro("fiber")

    def daily_balance(self, usr):
        """print day nutritions with macronutirents percent"""
        day = self.get_date()
        dv = self.get_dv()
        print(usr.balance(usr.schedule[day], dv))

    def week_balance(self, usr):
        """print week nutritions with macronutirents percent"""
        week = self.get_week()
        dv = self.get_dv()
        print(usr.week_balance(week, dv=dv))

    def update_usr(self, usr):
        usr.update()

    def browse_food_commands(self):
        print("___Browse Food Commands___")
        print("c - Print Commands")
        print("1 - Find Food")
        print("2 - Get Food")
        print("3 - Add Ingredient")
        print("4 - Add Meal")
        print("9 - Delete Food")
        print("b - Back")
        print("q - Quit")

    def main_commands(self):
        print("___Diet Planner Commands___")
        print("c - Print Commands")
        print("1 - Login")
        print("2 - New User")
        print("3 - Browse Food")
        print("q - Quit")
        print("d - debug")

    def user_commands(self):
        print("___User Commands___")
        print("c - Print Commands")
        print("1 - Show schedule")
        print("2 - Show day")
        print("3 - Add Meal")
        print("4 - Replace meal")
        print("5 - Remove meal")
        print("6 - Remove day")
        print("7 - Set macronutrients")
        print("8 - Show user")
        print("9 - Update")
        print("10 - Daily balance")
        print("11 - Week balace")
        print("b - Back (logout)")
        print("q - Quit")

    def quit(self):
        self.connect.close()
        self.running = False
        print("quit")

    def browse_food(self):
        self.browse_food_commands()
        while True:
            print("Browse Food:")
            cmd = input("Command:")
            if cmd == "1":
                self.find_food()
            if cmd == "2":
                self.get_food()
            if cmd == "3":
                self.add_ingredient()
            if cmd == "4":
                self.add_meal()
            if cmd == "9":
                self.delete_food()
            if cmd == "c":
                self.browse_food_commands()
            if cmd == "b":
                break
            if cmd == "q":
                self.quit()
                break

    def login(self):
        """ returns user obj from input login and password"""
        while True:
            login = input("Login: ")
            pswd = input("Password: ")
            try:
                usr = user.User(self.connect, login=login)
            except ValueError:
                print("Login not valid")
                continue
            if pswd == usr.password:
                print("Login successful")
                return usr
            else:
                print("Wrong password")
                continue

    def new_user(self):
        """create ne user"""
        login = self.get_login()
        name = input("Enter name: ")
        pswd = input("Enter password: ")
        sex = self.get_sex()
        age = self.get_age()
        height = self.get_height()
        weight = self.get_weight()
        wact = self.get_wact()
        pact = self.get_pact()
        loss_ratio = self.get_loss_ratio()

        return user.User(connect=self.connect, new=True, login=login, name=name, password=pswd, sex=sex, age=age,
                         height=height, weight=weight, wact=wact, pact=pact, loss_ratio=loss_ratio)

    def user_menu(self, usr):
        self.user_commands()
        while True:
            print(f"Hello, {usr.name}!")
            cmd = input("Command:")
            if cmd == "1":
                self.show_schedule(usr)
            if cmd == "2":
                self.show_day(usr)
            if cmd == "3":
                self.add_meal_usr(usr)
            if cmd == "4":
                self.replace_meal_usr(usr)
            if cmd == "5":
                self.remove_meal_usr(usr)
            if cmd == "6":
                self.remove_day(usr)
            if cmd == "7":
                self.set_macronutrients(usr)
            if cmd == "8":
                print(usr)
            if cmd == "9":
                self.update_usr(usr)
            if cmd == "10":
                self.daily_balance(usr)
            if cmd == "11":
                self.week_balance(usr)
            if cmd == "c":
                self.user_commands()
            if cmd == "b":
                break
            if cmd == "q":
                self.quit()
                break

    def debug(self):
        # usr = self.new_user()
        # self.user_menu(user.User(connect=self.connect, login='s'))
        self.week_balance(user.User(connect=self.connect, login='p'))
        self.quit()

    def run(self):
        self.main_commands()
        while self.running:
            print("Main Menu:")
            cmd = input("Command:")

            if cmd == "1":
                usr = self.login()
                self.user_menu(usr)
                del usr
            if cmd == "2":
                usr = self.new_user()
                self.user_menu(usr)
                del usr
            if cmd == "3":
                self.browse_food()
            if cmd == "c":
                self.main_commands()
            if cmd == "q":
                self.quit()
            if cmd == "d":
                self.debug()
        self.connect.close()


if __name__ == '__main__':
    app = App()
    # app.debug()
    app.run()
