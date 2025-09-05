import os

if __name__ == '__main__':
    while True:
        service = input("Select service to run:\n1: Server\n2: Client\n")
        match (service):
            case '1':
                os.system("python Server/server.py")
                break
            case '2':
                os.system("python Client/main.py")
                break
            case _:
                print("Enter Valid Commad")
