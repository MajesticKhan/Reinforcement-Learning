#--------------------------------------------------------Import libraries
import gym
import numpy as np
from gym.utils import seeding
from gym import spaces
from Car import Car

#--------------------------------------------------------Class for Gym Environment
class lineFollower(gym.Env):

    # Create a gym environment to train on

    # initialize the gym environment
    def __init__(self):

        # initiate agent
        self.carAgent = Car()

        # define state size
        self.observation_space = spaces.Box(255,255,[256,256,3], dtype = np.uint8)

        # define action space
        self.action_space = spaces.Discrete(3)

        # define reward limitation TODO: FIX THE REWARD RANGE
        self.reward_range = (-1000000,1000000)


    def step(self,action):

        # take the action
        self.carAgent.steering(action, turningAngle = .2)

        # update the simulation
        self.carAgent.updateSimulation()

        # get current state
        self.obs  = self.carAgent.captureImage()

        # get reward
        if action == 0:
            self.reward = 1
        else:
            self.reward = .5

        if self.carAgent.middleCheck(self.obs):
            self.reward += 5
        else:
            self.reward = -1

        # Handle terminal states
        self.terminal = False
        terminalStatus = self.carAgent.terminalCheck(self.obs)

        if terminalStatus == "Blue":
            self.terminal = True
            self.reward   = -100

        if terminalStatus == "Green":
            self.terminal = True
            self.reward   = 40000

        print("Action: {} | Reward: {} | Terminal State {}".format(action, self.reward, self.terminal))

        # return updated cycle given input action
        return self.obs, self.reward, self.terminal, {}


    def seed(self, seed = None):

        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def reset(self):

        # reset observation
        self.carAgent.reset()

        # step through the simulation
        self.carAgent.updateSimulation()

        return self.carAgent.captureImage()


    def shutdown(self):

        # Stop the simulation
        self.carAgent.shutdown()