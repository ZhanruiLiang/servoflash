import os, subprocess

Error = Exception

def update_join(d1, d2=None, **dargs):
    " update d1 with d2 -> d3 "
    d3 = d1.copy()
    if dargs:
        d2 = dargs
    for k, v in d2.iteritems():
        d3[k] = v
    return d3

def ord_join(ord1, ord2):
    result = []
    ord1 = ord1[::-1]
    ord2 = ord2[::-1]
    while ord1 and ord2:
        x = ord1[-1]
        if x not in ord2:
            result.append(x)
            del ord1[-1]
        else:
            y = ord2[-1]
            if x == y:
                result.append(x)
                del ord1[-1]
                del ord2[-1]
            elif y not in ord1:
                result.append(y)
                del ord2[-1]
            else:
                raise Error("cyclic order join: joined: %s, left: %s, %s" % (
                    result, ord1[::-1], ord2[::-1]))
    if ord1: result += ord1[::-1]
    else: result += ord2[::-1]
    return result

def concat_func(func1, func2):
    def func(*args, **dargs):
        func1(*args, **dargs)
        func2(*args, **dargs)
    return func

def color_eq(c1, c2):
    d = sum((x1 - x2) ** 2 for x1, x2 in zip(c1, c2))
    return d < 30

# step color c1 to color c2
def step_color(c1, c2, k=0.30):
    return tuple(int(x1 + (x2 - x1) * k) for x1, x2 in zip(c1, c2))

def copy_to_X(text):
    os.system("echo '%s' |xsel -b" % text)

def paste_from_X():
    p = subprocess.Popen('xsel -b', shell=True, stdout=subprocess.PIPE)
    p.wait()
    return p.stdout.read().rstrip()
