from threading import Condition
import datetime
import threading



class chatroom_manager:

    def __init__(self):
        self.rooms = {}
        self.room_count = 0
        self.manager_lock = Lock()

    def add_new_message(self, room_name, client_handle, client_id, client_msg_string):
        self.rooms[room_name].add_new_message(client_handle, client_id, client_msg_string)
        
    def get_new_messages(self, room_name, starting_id):
        #TODO add error checking
        return self.rooms[room_name].get_new_messages(starting_id)

    def join_room(self, room_name, client_handle, client_id):
        """
        Alerts room of new member. Returns tuple containing room reference and room condition
        for the client to wait on
        """
        #if room doesn't exist - create it
        self.manager_lock.acquire()
        if room_name not in self.rooms:
            self.rooms[room_name] = chatroom(room_name, self.room_count)
            self.room_count += 1
        self.manager_lock.release()

        join_message = "--|>%s has joined the room, say hello guys!"%client_handle
        room = self.rooms[room_name]
        room.add_new_message(client_handle, client_id, client_msg_string)
        return (room.room_ref, room.room_condition)

class chatroom:

    def __init__(self, room_name, room_ref)
        self.room_name = room_name
        self.room_ref = room_ref
        self.room_record = []
        self.room_record_count = 0
        self.room_condition = Condition()


    def add_new_message(self, client_handle, client_id, client_msg_string)
        """
        Adds a new message to the chat room - operation is atomic
        """
        new_message = message(client_handle, client_id, client_msg_string, self.room_record_count)

        self.room_condition.acquire()       #SAFE SECTION START#

        self.room_record.append(new_message)
        self.room_record_count += 1

        self.room_condition.release()       #SAFE SECTION END#


    def get_new_messages(self, starting_id)
        """
        Returns a list of messages from the starting_id to the current count 
        operation is atomic
        If starting_id is greater than the current room_record_count this will block
        until new messages arrive
        """
        messages = []

        self.room_condition_acquire()       #SAFE SECTION START#
        
        #will wait here until starting_id < room_record_count - as notified
        while starting_id > self.room_record_count:
            self.room_condition.wait()

        for i in range(i, len(self.room_record_count)):
            messages.append(self.room_record[i])

        self.room_condition.release()       #SAFE SECTION END#

        return messages

class message:
    def __init__(self, client_handle, client_id, client_msg_string, count)
        self.client_handle = client_handle
        self.client_id = client_id
        self.client_msg_value = client_msg_string
        self.client_msg_time = datetime.datetime.now()
        self.client_msg_id = count


