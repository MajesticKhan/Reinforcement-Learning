import gym
import numpy as np
from gym.utils import seeding
from pyrep import PyRep, objects
from gym import spaces
from stable_baselines import PPO2
import os, sys
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.callbacks import BaseCallback
from stable_baselines.common.evaluation import evaluate_policy
from multiprocessing import Process, Queue
from multiprocessing import Manager
from stable_baselines.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold


ci_build_and_not_headless = False
try:
    from cv2.version import ci_build, headless
    ci_and_not_headless = ci_build and not headless
except:
    pass
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/home/gal/coppelia/CoppeliaSim_Edu_V4_2_0_Ubuntu18_04"
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_FONTDIR")

class Car():

    # initialize
    def __init__(self, pathToScene = '/home/gal/coppelia/project/legocar.ttt'):
        """
        Initialize the parameters to start the simulation
        :param pathToScene:
        """
        # Start the simulator
        SCENE_FILE = pathToScene
        self.pr    = PyRep()
        self.pr.launch(SCENE_FILE, headless = False)
        self.pr.start()

        # Set the car shape
        self.car = objects.shape.Shape("car")

        # establish steering
        self.front_right_steer = objects.joint.Joint("front_right_steer")
        self.rear_right_steer  = objects.joint.Joint("rear_right_steer")
        self.front_left_steer  = objects.joint.Joint("front_left_steer")
        self.rear_left_steer   = objects.joint.Joint("rear_left_steer")

        # establish motor
        self.front_right_motor = objects.joint.Joint("front_right_motor")
        self.rear_right_motor  = objects.joint.Joint("rear_right_motor")
        self.front_left_motor  = objects.joint.Joint("front_left_motor")
        self.rear_left_motor   = objects.joint.Joint("rear_left_motor")

        # establish steering position for rear wheels TODO: motor should be disabled
        self.rear_right_steer.set_joint_target_velocity(0)
        self.rear_left_steer.set_joint_target_velocity(0)

        # Fix motor speed
        self.front_right_motor.set_joint_target_velocity(1)
        self.rear_right_motor.set_joint_target_velocity(1)
        self.front_left_motor.set_joint_target_velocity(1)
        self.rear_left_motor.set_joint_target_velocity(1)

        # Set Camera
        self.camera = objects.vision_sensor.VisionSensor("frontCamera")


    def captureImage(self):

        """
        :return: return current image based on camera feed
        """

        return np.uint8(self.camera.capture_rgb() * 255.)


    def steering(self, action, turningAngle = .2):
        """
        :param action       : either turn left or right
        :param turningAngle : angle of turning the wheel
        """

        # If action is left
        if action == 0:
            self.front_left_steer.set_joint_target_position(turningAngle)
            self.front_right_steer.set_joint_target_position(turningAngle)

        # if action is right
        elif action == 1:
            self.front_left_steer.set_joint_target_position(-turningAngle)
            self.front_right_steer.set_joint_target_position(-turningAngle)

        # if action is no steering
        elif action == 2:
            self.front_left_steer.set_joint_target_position(0)
            self.front_right_steer.set_joint_target_position(0)

        else:
            raise ValueError("Too Many actions")

    def terminalCheck(self,test):

        # focus on smaller slice of image
        test = test[-40:230]

        # Get the left and right boundaries of the car's hood
        left = test[:, 55, :]
        right = test[:, 198, :]

        # check if there is any blue
        left_check_blue = ((left[:, 0] <= 10) & (left[:, 1] <= 10) & (200 <= left[:, 2])).sum()
        right_check_blue = ((right[:, 0] <= 10) & (right[:, 1] <= 10) & (200 <= right[:, 2])).sum()

        # check if there is any Green
        check_green = ((test[:, :, 0] <= 10) & (200 <= test[:, :, 1]) & (test[:, :, 2] <= 10)).sum()

        if (left_check_blue + right_check_blue) != 0:
            return "Blue"

        if (check_green) != 0:
            return "Green"

        return None

    def updateSimulation(self):

        # Step through the simulation
        self.pr.step()


    def reset(self):
        """
        Return the car to the original position
        """
        self.car.set_pose([6.7750e+00,6.4750e+00,1.7500e-01,0,0, 7.08272636e-01 , 7.05938995e-01])

    def shutdown(self):

        """
        Shutdown the simulation
        """
        self.pr.stop()
        self.pr.shutdown()


class lineFollower(gym.Env):

    # initialize
    def __init__(self):

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





def evaluate_policy_process(model, n_eval_episodes,deterministic, queue):
    eval_env = lineFollower()
    print("TEST _ !")
    mean_reward, _ = evaluate_policy(
        model,
        eval_env,
        n_eval_episodes = n_eval_episodes,
        deterministic   = deterministic
    )
    eval_env.shutdown()
    print("TEST _ 2222")
    queue.put(mean_reward)

class eval(BaseCallback):

    def __init__(self,
                 n_eval_episodes: int = 1,
                 deterministic: bool  = True,
                 reward_threshold     = None,
                 path                 = None,
                 eval_freq            = 10,
                 queue                = None):

        super().__init__()
        self._n_eval_episodes  = n_eval_episodes
        self._eval_freq        = eval_freq
        self._deterministic    = deterministic
        self._reward_threshold = reward_threshold
        self._path             = path
        self.queue             = queue

    def _on_step(self) -> bool:
        print(self.n_calls)
        if self.n_calls % self._eval_freq == 0:
            print("EVALLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
            p = Process(name = "eval",
                        target = evaluate_policy_process,
                        args=(self.model,
                              self._n_eval_episodes,
                              self._deterministic,
                              self.queue,))
            print("EVALLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
            p.start()
            mean_reward = self.queue.get()
            print(mean_reward)

            #if mean_reward >= self._reward_threshold:
            if True:
                self.model.save(self._path)
                return False
        return True

def train(queue):

    # create env to train
    train_env = lineFollower()
    print("THIS IS WHERE IT CRAPS OUT")

    print("THIS IS WHERE IT CRAPS OUT HAHA")
    # Specify model
    model = PPO2(CnnPolicy,
                 train_env,
                 n_steps=256)

    # specify callback
    eval_callback = eval(n_eval_episodes  = 3,
                         deterministic    = True,
                         reward_threshold = 100000,
                         path             = "test_run_model",
                         queue            = queue)

    # train model
    model.learn(total_timesteps = int(200000),
                callback        = eval_callback)

if __name__ == '__main__':

    # Queue for holding values in processes
    queue_process = Manager().Queue()

    train_process = Process(name = "Train",target=train, args=(queue_process,))
    train_process.start()












# # Separate evaluation env
# eval_env = lineFollower()
#
# # Stop training when the model reaches the reward threshold
# callback_on_best = StopTrainingOnRewardThreshold(reward_threshold=-1500, verbose=1)
#
# # Create call back that will eval model and save the best one and stop training once reward has reached 490
# eval_callback    = EvalCallback(eval_env,
#                                 n_eval_episodes      = 10,
#                                 eval_freq            = int(800*50),
#                                 callback_on_new_best = callback_on_best,
#                                 best_model_save_path = "test_model",
#                                 log_path             = "test_model",
#                                 verbose              = 1)
#
# # Almost infinite number of timesteps, but the training will stop
# # early as soon as the reward threshold is reached
#
# # Separate evaluation env
# eval_env = Car()
# # Stop training when the model reaches the reward threshold
# callback_on_best = StopTrainingOnRewardThreshold(reward_threshold=-200, verbose=1)
# eval_callback = EvalCallback(eval_env, callback_on_new_best=callback_on_best, verbose=1)
#

# https://stable-baselines.readthedocs.io/en/master/guide/examples.html
#
# env   = lineFollower()
#
# model = PPO2(CnnPolicy,
#              env,
#              n_steps =256)
#
# model.learn(total_timesteps= int(200000)) #callback=eval_callback
#
# model.save("test_run_model")