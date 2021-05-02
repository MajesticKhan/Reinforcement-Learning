import numpy as np
import gym
from gym import spaces
from gym.utils import seeding
from BeautifulBlueSquare.Blue import frame_environment

class simpleAvoidance(gym.Env):

    """
    Create environment
    """

    def __init__(self):
        # Set up frame work
        self.frame = frame_environment()

        # Create the reset frame
        self.obs = self.frame.reset_frame()

        # set up frame height/width
        self.height = self.frame.height
        self.width  = self.frame.width

        # define action space
        self.action_space = spaces.Discrete(3)

        # define observation space, which are images
        self.observation_space = spaces.Box(255,255,[self.frame.height,self.frame.width,3],dtype=np.uint8)

        # define action type
        self.move = [-1,0,1]

        # Define reward action
        self.reward_range = (-1, 1)

    def step(self, action):

        # update the agent movements
        self.state = self.frame.create_frame(self.move[action])

        # check terminal state
        self.terminal = self.frame.terminal_check()

        # update reward
        if not self.terminal:

            if action == 1:
                self.reward = 1
            else:
                self.reward = .9
        else:
            self.reward = -1

        # TODO: This needs to be part of frame_environment.terminal_check()
        # if its the last frame then stop
        if self.frame.frame_step == 800:
            self.terminal = True
            self.reward   = 1

        return self.state, self.reward, self.terminal, {}

    def seed(self, seed=None):


        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def reset(self):

        return self.frame.reset_frame()
