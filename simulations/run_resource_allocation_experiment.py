import sys

sys.path.append('../')

import numpy as np
import gym

import or_suite

from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy




''' Defining parameters to be used in the experiment'''


DEFAULT_ENV_CONFIG = or_suite.envs.env_configs.resource_allocation_simple_config
#DEFAULT_ENV_CONFIG = or_suite.envs.env_configs.resource_allocation_default_config

# #TODO: Edit algo-list to be the names of the algorithms you created
problem_list = ['simple']#,'default']


for problem in problem_list:
    nEps = 2
    numIters = 1
    #initialize resource allocation environment w/ default parameters
    env = gym.make('Resource-v0', config = DEFAULT_ENV_CONFIG)
    epLen = env.epLen
    # algo_information = {'Random': or_suite.agents.rl.random.randomAgent(), 'Equal_Allocation': or_suite.agents.resource_allocation.equal_allocation.equalAllocationAgent(epLen, DEFAULT_ENV_CONFIG)}
    algo_information = {'Equal_Allocation': or_suite.agents.resource_allocation.equal_allocation.equalAllocationAgent(epLen, DEFAULT_ENV_CONFIG)}

    DEFAULT_SETTINGS = {'seed': 1, 'recFreq': 1, 'dirPath': '../data/allocation/', 'deBug': False, 'nEps': nEps, 'numIters': numIters, 'saveTrajectory': True, 'epLen' : epLen}


    path = {}
    for algorithm in algo_information:
        DEFAULT_SETTINGS['dirPath'] = '../data/allocation_%s_%s'%(algorithm,problem)
        or_suite.utils.run_single_algo(env, algo_information[algorithm], DEFAULT_SETTINGS)




# #below is work on the PPO algorithm, kinda not the greatest atm
# env = gym.make('Resource-v0', config = DEFAULT_ENV_CONFIG)
# model = PPO(MlpPolicy, env, verbose=1, gamma=1)
# model.learn(total_timesteps=1000)

# env = gym.make('Ambulance-v1')
# n_episodes = 100
# res_mean, res_std = evaluate_policy(model, env, n_eval_episodes=n_episodes)

# print(-res_mean, '+/-', 1.96*res_std/np.sqrt(n_episodes))