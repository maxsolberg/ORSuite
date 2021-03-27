import time
from shutil import copyfile
import pandas as pd
import tracemalloc
import numpy as np
import pickle
import os

class SB_Experiment(object):

    def __init__(self, env, model, dict):
        '''
        A simple class to run a MDP Experiment with a stable baselines model.
        Args:
            env - an instance of an Environment
            agent - an agent
            dict - a dictionary containing the arguments to send for the experiment, including:
                seed - random seed for experiment
                recFreq - proportion of episodes to save to file
                targetPath - path to the file for saving
                deBug - boolean of whether to include
                nEps - number of episodes
                numIters - the number of iterations to run experiment
                saveTrajectory - boolean of whether to save trajectory information
        '''
        # assert isinstance(env, environment.Environment)

        self.seed = dict['seed']
        self.epFreq = dict['recFreq']
        self.dirPath = dict['dirPath']
        # self.targetPath = dict['targetPath']
        self.deBug = dict['deBug']
        self.nEps = dict['nEps']
        self.env = env
        self.epLen = dict['epLen']
        self.num_iters = dict['numIters']
        self.save_trajectory = dict['saveTrajectory']
        self.agent = agent
        # print('epLen: ' + str(self.epLen))
        self.data = np.zeros([dict['nEps']*self.num_iters, 5])


        if self.save_trajectory:
            self.trajectory = []

        np.random.seed(self.seed)

    # Runs the experiment
    def run(self):
        print('**************************************************')
        print('Running experiment')
        print('**************************************************')


        index = 0
        traj_index = 0
        for i in range(self.num_iters):
            self.agent.reset()
            self.agent.update_config(self.env, self.env.get_config())
            for ep in range(1, self.nEps+1):
                # print('Episode : ' + str(ep))
                # Reset the environment
                self.env.reset()
                oldState = self.env.state
                epReward = 0

                self.agent.update_policy(ep)

                done = False
                h = 0

                start_time = time.time()
                tracemalloc.start()

                while (not done) and h < self.epLen:
                    # Step through the episode
                    if self.deBug:
                        print('state : ' + str(oldState))
                    action = self.agent.pick_action(oldState, h)
                    if self.deBug:
                        print('action : ' + str(action))

                    newState, reward, done, info = self.env.step(action)
                    epReward += reward

                    self.agent.update_obs(oldState, action, reward, newState, h, info)

                    if self.save_trajectory: # 
                        # turn into list, make self.trajectory a list, append. try pickle
                        record = {'iter': i, 'episode': ep, 'step' : h, 'oldState' : oldState, 'action' : action, 'reward' : reward, 'newState' : newState, 'info' : info}
                        self.trajectory.append(record)

                    oldState = newState
                    h = h + 1

                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                end_time = time.time()
                
                if self.deBug:
                    print('final state: ' + str(newState))
                # print('Total Reward: ' + str(epReward))

                # Logging to dataframe
                # if ep % self.epFreq == 0:
                # print('## LOGGING TO DATA FRAME ##')
                # print('Episode : ' + str(ep))
                # print('Total Reward: ' + str(epReward))
                # print('##                       ##')
                self.data[index, 0] = ep-1
                self.data[index, 1] = i
                self.data[index, 2] = epReward
                self.data[index, 3] = current
                self.data[index, 4] = ((end_time) - (start_time)) * (10**9)

                index += 1

        print('**************************************************')
        print('Experiment complete')
        print('**************************************************')

    # Saves the data to the file location provided to the algorithm
    def save_data(self): # TODO: Best way of getting directory locations for both paths? kwargs? 
                        # remove targetPath - force into data.csv and traj.csv
        print('**************************************************')
        print('Saving data')
        print('**************************************************')

        print(self.data)


        dir_path = self.dirPath

        data_loc = 'data.csv'
        traj_loc = 'trajectory.obj'


        if self.save_trajectory:

            dt = pd.DataFrame(self.data, columns=['episode', 'iteration', 'epReward', 'memory', 'time'])
            dt = dt[(dt.T != 0).any()]

            filename = os.path.join(dir_path, traj_loc)

            print('Writing to file ' + data_loc)
        else:

            dt = pd.DataFrame(self.data, columns=['episode', 'iteration', 'epReward', 'memory', 'time'])
            dt = dt[(dt.T != 0).any()]
            print('Writing to file ' + data_loc)

        if os.path.exists(dir_path):
            dt.to_csv(os.path.join(dir_path,data_loc), index=False, float_format='%.2f', mode='w')
            if self.save_trajectory:
                outfile = open(filename, 'wb')
                pickle.dump(self.trajectory, outfile)
                outfile.close()
        else:
            os.makedirs(dir_path)
            dt.to_csv(os.path.join(dir_path, data_loc), index=False, float_format='%.2f', mode='w')
            if self.save_trajectory:
                outfile = open(filename, 'wb')
                pickle.dump(self.trajectory, outfile)
                outfile.close()

        print('**************************************************')
        print('Data save complete')
        print('**************************************************')

        return dt