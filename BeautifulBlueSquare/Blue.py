import numpy as np

class frame_environment():

    def __init__(self):

        # Background information
        self.width  = 320
        self.height = 200

        # Agent's position
        self.agent_position = [50,290]
        self.agent_size     = 10

        # set up inital movement
        self.agent_movement = np.random.randint(1,90)

        # setup number of boxes
        self.num_boxes = 6

        # define how far the boxes are
        self.spread = 100

        # set up step
        self.frame_step = 0

    def background(self):

        # background
        self.state = np.tile(255,(self.height,self.width,3)).astype(np.uint8)

        # Set up lanes
        self.state[25:50,:]   = [255,0,0]
        self.state[-50:-25,:] = [255,0,0]

    def pipes(self):

        # create boxes
        box_position = [50, 20]
        box_width = 10
        box_height = 50

        for i in range(self.num_boxes):

            box_movement = (i * -self.spread) + self.frame_step
            box_switch = 0

            if box_movement < 0:
                continue

            if i % 2 != 0:
                box_switch = 50

            self.state[box_position[0] + box_switch:
                       box_position[0] + box_switch + box_height,

            box_position[1] + box_movement:
            box_position[1] + box_movement + box_width] = [0, 255, 0]

    def agent_update(self,action):

        # update movement
        self.agent_movement += action

        # create agent
        self.state[self.agent_position[0] + self.agent_movement:
                   self.agent_position[0] + self.agent_movement + self.agent_size,

                   self.agent_position[1]:
                   self.agent_position[1] + self.agent_size] = [0,0,255]

    def create_frame(self, action = 0, step = 1):

        # set up background
        self.background()

        # set up pipes
        self.pipes()

        # set up agent
        self.agent_update(action)

        # update the frame_step
        self.frame_step += step

        return self.state

    def terminal_check(self):

        self.terminal = False

        self.check = self.state[self.agent_position[0] + self.agent_movement -1 :
                                self.agent_position[0] + self.agent_movement + self.agent_size + 1,

                                self.agent_position[1] - 1:
                                self.agent_position[1] + self.agent_size + 1].sum()

        if  self.check!= 59160:
            self.terminal = True

        return self.terminal

    def reset_frame(self):

        # reset frame
        self.frame_step = 0

        # new random position
        self.agent_movement = np.random.randint(1, 90)

        # create fresh frame
        self.create_frame(step = 0)

        return self.state