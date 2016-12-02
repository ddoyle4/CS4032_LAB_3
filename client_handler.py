import threading
import random
import re
import collections
import time

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
        self.client_socket.setblocking(0)       #set the socket to non-blocking
        self.client_socket_wlock = threading.Lock()       #write lock client socket
        self.global_variables_lock = lock       #write lock global data
        self.server_info = server_info
        self.client_addr = client_addr

        #client can subscribe to listen to a number of chat rooms - these are
        #handled concurrently. Threads saved to listening_services
        # thread saved in a dict pointed to by the room name
        # format:
        #   room : {Thread service_thread}
        self.listening_services = {}           
        self.listening_serices_lock = threading.Lock()

        self.client_id = client_id              #unique int identifier
        self.client_addr = client_addr
        self.running = True
        self.run()      #run service

    def run(self):
    
        while self.running:
            self.check_for_kill_signal()
            try: #process client message if present
                 
                client_msg = self.client_socket.recv(65536)
                response = ""
                respond = True
                print "new client msg:\n----\n%s\n----\n"%(str(client_msg))

                #TODO better regex checking
                if client_msg.startswith("HELO ", 0, 5):
                    response = self.process_helo_command(client_msg)
                    respond = True
                elif client_msg == "KILL_SERVICE\n":
                    response = self.process_kill_service_command()
                    respond = False
                elif client_msg.startswith("JOIN_CHATROOM", 0, 13):
                    args = self.parseChatCommand(client_msg)
                    response = self.process_join_command(args)
                    respond = True
                elif client_msg.startswith("LEAVE_CHATROOM", 0, 14):
                    args = self.parseChatCommand(client_msg)
                    response = str(self.process_leave_command(args))
                    #response = response.strip()
                    respond =  False
                elif client_msg.startswith("CHAT", 0, 4):
                    args = self.parseChatCommand(client_msg)
                    response = self.process_chat_command(args)
                    respond = True
                elif client_msg.startswith("DISCONNECT", 0, 10):
                    args = self.parseChatCommand(client_msg)
                    response = self.process_disconnect_command(args)
                    respond = False
                else:
                    #response = self.generate_error_message(1, "unrecognised command")
                    print "unrecognised command"
                    respond = ""
                    respond = False
                    #self.running = False

                if respond:
                    print "sending this to client:\n----\n%s----\n"%(response)
                    self.send_to_client(response)
            except IOError as e:  # otherwise just sleep for a while
                if e.errno == 11:
                    #should sleep when not working
                    time.sleep(0.05)   
        
        self.client_socket.close()


    def process_disconnect_command(self, args):
        #kill main thread
        self.running = False
        for name, value in self.listening_services.iteritems():
            self.stop_listening_service(name, args["CLIENT_NAME"])
        return "OK"


    def process_chat_command(self, args):
        room_name = self.reverse_listening_service_by_ref(int(args["CHAT"]))
        self.cr_handler.add_new_message(
                room_name, 
                args["CLIENT_NAME"], 
                args["JOIN_ID"], 
                args["MESSAGE"])
        return "OK"

    def generate_error_message(self, errno, msg):
        args = collections.OrderedDict()
        args["ERROR_CODE"] = str(errno)
        args["ERROR_DESCRIPTION"] = msg
        return self.generateChatCommand(args)

    def process_leave_command(self, args):
        """
        Flushes any messages yet to be delivered to client and
        removes the listening_service for that client in that room
        """
        
        #response_dict = collections.OrderedDict()
        #response_dict["LEFT_CHATROOM"] = args["LEAVE_CHATROOM"]
        #response_dict["JOIN_ID"] = args["JOIN_ID"]
        #return self.generateChatCommand(response_dict).strip()

        respond_string = str("LEFT_CHATROOM:%s\nJOIN_ID:%s\n"%(str(args["LEAVE_CHATROOM"]), args["JOIN_ID"]))
        print "SPECTIAL LEAVE COMMAND SENDING\n----"
        self.client_socket.send(respond_string)
        print "\n---"

        
        room_name = self.reverse_listening_service_by_ref(int(args["LEAVE_CHATROOM"]))
        self.stop_listening_service(room_name, args["CLIENT_NAME"])
        return respond_string

    def stop_listening_service(self, room_name, client_name):
        """
        Stops the listening service for a particular room
        """
        print "dave 1"
        with self.listening_serices_lock:
            print "dave 2"
            
            if self.listening_services[room_name][2]:
                print "dave 3"
                #inform chatroom
                msg = "%s has left!"%client_name
                print "dave 4"
                #self.cr_handler.admin_add_new_message(room_name, msg)
                self.cr_handler.add_new_message(room_name, client_name, 2, msg)
                print "dave 5"
                print "dave 6"

        #allow message to propogate to the client
        time.sleep(4)
        with self.listening_serices_lock:
            #stop listening service
            old_value = self.listening_services[room_name]
            new_value = (old_value[0], old_value[1], False)
            self.listening_services[room_name] = new_value

    def reverse_listening_service_by_ref(self, ref):
        """
        returns the room name based on the room ref
        """
        thread = None
        for key, value in self.listening_services.iteritems():
            if value[0] == ref:
                return key

        return thread

    def process_kill_service_command(self):
        print("Kill Service Command!!!")		

        self.kill_service()

        #then set flag to let main thread know we want to quit
        with self.global_variables_lock:
            global kill_service_value
            kill_service_value = True

        return "KILLING"

    def kill_service(self):
        self.running = False

    def check_for_kill_signal(self):
        """
        checks if the kill signal has been set and stops client service if
        it is
        """
        with self.global_variables_lock:
            if kill_service_value:
                self.running = False


    def process_helo_command(self, client_msg):
        response = "%sIP:%s\nPort:%s\nStudentID:%s\n"%(
                client_msg, 
                self.server_info["host"], 
                self.server_info["port"],
                self.server_info["sid"]
        )
        return response

    def process_join_command(self, args):

        #join the chatroom
        (name, ref, count) = self.cr_handler.join_room(
                args["JOIN_CHATROOM"], 
                args["CLIENT_NAME"],
                self.client_id)
        #start a listening service
        new_listening_service = threading.Thread(
                target=self.listen_to_chatroom, 
                args=(ref, name, count)).start()

        #register listening service
        with self.listening_serices_lock:
            self.listening_services[name] = (int(ref), new_listening_service, True)

        #formulate correct response
        response_dict = collections.OrderedDict()

        response_dict["JOINED_CHATROOM"] = name
        response_dict["SERVER_IP"] = self.server_info["host"]
        response_dict["PORT"] = self.server_info["port"]
        response_dict["ROOM_REF"] = ref
        response_dict["JOIN_ID"] = str(self.client_id)

        #inform chatroom of new member
        new_msg = "client1 has joined this chatroom."#%args["CLIENT_NAME"] 
        self.cr_handler.add_new_message(
                args["JOIN_CHATROOM"], 
                args["CLIENT_NAME"], 
                self.client_id, 
                new_msg)
            

        return self.generateChatCommand(response_dict)


    def send_to_client(self, msg):
        self.client_socket_wlock.acquire()
        self.client_socket.send(msg)
        self.client_socket_wlock.release()

    def listen_to_chatroom(self, room_ref, room_name, starting_id):
        """
        To be spawned in new thread
        Simply listens to all chat room messages and reports back to client,
        starting from starting_id
        """
        
        running = True
        current_id = starting_id

        while running:
            #old count 1 after set up
            messages = self.cr_handler.get_new_messages(room_name, current_id)
            current_id += len(messages)
            

            #check if leaving service
            with self.listening_serices_lock:
                if not self.listening_services[room_name][2]:
                    running = False

            if running:        
                #NOTE - sending each message individually like this would be wasteful if there
                #were many messages here, but there should usually only be 1
                for message in messages:
                    command = collections.OrderedDict()
                    
                    command["CHAT"] = room_ref
                    command["CLIENT_NAME"] =  message.client_handle
                    command["MESSAGE"] = message.client_msg_value

                    response = self.generateChatCommand(command)
                    print "sending this to client:\n----\n%s----\n"%(response)
                    self.send_to_client(response)



    #TODO move these methods to a new class that checks validity of messages
    # and generates an error message if necessary to return to client
    def parseChatCommand(self, command):
        regex = "([A-Za-z0-9\-\_]+)\:([A-Za-z0-9\-\_\ ]+)"
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
            clean_key = str(key).strip()
            clean_value = str(key).strip()
            command_string += str(key) + ":"
            command_string += str(value) + "\n"
        return command_string

