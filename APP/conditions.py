print(" Movie Ticket Booking System")
age = int(input("Enter your age: "))
if age < 18:
    ticket_price = 100
elif age <= 60:
    ticket_price = 200
else:
     ticket_price = 150
print("Your ticket price is: ", ticket_price)