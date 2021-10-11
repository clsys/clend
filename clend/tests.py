from django.test import TestCase

# Create your tests here.
from settings import SETTINGS
def main():
    print(SETTINGS["datafeed.password"])
if __name__ == '__main__':
    main()
