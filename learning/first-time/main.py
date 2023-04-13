def thing(c):
    """
    things a c
    
    Arguments:
        c {number} -- an integer to thing with
    """
    return 'c=' + c


def foo(a, b):
    """foo a with b
    
    Arguments:
        a {string} -- the value of a
        b {string} -- the value of b

    Return:
        Foo of a by b
    """
    return (a+1, b+1)


bar = (foo, 1, "b".format("face"), 0x1B, "\n", False)
print(bar[5])
esc = "{0:08b}".format(127)
print(esc)

zipped = zip('<^>', ['left', 'center', 'right'])
print(type(zipped))
for align, text in zipped:
    print('{0:{fill}{align}16}'.format(text, fill=align, align=align))

a = 3
b = 7

first_name = "Rick"
last_name = "Christy"

full_name = first_name + " " + last_name
print(full_name)
full_name = first_name \
    + " " + last_name
print(full_name)
full_name = first_name \
    + \
        " " \
            + \
                last_name
print(full_name)
print(first_name, last_name)
print(*[first_name, last_name])
names = {
    "first": first_name,
    "last": last_name
}
print(*names)
names = { "value": names }
print(names)
print(*names)
print(first_name, last_name)
full_name = "print(\"" + first_name + ", " + last_name + "\")"
eval(full_name)
full_name = ("Rick" " " "Christy")
print(full_name)
names = [ first_name, last_name ]
full_name.join(names)
print(full_name)
names = ( first_name, last_name )
full_name.join(names)
print(full_name)

names = { first_name, last_name }
print(names)
print(type(names))
full_name.join(names)
print(full_name)

names = { "f": first_name, "l": last_name }
print(names)
print(type(names))
full_name.join(names)
print(full_name)
print(type(names['f'][0:1]))
print(type(foo(a,b)))

print(dir(foo.__code__))

print(
    """
    things: {a}
    stuff : {b}
    """.format(
        a=a,
        b='more'
    )
)
print(
    """
    foo: {}
    bar: {}
    """.format(
        *foo(1,2)
    )
)
