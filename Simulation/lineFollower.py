import gym
import numpy as np
from gym.utils import seeding
from gym import spaces

class lineFollower(gym.Env):

    # initialize
    def __init__(self, Car):

        # initiate agent
        self.carAgent = Car()

        # define state size
        self.observation_space = spaces.Box(255,255,[256,256,3], dtype = np.uint8)

        # define action space
        self.action_space = spaces.Discrete(3)

        # define reward limitation
        self.reward_range = (-10000,100)

    def step(self,action):

        # take the action
        self.carAgent.steering(action, turningAngle = .2)

        # update the simulation
        self.carAgent.updateSimulation()

        # get current state
        self.obs = self.carAgent.captureImage()

        # get reward
        self.reward = 1

        # Handle terminal states
        self.terminal = False
        terminalStatus = self.carAgent.terminalCheck(self.obs)

        if terminalStatus == "Blue":
            self.terminal = True
            self.reward   = -100

        if terminalStatus == "Green":
            self.terminal = True
            self.reward   = 100000

        print("Action: {} | Reward: {} | Terminal State {}".format(action, self.reward, self.terminal))
        # return updated cycle
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
        self.carAgent.shutdown()
