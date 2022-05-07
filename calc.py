import yaml
import argparse
import datetime
import exceptions


def get_calories_limit(profile, weights):

    def get_calculated_daily_calories_limit():

        def get_basal_metabolic_rate():

            def get_body_weight() -> float:

                if len(weights) > 0:
                    body_weight = list(weights[-1].items())[0][1]
                else:
                    body_weight = 0

                return float(body_weight)

            def get_age():

                days_in_year = 365.2425
                days_in_life = (datetime.date.today() - profile['birth_date']).days

                return int(days_in_life / days_in_year)

            weight = get_body_weight()
            height = profile['height']

            age = get_age()
            bmr = (10 * weight) + (6.25 * height) - (5 * age)  # https://en.wikipedia.org/wiki/Harris–Benedict_equation

            if profile['sex'] == 'man':
                bmr += 5
            else:
                bmr -= 161

            return bmr

        basal_metabolic_rate = get_basal_metabolic_rate()

        calories = basal_metabolic_rate * profile['activity_multiplier']
        shortage = calories * profile['caloric_deficit'] / 100

        return round(calories - shortage)

    if profile['calories_limit'] > 0:
        result = profile['calories_limit']
    else:
        result = get_calculated_daily_calories_limit()

    return result


def get_consumption_for_date(journal_for_date, catalog):

    def get_food(food_title):

        foods_list = list(filter(lambda x: x['title'] == food_title, foods))

        return foods_list[0] if len(foods_list) > 0 else None

    def get_food_template(food_title):

        return {
            'title': food_title,
            'total': get_total_template()
        }

    def get_total_template():

        return {
            'calories': 0,
            'protein': 0,
            'fat': 0,
            'carbs': 0,
        }

    def get_food_title_from_catalog(food_title):

        result = None

        for catalog_item in catalog:

            if catalog_item.lower() == food_title.lower():

                if type(catalog[catalog_item]) == str:
                    result = get_food_title_from_catalog(catalog[catalog_item])
                else:
                    result = catalog_item
                break

        return result

    def get_aggregates_of_journal_for_date():

        result = {}

        for entry in journal_for_date:

            try:

                entry_title = tuple(entry)[0]

                entry_title_from_catalog = get_food_title_from_catalog(entry_title)

                if entry_title_from_catalog is None:
                    raise exceptions.CatalogEntryNotFound(entry_title)

                entry_grams = tuple(entry.values())[0]

                if result.get(entry_title_from_catalog) is None:
                    result[entry_title_from_catalog] = entry_grams
                else:
                    result[entry_title_from_catalog] += entry_grams

            except exceptions.CatalogEntryNotFound as exception:

                print(exception.message)

        return result

    foods = []
    total = get_total_template()

    aggregates = get_aggregates_of_journal_for_date()

    for aggregate in aggregates:

        title = aggregate
        grams = aggregates[aggregate]

        food = get_food(title)

        if food is None:
            foods.append(get_food_template(title))
            food = foods[-1]

        attribute_values = catalog[title]

        for attribute in ('calories', 'protein', 'fat', 'carbs'):

            value = round(grams * attribute_values[attribute] / 100)

            food['total'][attribute] += value

            total[attribute] += value

    foods = sorted(foods, key=lambda x: x['total']['calories'], reverse=True)

    return foods, total


def get_yaml_data(yaml_filepath):

    with open(yaml_filepath, encoding='utf-8-sig') as yaml_file:
        result = yaml.safe_load(yaml_file)

    return result


def get_args() -> dict:

    parser = argparse.ArgumentParser()

    parser.add_argument('--profile', type=str, help='a path to the profile file')
    parser.add_argument('--journal', type=str, help='a path to the journal file')
    parser.add_argument('--catalog', type=str, help='a path to the catalog file')
    parser.add_argument('--weights', type=str, help='a path to the weights file')
    parser.add_argument('--date', type=str, help='a particular date to calculate consumption statistics')

    return vars(parser.parse_args())


def run():

    def get_food_offset():

        result = 0

        for catalog_item in catalog:

            length = len(catalog_item)

            if length > result:
                result = length

        return result + data_offset

    def print_table_row(food_value, calories_value, protein_value, fat_value, carbs_value):

        food_value = food_value.ljust(food_offset)
        calories_value = str(calories_value).ljust(data_offset)
        protein_value = str(protein_value).ljust(data_offset)
        fat_value = str(fat_value).ljust(data_offset)
        carbohydrates_value = str(carbs_value).ljust(data_offset)

        print(food_value, calories_value, protein_value, fat_value, carbohydrates_value)

    def print_nutrients_balance():

        def percent(value):

            if nutrients_total > 0:
                result = round(value * 100 / nutrients_total)
            else:
                result = 0

            result = str(result) + '%'

            return result

        def default_percent(value):

            return '{}%'.format(value)

        nutrients_total = total['protein'] + total['fat'] + total['carbs']

        protein_percent = percent(total['protein'])
        fat_percent = percent(total['fat'])
        carbs_percent = percent(total['carbs'])

        default_protein_percent = default_percent(profile['protein_percent'])
        default_fat_percent = default_percent(profile['fat_percent'])
        default_carbs_percent = default_percent(profile['carbs_percent'])

        print_table_row('Balance today', '', protein_percent, fat_percent, carbs_percent)
        print_table_row('Target ranges', '', default_protein_percent, default_fat_percent, default_carbs_percent)

    def print_calories_balance():

        calories_limit = get_calories_limit(profile, weights)
        calories_to_consume = calories_limit - total['calories']

        if calories_to_consume >= 0:
            balance_message = 'balance for today — {}.'.format(calories_to_consume)
        else:
            balance_message = 'excess — {}!'.format(calories_to_consume * -1)

        message = 'Daily calorie intake — {} kcal; {}'.format(calories_limit, balance_message)

        print(message)

    def get_yaml_file_data(arg):

        yaml_filepath = args.get(arg)

        if yaml_filepath is None:
            yaml_filepath = '{}.yaml'.format(arg)

        result = None

        try:

            with open(yaml_filepath, encoding='utf-8-sig') as yaml_file:
                result = yaml.safe_load(yaml_file)

        except FileNotFoundError:

            print("File is not found: {}".format(yaml_filepath))
            exit(1)

        return result

    args = get_args()

    profile = get_yaml_file_data('profile')
    journal = get_yaml_file_data('journal')
    weights = get_yaml_file_data('weights')
    catalog = get_yaml_file_data('catalog')

    date = args['date'] if args.get('date') is not None else datetime.datetime.today().strftime('%d.%m.%Y')

    journal_for_date = journal.get(date)

    if journal_for_date is not None:

        foods, total = get_consumption_for_date(journal_for_date, catalog)

        data_offset = 15
        food_offset = get_food_offset()

        print_table_row('FOOD', 'CALORIES', 'PROTEIN', 'FAT', 'CARBS')
        print()

        for entry in foods:
            print_table_row(
                entry['title'],
                entry['total']['calories'],
                entry['total']['protein'],
                entry['total']['fat'],
                entry['total']['carbs']
            )

        print()
        print_table_row('TOTAL', total['calories'], total['protein'], total['fat'], total['carbs'])

        print()
        print_nutrients_balance()

        print()
        print_calories_balance()


if __name__ == '__main__':
    run()
