import discord
import json
import os

from datetime import datetime
from typing import Optional
from run import absolute_path


'''
Simple database implementation
Using json files to store the data (yeah, simple lmao)
'''

def fix_log_existence(guild_id: str):
    """
    Creates database for server with [guild_id] if it doesn't exist
    :param guild_id: server ID
    :return: None
    """
    if not os.path.exists(absolute_path + '/JsonBases/{0}.json'.format(guild_id)):
        with open(absolute_path + '/JsonBases/{0}.json'.format(guild_id), 'w+', encoding="utf-8") as json_file:
            json.dump({}, json_file, ensure_ascii=False)


def save_data(func):
    """
    Saves user_data to database when func finishes it's job
    :param func: function
    :return: decorated function
    """

    def decorated(self, *args):
        func(self, *args)
        save_user_history(self.guild, self.user, self.history)

    return decorated


def get_user_history(guild: discord.Guild, user: discord.User) -> Optional[dict]:
    """
    Getting information about the user from the database
    :param guild: Server Object
    :param user: User Object
    :return: user's stats
    """
    guild_id = str(guild.id)

    fix_log_existence(guild_id)
    with open(absolute_path + '/JsonBases/{0}.json'.format(guild_id), 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    if str(user.id) not in data:
        return None
    return data[str(user.id)]


def get_user_history_by_id(guild: discord.Guild, user_id: str) -> Optional[dict]:
    """
    Getting user stats with their Discord ID.
    This funtion is needed in case of banned users
    :param guild: Server Object
    :param user_id: user ID
    :return: None
    """
    guild_id = str(guild.id)
    fix_log_existence(guild_id)
    with open(absolute_path + '/JsonBases/{0}.json'.format(guild_id), 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    if user_id not in data:
        return None
    return data[user_id]


def save_user_history(guild: discord.Guild, user: discord.User, history: dict) -> None:
    """
    Saving user history
    :param guild: Server Object
    :param user: User Object
    :param history: their stats
    :return: None
    """
    guild_id = str(guild.id)
    fix_log_existence(guild_id)
    with open(absolute_path + '/JsonBases/{0}.json'.format(guild_id), 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    data[str(user.id)] = history

    with open(absolute_path + '/JsonBases/{0}.json'.format(guild_id), 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False)


class UserRecord:
    def __init__(self, user: discord.User, guild: discord.Guild):
        """
        User staticstics object
        """
        self.user = user
        self.guild = guild
        self.history = get_user_history(self.guild, self.user)

        if not self.history:
            self.generate_history()

    @save_data
    def clear_history(self):
        """
        Clear user statistics
        """
        self.history = dict()

    @save_data
    def generate_history(self):
        """
        Generate history for new user in db
        :return: None
        """
        self.history = dict()
        self.history["id"] = self.user.id
        self.history["name"] = self.user.name
        self.history["notes"] = []
        self.history["records"] = []

    @save_data
    def set_warn(self, warn_text):
        """
        Creates a warning for the user
        :param warn_text: warning reason
        :return: None
        """
        warning = dict()
        warning['record_type'] = 'warning'
        warning['reason'] = warn_text
        warning['time'] = str(datetime.now())
        self.history['records'].append(warning)

    @save_data
    def set_note(self, note_text):
        """
        Creates a note for the user
        :param note_text: note reason
        :return: None
        """
        note = dict()
        note['record_type'] = 'note'
        note['time'] = str(datetime.now())
        note['note'] = note_text
        self.history['notes'].append(note) 

    @save_data
    def set_mute(self, duration, reason):
        """
        Creates a mute record in db
        :param duration: duration (in min)
        :param reason: mute reason
        :return: None
        """
        mute = dict()
        mute['record_type'] = 'mute'
        mute['duration'] = duration
        mute['reason'] = reason
        mute['time'] = str(datetime.now())
        self.history['records'].append(mute)

    @save_data
    def set_ban(self, reason):
        """
        Creates a ban record in db
        :param reason: ban reason
        :return: None
        """
        ban = dict()
        ban['record_type'] = 'ban'
        ban['reason'] = reason
        ban['time'] = str(datetime.now())
        self.history['records'].append(ban)

    @save_data
    def clear_record(self, time_of_record: str):
        """
        Deletes users record by the time of it
        :param time_of_record: time 
        :return: None
        """
        for record in self.history['records']:
            if record['time'] == time_of_record:
                self.history['records'].remove(record)
                return
        for record in self.history['notes']:
            if record['time'] == time_of_record:
                self.history['notes'].remove(record)
                return
