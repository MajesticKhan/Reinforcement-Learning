#--------------------------------------------------------Import libraries
from stable_baselines import PPO2
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.callbacks import BaseCallback
import multiprocessing as mp
from multiprocessing import Process, Queue
from env import lineFollower
import numpy as np
import pickle

#--------------------------------------------------------Evaluation process
# creates a function used by a separate process to evalulate the current model trained
def evaluate_policy_process(model, n_eval_episodes,deterministic, queue):
    """
     :param model           : path to trained model to be evaluated
     :param n_eval_episodes : How many times to evaluate the environment
     :param deterministic   : Should the model be stochastic or deterministic
     :param queue           : Queue to allow values to be exchanged
    """

    # Load separate environment for evaluation
    env = lineFollower()

    # calculate mean reward
    episode_rewards = []

    # load model
    model = PPO2.load(model)

    for _ in range(n_eval_episodes):
        reward_sum = 0
        done       = False
        obs        = env.reset()

        while not done:
            action, _states = model.predict(obs, deterministic = deterministic)
            obs, reward, done, info = env.step(action)
            reward_sum += reward
        episode_rewards.append(reward_sum)

    # shutdown environment
    env.shutdown()

    # Put reward value into queue
    queue.put(np.mean(episode_rewards))


# Class used to call back
class eval(BaseCallback):

    def __init__(self, n_eval_episodes, deterministic, reward_threshold, path, eval_freq, queue):
        """
         :param n_eval_episodes  : How many times to evaluate the environment
         :param deterministic    : Should the model be stochastic or deterministic
         :param reward_threshold : The max reward to stop training
         :param path             : File path saved
         :param eval_freq        : When should the steps be evaluated
         :param queue            : Queue to allow values to be exchanged
        """

        super().__init__()
        self._n_eval_episodes  = n_eval_episodes
        self._deterministic    = deterministic
        self._reward_threshold = reward_threshold
        self._path             = path
        self._eval_freq        = eval_freq
        self.queue             = queue

    def _on_step(self):

        if self.n_calls % self._eval_freq == 0:

            # Write eval model
            self.model.save(self._path + "_eval")

            # Create a separate evaluation process
            p = Process(name = "eval",
                        target = evaluate_policy_process,
                        args=(self._path + "_eval",
                              self._n_eval_episodes,
                              self._deterministic,
                              self.queue,))

            # start process
            p.start()

            # collect mean_reward from queue
            mean_reward = self.queue.get()

            # Wait for the process to stop
            p.join()

            # Get previous or initial value
            with open('reward.pkl', 'rb') as g:
                previous_run = pickle.load(g)

            if mean_reward >= self._reward_threshold and mean_reward > previous_run['reward']:
                self.model.save(self._path + "_final")
                previous_run["run"] = 0
                previous_run["reward"] = mean_reward

            elif previous_run["run"] > 2:
                return False

            else:
                previous_run["run"] += 1
                with open('reward.pkl', 'wb') as beg:
                    pickle.dump(previous_run, beg)

        # Continue to train
        return True


# train the model
def train(queue):
    """
    :param queue: Queue to collect and output results during evaluation phase
    """
    # write 0 for history of rewards
    with open('reward.pkl', 'wb') as beg:
        pickle.dump({'reward':0,'run':0}, beg)

    # Create env to train
    train_env = lineFollower()

    # Specify model and feed the environment
    model = PPO2(CnnPolicy,
                 train_env,
                 n_steps=256)

    # Specify callback to evaluate training
    eval_callback = eval(n_eval_episodes  = 3,
                         deterministic    = True,
                         reward_threshold = 40000,
                         path             = "model_output/model",
                         eval_freq        = 10000,
                         queue            = queue)

    # train model
    model.learn(total_timesteps = int(200000),
                callback        = eval_callback)

    # shutdown the simulator
    train_env.shutdown()


if __name__ == '__main__':

    # Make sure to start a brand new process
    mp.set_start_method('spawn')

    # Queue for holding values in processes
    queue_process = Queue()

    # execute training
    train(queue_process)