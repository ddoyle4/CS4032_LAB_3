
#GLOBAL VARIABLES
#flag for whether or not to kill the main service
kill_service_value = False

class client_h:
    def __init__(self, client_socket, client_addr, server_info, lock, cr_handler):
        self.cr_handler = cr_handler
        self.run(client_socket, client_addr, server_info, lock)


    def run(self, client_socket, client_addr, server_info, lock):
        running = True
    
        while running:
                client_msg = client_socket.recv(65536)
                response = ""
                #start of command logic
                if client_msg.startswith("HELO ", 0, 5):
                        response = "%s\nIP:[%s]\nPort:[%s]\nStudent ID:[%s]\n"%(
                                client_msg, 
                                server_info["host"], 
                                server_info["port"],
                                server_info["sid"]
                        )
                elif client_msg == "KILL_SERVICE\n":
                        print("Kill Service Command!!!")		
                        lock.acquire()
                        global kill_service_value
                        kill_service_value = True
                        lock.release()	
                        running = False
                elif client_msg.startswith("JOIN_CHATROOM", 0, 13):
                    command = self.parseChatCommand(client_msg)
                    self.cr_handler.join_room(command["JOIN_CHATROOM"], self.get_client_id())

                else:
                        response = "ERROR: unrecognised command\nGood day to you sir!"
                        running = False

                client_socket.send(response)

        client_socket.close()


    def parseChatCommand(self, command):
        regex = "([A-Za-z0-9\-\_]+)\:\ \[([A-Za-z0-9\-\_\ ]+)\]"
        lines = command.split("\n")
        command_dict = {}
        for line in lines:
            matches = re.match(regex, line, re.M|re.I)
            if matches:
                command_dict[str(matches.group(1))] = str(matches.group(2))
        return command_dict


    def generateChatCommand(self, command_dict):
        command_string = ""
        for key, value in command_dict.iteritems():
            command_string += key + ": ["
            command_string += value + "]\n"
        return command_string

