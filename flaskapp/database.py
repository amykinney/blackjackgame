from typing import Any, Dict, List

from pymysql import connect
from pymysql.cursors import DictCursor

from flaskapp.config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE

"""
Big Hint #1: Alexander used dictionaries. Example usages are at
the bottom of this file.

For example:

```
add_person(
    {
        "name": "Alan Perlis",
        "email": "perlis@example.com",
        "date_of_birth": "1990-01-01",
        "mobile_phone_number": "1112223333",
        "role": "member",
    }
)
```
"""


def get_connection():
    return connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        cursorclass=DictCursor,
    )


def get_people() -> List[Dict[str, Any]]:
    """Get a list of dictionaries for every person in the database."""
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute("select * from person")
        people = curr.fetchall()
    conn.close()
    return people


def get_person(person_id: int) -> Dict[str, Any]:
    """Get a person by their id, return a dictionary containing their data."""
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute("select * from person where id = %s", (person_id,))
        person = curr.fetchone()
    conn.close()
    return person



def get_members() -> List[Dict[str, Any]]:
    """Only *members* can rent items.
    """
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute("select * from person where role = 'member'")
        members = curr.fetchall()
    conn.close()
    return members


def add_person(new_person: Dict[str, Any]) -> None:
    """Takes data for a person, puts it in the person table.

    See also: Big Hint #1 (above)
    """
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute(
            "insert into person (name, email, date_of_birth, mobile_phone_number, role) values (%s, %s, %s, %s, %s)",
            (
                new_person["name"],
                new_person["email"],
                new_person["date_of_birth"],
                new_person["mobile_phone_number"],
                new_person["role"],
            )
        )
    conn.commit()
    conn.close()



def update_person(person_id: int, person_data: Dict[str, str]) -> None:
    """Updates the person table with 'person_data' for the person with 'person_id'

    See also: Big Hint #1 (above)
    """
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute(
            "update person set name=%s, email=%s, date_of_birth=%s, mobile_phone_number=%s, role=%s where id=%s",
            (
                person_data["name"],
                person_data["email"],
                person_data["date_of_birth"],
                person_data["mobile_phone_number"],
                person_data["role"],
                person_id,
            )
        )
    conn.commit()
    conn.close()


def get_all_items() -> List[Dict[str, Any]]:
    """Get all items from the 'item' table."""
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute("select * from item")
        items = curr.fetchall()
    conn.close()
    return items



def get_one_item(item_id: int) -> Dict[str, Any]:
    """Get data for the item with `item_id`"""
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute("select * from item where id = %s", (item_id,))
        item = curr.fetchone()
    conn.close()
    return item


def add_item(new_item: Dict[str, Any]) -> None:
    """Takes data for a new item, puts it in the 'item' table.
    """
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute(
            "insert into item (name, summary, description, daily_rental_price, weight, purchase_date, item_condition, notes, image_path, currently_available) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                new_item["name"],
                new_item["summary"],
                new_item["description"],
                new_item["daily_rental_price"],
                new_item["weight"],
                new_item["purchase_date"],
                new_item["item_condition"],
                new_item["notes"],
                new_item["image_path"],
                new_item["currently_available"],
            )
        )
    conn.commit()
    conn.close()


def update_one_item(item_id: int, updated_equipment: Dict[str, Any]) -> None:
    """Updates data for an 'item' using the 'item_id'
    """
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute(
            "update item set name=%s, summary=%s, description=%s, daily_rental_price=%s, weight=%s, purchase_date=%s, item_condition=%s, notes=%s, image_path=%s, currently_available=%s where id = %s",
            (
                updated_equipment["name"],
                updated_equipment["summary"],
                updated_equipment["description"],
                updated_equipment["daily_rental_price"],
                updated_equipment["weight"],
                updated_equipment["purchase_date"],
                updated_equipment["item_condition"],
                updated_equipment["notes"],
                updated_equipment["image_path"],
                updated_equipment["currently_available"],
                item_id,
            )
        )
    conn.commit()
    conn.close()


def get_due_dates() -> List[Dict[str, Any]]:
    """Get the 'item_id' and the 'due_date' for each item that is rented out.
    """
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute("select item_id, due_date from rental where return_date is null")
        items = curr.fetchall()
    conn.close()
    return items


def rent_one_item(person_id: int, item_ind: int) -> None:
    """
    Inserts appropriate data into the database representing the the person
    is renting an item.

    TODO(hayesall): This does not validate that an item is `currently_available`.
        I assume that has already been done elsewhere.
    """
    conn = get_connection()
    with conn.cursor() as curr:
        curr.execute("insert into rental (person_id, item_id) values (%s, %s)", (person_id, item_ind))
        curr.execute("update item set currently_available = 0 where id = %s", (item_ind,))
    conn.commit()
    conn.close()


def return_one_item(item_ind: int):
    """
    Updates the database to indicate the item was returned.

    TODO(hayesall): I *think* the updates will fail if this gets called on an
        invalid `item_id` (e.g. where there is not a NULL return date),
        but this hasn't been tested thoroughly.
    """
    conn = get_connection()
    with conn.cursor() as curr:

        # Since an item cannot be rented out
        # by multiple people at the same time:
        # we can update the `rental` table using
        # an item_id and a NULL value.
        #
        # A NULL can become a date, but not the
        # other way around.

        curr.execute("update rental set return_date = curdate() where return_date is null and item_id = %s", (item_ind,))

        curr.execute("update item set currently_available = 1 where id = %s", (item_ind,))

    conn.commit()
    conn.close()

def get_rentals_by_person(person_id: int) -> List[Dict[str, Any]]:
    """
    Return all attributes from the 'item' table for all items rented
    out by the person with 'person_id'.
    """
    conn = get_connection()
    with conn.cursor() as curr:

        # Since a person can rent the same item multiple times, this also
        # includes dates from the rental table to disambiguate rows.

        curr.execute("select item.*, checkout_date, return_date, due_date from item join rental on rental.item_id = item.id where person_id = %s", (person_id,))
        items = curr.fetchall()
    conn.close()
    return items


def get_all_past_item_rentals(item_id: int) -> List[Dict[str, Any]]:
    """Return all data in 'rental' for item with 'item_id'."""
    conn = get_connection()
    with conn.cursor() as curr:

        # This also joins on the person table, since a human-readable
        # name is easier to understand than an indecipherable "1".

        curr.execute("select name, rental.* from rental join person on rental.person_id = person.id where item_id = %s", (item_id,))
        items = curr.fetchall()
    conn.close()
    return items


if __name__ == "__main__":

    from pprint import pprint

    print(get_people())
    print(get_person(1))

    pprint(get_members())

    add_person(
        {
            "name": "Alan Perlis",
            "email": "perlis@example.com",
            "date_of_birth": "1990-01-01",
            "mobile_phone_number": "1112223333",
            "role": "member",
        }
    )

    update_person(
        7,
        {
            "name": "Alan Perlis",
            "email": "perlis@example.com",
            "date_of_birth": "1980-01-01",
            "mobile_phone_number": "1112223333",
            "role": "member",
        }
    )

    pprint(get_all_items())

    pprint(get_one_item(1))

    add_item(
        {
            "name": "Binoculars",
            "summary": "TODO",
            "description": "TODO",
            "daily_rental_price": "5",
            "weight": "2",
            "purchase_date": "2023-01-01",
            "item_condition": "new",
            "notes": "TODO",
            "image_path": "images/null_image.jpg",
            "currently_available": "1",
        }
    )

    update_one_item(
        7,
        {
            "name": "Binoculars",
            "summary": "TODO",
            "description": "TODO",
            "daily_rental_price": "5",
            "weight": "2",
            "purchase_date": "2023-01-01",
            "item_condition": "new",
            "notes": "TODO",
            "image_path": "images/null_image.jpg",
            "currently_available": "1",
        }
    )

    pprint(get_due_dates())

    rent_one_item(1, 1)
    return_one_item(1)

    pprint(get_rentals_by_person(1))

    pprint(get_all_past_item_rentals(1))
# from typing import Any, Dict, List

# from pymysql import connect
# from pymysql.cursors import DictCursor

# from flaskapp.config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE

# """
# Big Hint #1: For all items and people (adding and updating), you can either use dictionaries,
# or write your functions with all of the attributes in the function
# signature (like we did in the lecture repo).

# For example:

# ```
# add_person(new_person: Dict[str, str])
# ```

# or

# ```
# add_person(name, email, date_of_birth, mobile_phone_number, role)
# ```

# Big Hint #2: Depending on how you wrote your 2.2 code, one might be
# far easier than the other.
# """


# def get_connection():
#     return connect(
#         host=DB_HOST,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         database=DB_DATABASE,
#         cursorclass=DictCursor,
#     )


# def get_people() -> List[Dict[str, Any]]:
#     """Get a list of dictionaries for every person in the database."""
#     sql = "SELECT * FROM person"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql)
#         people = cursor.fetchall()
#     conn.close()
#     return people

# def get_person(person_id: int) -> Dict[str, Any]:
#     """Get a person by their id, return a dictionary containing their data."""
#     sql = "SELECT * FROM person WHERE id = %s"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (person_id,))
#         person = cursor.fetchone()
#     conn.close()
#     return person


# def get_members() -> List[Dict[str, Any]]:
#     """
#     Only *members* can rent items. Return a list of dictionaries for all
#     people with role=member.

#     Hint: You might need this in 3.3 for renting an item.
#     """
#     sql = "SELECT * FROM person where role ='member'"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql)
#         people = cursor.fetchall()
#     conn.close()
#     return people


# def add_person(new_person: Dict[str, Any]) -> None:
#     """Takes data for a person, puts it in the person table.

#     See also: Big Hint #1 (above)
#     """
#     sql = "INSERT INTO person (name, email, date_of_birth, mobile_phone_number, role) VALUES (%s, %s, %s, %s, %s)"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (new_person['name'], new_person['email'], new_person['date_of_birth'], new_person['mobile_phone_number'], new_person['role']))
#     conn.commit() 
#     conn.close()



# def update_person(person_id: int, person_data: Dict[str, str]) -> None:
#     """Updates the person table with 'person_data' for the person with 'person_id'

#     See also: Big Hint #1 (above)
#     """
#     sql = "UPDATE item SET name = %s, email = %s, date_of_birth = %s, mobile_phone_number = %s, role = %s, WHERE id = %s"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (
#             person_data['name'], person_data['email'], person_data['date_of_birth'],person_data['mobile_phone_number'], person_data['role'], person_id))
#     conn.commit()
#     conn.close()


# def get_all_items() -> List[Dict[str, Any]]:
#     sql = "SELECT * FROM item"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql)
#         items = cursor.fetchall()
#     conn.close()
#     return items


# def get_one_item(item_id: int) -> Dict[str, Any]:
#     """Get data for the item with `item_id`"""
#     sql = "SELECT * FROM item WHERE id = %s"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (item_id,))
#         item = cursor.fetchone()
#     conn.close()
#     return item


# def add_item(new_item: Dict[str, Any]) -> None:
#     sql = "INSERT INTO item(name,summary,description,daily_rental_price,weight,image_path,item_condition,purchase_date,notes,currently_available) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (new_item['name'], new_item['summary'], new_item['description'], new_item['daily_rental_price'], new_item['weight'], new_item['image_path'], new_item['item_condition'], new_item['purchase_date'], new_item['notes'], new_item['currently_available']))
#     conn.commit() 
#     conn.close()

# def update_one_item(item_id: int, updated_equipment: Dict[str, Any]) -> None:
#     sql = "UPDATE item SET name = %s, summary = %s, description = %s, daily_rental_price = %s, weight = %s, image_path = %s, item_condition = %s, purchase_date = %s, notes = %s, currently_available = %s WHERE id = %s"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (
#             updated_equipment['name'], updated_equipment['summary'], updated_equipment['description'],updated_equipment['daily_rental_price'], updated_equipment['weight'], updated_equipment['image_path'],updated_equipment['item_condition'], updated_equipment['purchase_date'], updated_equipment['notes'],updated_equipment['currently_available'], item_id))
#     conn.commit()
#     conn.close()


# def get_due_dates() -> List[Dict[str, Any]]:
#     sql = "SELECT item_id, due_date FROM rental WHERE return_date IS NULL"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql)
#         due_dates = []
#         for row in cursor.fetchall():
#             duedateinfo = {"item_id": row['item_id'], "due_date": row['due_date']}
#             due_dates.append(duedateinfo)
#     conn.close()
#     return due_dates

# def rent_one_item(person_id: int, item_ind: int) -> None:
#     """
#     Inserts appropriate data into the database representing the the person
#     is renting an item.

#     "due date" in the rental table should be set to 14 days from the current date.
#     """
#     sql = ""
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (person_id,))
#         rentals = cursor.fetchone()
#     conn.close()
#     return rentals


# def return_one_item(item_ind: int):
#     """
#     Updates the database to indicate the item was returned. Both the
#     'item' and 'rental' table must be updated appropriately.
#     """
#     sql = "UPDATE rental SET return_date = %s WHERE item_id = %s AND return_date IS NULL"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (item_ind,))
#         rentals = cursor.fetchone()
#     conn.close()
#     return rentals



# def get_rentals_by_person(person_id: int) -> List[Dict[str, Any]]:
#     """
#     Return all attributes from the 'item' table for all items rented
#     out by the person with 'person_id'.
#     """
#     sql = "SELECT * FROM rental WHERE return_date is NOT NULL and item_id = %s"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (person_id))
#         rentals = cursor.fetchall()
#     conn.close()
#     return rentals
    


# def get_all_past_item_rentals(item_id: int) -> List[Dict[str, Any]]:
#     sql = "SELECT * FROM rental WHERE return_date IS NOT NULL AND item_id = %s"
#     conn = get_connection()
#     with conn.cursor() as cursor:
#         cursor.execute(sql, (item_id,))
#         rentals = cursor.fetchall()
#     conn.close()
#     return rentals

# if __name__ == "__main__":
#     print(get_due_dates())
#     # new_person = {
#     #     "name": "Amy Kinney",
#     #     "email": "amykinney0@gmail.com",
#     #     "date_of_birth": "2003-11-21",
#     #     "mobile_phone_number": "3173334070",
#     #     "role": "member"
#     # }
#     # add_person(new_person)
#     # people = get_people()
#     # for person in people:
#     #     print(person)

#     # new_item = {
#     #     "name": "Waterbottle",
#     #     "summary": "blah blah blah",
#     #     "description": "blah blah blah blah",
#     #     "daily_rental_price": 17,
#     #     "weight": 5,
#     #     "image_path": 'images/null_image.jpg',
#     #     "item_condition": "good",
#     #     "purchase_date": "2024-04-17",
#     #     "notes": "blahh blajj",
#     #     "currently_available": 3
#     # }
#     # add_item(new_item)
#     # items = get_all_items()
#     # for item in items:
#     #     print(item)

#     #update_person
#     #get_due_dates
#     #rent_one_item
#     #return_one_item
#     #get_rentals_by_person
#     #get_all_past_item_rentals