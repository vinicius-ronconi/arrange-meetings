from abc import ABCMeta, abstractmethod


class IUserPreferencesDao(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_user_preferences(self, user_id):
        """
        :type user_id: int
        :rtype: users.dao.beans.UserPreferences
        """
