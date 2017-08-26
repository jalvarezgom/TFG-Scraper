#!/usr/bin/python

# simple script
print ("Hello World!")

# using function
def greeting():
    print ("Hello World!")

# call function
greeting()


# using a function that returns a greeting
def greeting2():
    return "Hello World!"

# print the return value
print (greeting2())


# using a class
class MyClass:
    def greeting(self): print ("Hello World!")


myClass = MyClass()
myClass.greeting()

# done!
# fin!