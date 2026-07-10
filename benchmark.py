import timeit
import datetime

# Setup
setup_code = """
import datetime
date_str = '2023-10-27'
today = datetime.date.today()
"""

test1 = """
try:
    exp_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
except:
    exp_date = today
"""

test2 = """
try:
    exp_date = datetime.date.fromisoformat(date_str)
except:
    exp_date = today
"""

# Run tests
n = 1000000
t1 = timeit.timeit(test1, setup=setup_code, number=n)
t2 = timeit.timeit(test2, setup=setup_code, number=n)

print(f"strptime: {t1:.4f} seconds")
print(f"fromisoformat: {t2:.4f} seconds")
print(f"Improvement: {(t1-t2)/t1*100:.2f}%")
