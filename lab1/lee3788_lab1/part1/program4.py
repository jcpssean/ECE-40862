birthdays = {
    "James": "01/01/2000",
    "Jason": "09/09/1966",
    "Eric": "03/22/1978",
    "Alice": "04/13/2016",
    "Bella": "12/25/1988"
}
print(f"Welcome to the birthday dictionary. We know the birthdays of: ")
for n in birthdays:
    print(n)
name = input("Whose birthday do you want to look up? ")
print(f"{name}'s birthday is {birthdays[name]}.")
