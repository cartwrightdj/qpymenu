import time
def hello_world():
    print('Hello World')

def read_text_file(filepath):
    with open(filepath) as f:
        print(f.readlines())

def about():
    print("qPyMenu\n\n"
          "Quick and easy menuing ssytem for python")

def count_down():
    x = [i for i in range(30)]
    x.reverse()
    while len(x) > 0:
        print(f'Countdown: {x.pop(0)}')
        time.sleep(.5)
