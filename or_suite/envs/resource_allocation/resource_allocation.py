'''
Implementation of a basic RL environment for continuous spaces.
Includes three test problems which were used in generating the figures.
'''

import numpy as np
import gym
from gym import spaces
import math


#------------------------------------------------------------------------------
'''Sequential Resource Allocation Problem for n agents with K commodities. 
Currently reward is Nash Social Welfare but in the future will integrate more options 
to determine a fair allocation '''

DEFAULT_ENV_CONFIG = {'K':2, 
    'num_agents':3,
    'weight_matrix':np.array([[1,0],[0,1],[1,1]]),
    'init_budget': 100*np.ones(2),
    'type_dist':lambda i: np.random.randint(50,size=3),
    'utility_function': lambda x,theta: np.dot(x,theta)
    }



class ResourceAllocationEnvironment(gym.Env):
  """
  Custom Environment that follows gym interface.
  """
  # Because of google colab, we cannot implement the GUI ('human' render mode)
  metadata = {'render.modes': ['human']}
  # Define constants for clearer code



  def __init__( self, config=DEFAULT_ENV_CONFIG):
        '''
        Initializes the Sequential Resource Allocation Environment

        weight_matrix - Weights predefining the commodity needs for each type, every row is a type vector
        K - number of commodities
        num_agents - Number of agents (also the length of an episode)
        init_budget - amount of each commodity the principal begins with
        endowments - how much of the commodities are given to the agents (rough corrolary of "size")
        type_dist: Function determining the types (preferences) of each agent, is a function from integer to integer
        u: utility function, given an allocation x and a type theta, u(x,theta) is how good the fit is
        '''
        super(ResourceAllocationEnvironment, self).__init__()
        self.weight_matrix = config['weight_matrix']
        self.num_types = config['weight_matrix'].shape[0]
        self.num_commodities = config['K']
        self.epLen = config['num_agents']
        self.budget = config['init_budget']
        self.type_dist = config['type_dist']
        self.utility_function = config['utility_function']
        self.starting_state = (config['init_budget'],self.type_dist(0))
        self.state = self.starting_state
        self.timestep = 0



        # Action space will be choosing Kxn-dimensional allocation matrix
        self.action_space = spaces.Box(low=0, high=max(self.budget),
                                        shape=(self.num_types,self.num_commodities), dtype=np.float32)
        # First K entries of observation space is the remaining budget, next K is the type of the location
        self.observation_space = spaces.Box(low=0, high=max(self.budget),
                                        shape=(2*self.num_commodities+1,), dtype=np.float32)

  def reset(self):
        """
        Important: the observation must be a numpy array
        :return: (np.array)
        """
        # Initialize the timestep
        self.timestep = 0
        self.state = self.starting_state

        return self.starting_state
        ## return a spaces.box object here


  def step(self, action):
        '''
        Move one step in the environment

        Args:
        action - matrix - chosen action (each row how much to allocate to prev location)
        Returns:
            reward - double - reward
            newState - int - new state
            done - 0/1 - flag for end of the episode
        '''
        (old_budget,old_type) = self.state
        # new state is sampled from the arrivals distribution
        allocation = np.array(action)
  

        # print('old_state' , old_state)
        # print('new_type' , new_type)

        # TODO: INTEGRATE OTHER FAIRNESS METRICS
        
        reward = (1/np.sum(old_type))*sum(
            [old_type[theta]*np.log(self.utility_function(allocation[theta,:],self.weight_matrix[theta,:]) for theta in range(self.num_types))]
            )
        print("Reward: %s"%reward)
        (new_budget, new_type) = (
            old_budget-np.sum(allocation, axis=0), self.type_dist(self.timestep))

        # print('New state' , newState)
        # Cost is a linear combination of the distance traveled to the action
        # and the distance served to the pickup
        # Optionally we can pass additional info, we are not using that for now
        info = {'type' : new_type}

        if self.timestep <= self.epLen:
            pContinue = True
            self.reset()
        else:
            pContinue = False

        
        self.state = (new_budget, new_type)
        #not sure how to make it such the sum across all types is <= budget
        self.action_space = spaces.Box(low=0, high=max(new_budget),
                                shape=(self.num_types,self.num_commodities), dtype=np.float32)
        
        self.timestep += 1
        #return self.state and also a box object
        # can probably return self.state

        return self.state, reward,  pContinue, info

  def render(self, mode='console'):
    if mode != 'console':
      raise NotImplementedError()


  def close(self):
    pass


#-------------------------------------------------------------------------------
# Benchmark environments used when running an experiment

#TODO: Make wrapper passing all arguments: e.g.
# def make_ambulanceEnvMDP(epLen = 5  , arrival_dist = lambda x : np.random.rand() ,alpha = 0.25 , starting_state = np.array([0]) , num_ambulance = 1)


def make_resource_allocationEnvMDP(config=DEFAULT_ENV_CONFIG):
    return ResourceAllocationEnvironment(config)