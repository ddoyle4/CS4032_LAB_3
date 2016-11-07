import threading

#GLOBAL VARIABLES
#flag for whether or not to kill the main service
kill_service_value = False
#for assigning new client ids
master_client_id = 0

#TODO - listening services lock?

class client_h:
    def __init__(self, client_id, client_socket, client_addr, server_info, lock, cr_handler):
        self.cr_handler = cr_handler            #master chatroom manager
        self.client_socket = client_socket      #client socket connection
        self.client_socket_wlock = Lock()       #write lock client socket
        self.global_variables_lock = lock       #write lock global data
        self.server_info = server_info
        self.client_addr = client_addr

        #client can subscribe to listen to a number of chat rooms - these are
        #handled concurrently. Threads saved to listening_services
        self.listening_services = []        

        self.client_id = client_id              #unique int identifier
        self.running = True
        self.run(client_addr)      #run service

    def run(self):
    
        while self.running:
                client_msg = self.client_socket.recv(65536)
                response = ""

                #TODO better regex checking
                if client_msg.startswith("HELO ", 0, 5):
                    response = self.process_helo_command(client_msg)
                elif client_msg == "KILL_SERVICE\n":
                    response = process_kill_service_command()
                elif client_msg.startswith("JOIN_CHATROOM", 0, 13):
                    response = self.parseChatCommand(client_msg)
                else:
                    response = "ERROR: unrecognised command\nGood day to you sir!"
                    self.running = False

                self.send_to_client(response)

        self.client_socket.close()

    def process_kill_service_command(self):
        print("Kill Service Command!!!")		

        self.kill_service()

        #then set flag to let main thread know we want to quit
        with self.global_variables_lock:
            global kill_service_value
            kill_service_value = True

    def kill_service(self):
        self.running = False

        #kill all listening services
        for thread in self.listening_services:
            thread.exit()


    def process_helo_command(self, client_msg):
        response = "%s\nIP:[%s]\nPort:[%s]\nStudent ID:[%s]\n"%(
                client_msg, 
                self.server_info["host"], 
                self.server_info["port"],
                self.server_info["sid"]
        )
        return response

    def process_join_command(self, args):

        #join the chatroom
        (name, count) = self.cr_handler.join_room(
                args["JOIN_CHATROOM"], 
                self.client_id)

        #start a listening service
        new_count = count - 1       
        new_listening_service = threading.Thread(
                target=self.listen_to_chatroom, 
                args=(name, new_count)).start()

        self.listening_services.append(new_listening_service)
        #TODO create proper return string
        return ""


    def send_to_client(self, msg):
        self.client_socket_wlock.acquire()
        self.client_socket.send(msg)
        self.client_socket_wlock.release()

    def listen_to_chatroom(self, room_name, starting_id)
        """
        To be spawned in new thread
        Simply listens to all chat room messages and reports back to client,
        starting from starting_id
        """
        running = True
        current_id = starting_id
        while running:
           messages = self.cr_handler.get_new_messages(room_name, current_id)
           current_id += len(messages)

            

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

