from django.test import TestCase

# Create your tests here.

if __name__ == '__main__':
    list = [1]
    times = 1
    while True:
        times += 1
        print(times)
        list.extend(list)
