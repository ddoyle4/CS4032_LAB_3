from threading import Condition
import datetime
import threading



class chatroom_manager:

    def __init__(self):
        self.rooms = {}
        self.room_count = 1
        self.manager_lock = threading.Lock()

    def add_new_message(self, room_name, client_handle, client_id, client_msg_string):
        self.rooms[room_name].add_new_message(client_handle, client_id, client_msg_string)
        
    def admin_add_new_message(self, room_name, msg):
        self.rooms[room_name].add_new_message("SERVER ADMIN", "-1", msg)

    def get_new_messages(self, room_name, starting_id):
        #TODO add error checking
        return self.rooms[room_name].get_new_messages(starting_id)

    def join_room(self, room_name, client_handle, client_id):
        """
        TODO
        """
        #if room doesn't exist - create it
        self.manager_lock.acquire()
        if room_name not in self.rooms:
            print "creating room \"%s\", at the request of \"%s\""%(room_name,client_handle)
            self.rooms[room_name] = chatroom(room_name, self.room_count)
            self.room_count += 1
        self.manager_lock.release()

        #send message to room as server admin
        #join_message = "%s has joined the room, say hello guys!"%client_handle
        room = self.rooms[room_name]
        #room.add_new_message(client_handle, client_id, join_message)
        return (room.room_name, room.room_ref, room.room_record_count)

    def close_all(self):
        """
        close all chatrooms - kills all listening services
        """
        with self.manager_lock:
            for name, room in self.rooms.iteritems():
                room.add_new_message("SERVER ADMIN", "-1", "WE'RE GOING DOWN!")
                try:
                    room.room_condition.acquire()
                    room.kill_room()
                    room.room_condition.notify()
                finally:
                    room.room_condition.release()

class chatroom:

    def __init__(self, room_name, room_ref):
        self.room_name = room_name
        self.room_ref = room_ref
        self.room_record = []
        self.room_record_count = 0
        self.room_condition = Condition()
        self.room_is_active = True

    def add_new_message(self, client_handle, client_id, client_msg_string):
        """
        Adds a new message to the chat room - operation is atomic
        """
        new_message = message(client_handle, client_id, client_msg_string, self.room_record_count)
        self.room_condition.acquire()       #SAFE SECTION START#

        self.room_record.append(new_message)
        self.room_record_count += 1
        self.room_condition.notifyAll()
        self.room_condition.release()       #SAFE SECTION END#

    def kill_room(self):
        self.room_is_active = False

    def get_new_messages(self, starting_id):
        """
        Returns a list of messages from the starting_id to the current count 
        operation is atomic
        If starting_id is greater than the current room_record_count this will block
        until new messages arrive
        """
        running_id = starting_id
        messages = []

        self.room_condition.acquire()       #SAFE SECTION START#
        
        #will wait here until running_id < room_record_count - as notified
        while (running_id >= self.room_record_count) and self.room_is_active:
            self.room_condition.wait()

        for i in range(running_id, self.room_record_count):
            messages.append(self.room_record[i])

        self.room_condition.release()       #SAFE SECTION END#

        return messages

class message:
    def __init__(self, client_handle, client_id, client_msg_string, count):
        self.client_handle = client_handle
        self.client_id = client_id
        self.client_msg_value = client_msg_string + '\n' + '\n'
        self.client_msg_time = datetime.datetime.now()
        self.client_msg_id = count


