import datetime
from threading import Condition



class chatroom_manager:

    def __init__(self):
        self.rooms = {}
        self.room_count = 0

    def add_new_message(self, room_name, client_handle, client_id, client_msg_string):
        if room_name not in self.rooms:
            new_room = chatroom(room_name, self.room_count)
            self.room_count += 1

        self.rooms[room_name].add_new_message(client_handle, client_id, client_msg_string)
        
    def get_new_messages(self, room_name, starting_id):
        #TODO add error checking
        return self.rooms[room_name].get_new_messages(starting_id)

    def join_room(self, room_name, client_handle, client_id):
        """
        Alerts room of new member. Returns tuple containing room reference and room condition
        for the client to wait on
        """
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
        new_message = message(client_handle, client_id, client_msg_string, self.room_record_count)
        self.room_record.append(new_message)
        self.room_record_count += 1

    def get_new_messages(self, starting_id)
        """
        Returns a list of messages from the starting_id to the current count
        """
        messages = []
        for i in range(i, len(self.room_record_count)):
            messages.append(self.room_record[i])

        return messages

class message:
    def __init__(self, client_handle, client_id, client_msg_string, count)
        self.client_handle = client_handle
        self.client_id = client_id
        self.client_msg_value = client_msg_string
        self.client_msg_time = datetime.datetime.now()
        self.client_msg_id = count
