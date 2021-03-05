'''
All agents should inherit from the Agent class.
- FiniteHorizonAgent = finite *known* horizon H
'''


class Agent(object):

    def __init__(self):
        pass

    def update_obs(self, obs, action, reward, newObs):
        '''Add observation to records'''

    def update_policy(self, h):
        '''Update internal policy based upon records'''

    def pick_action(self, obs):
        '''Select an action based upon the observation'''

