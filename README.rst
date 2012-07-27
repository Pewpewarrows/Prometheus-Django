Prometheus-Django
=================

Django mold for the Prometheus project generator

Web development made easy!


Note that in order to have pyOpenSSL work with Python2.7, the SocketServer.py
file must be manually edited for your current python environment. For pybrew
users, this file will be located in:

~/.pythonbrew/pythons/Python-2.7.3/lib/python2.7/SocketServer.py

Edit line 459 to be:

    request.shutdown()

For reference, to reverse this change modify the line back to:

    request.shutdown(socket.SHUT_WR)


To download new packages from pip, use the following command:

    pip install -d vendor/python/ package_name
