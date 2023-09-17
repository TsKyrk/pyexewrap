import traceback

try:
    print("hello")
    exit(1)
    print("your won't see this")
except BaseException as e:
    print(traceback.format_exc())

input("pause")