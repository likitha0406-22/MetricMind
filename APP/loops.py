print(" Metricmind daily sales counter")
sales = [ 1200, 1500, 1800, 2200,2500]
print("sales using for loop")
total_sales = 0
for sale in sales:
    print("sales:", sale)
    total_sales += sale
    print("Total sales:", total_sales)
    print("sales using while loop")
    i = 0
    while i< len(sales):
        print ("day", i+1, "sales:", sales[i])
        i += 1