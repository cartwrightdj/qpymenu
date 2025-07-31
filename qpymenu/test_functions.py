
def hello_world():
    print('Hello World')

def read_text_file(filepath):
    with open(filepath) as f:
        print(f.readlines())

def about():
    print("qPyMenu\n\n"
          "Quick and easy menuing ssytem for python")
