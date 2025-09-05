# Instant-Messenger

Chat Application that provides:
- Connection from multiple clients to a central server
- Clients can send messages and images
- Clients can create password protected rooms

# Installation

In order to avoid installing all the packages globaly they are installed in a python environment.
All required packets are in `requirements.txt`
Run `setup.sh` to setup the environment. This will install all the required dependencies in the environment.
Then run `source venv/bin/activate` to activate the environment.
Run `deactivate` to exit the environment.

Running main.py will prompt the user to run either a server or a client. 
One server must run for the application to run. By default it is accessible on the host ip address. 
It is also available on the loopback address (127.0.0.1)

# Disclaimer

As images are sent through sockets then cannot exceed a certain size. Functioning images can be found in ressources/
# Chatapp
