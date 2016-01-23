# runserver file for application
# AdoptUsDogs - -- implementation of a catalog system
# 23/01/2016 Andrew Moore

from puppies import app


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
