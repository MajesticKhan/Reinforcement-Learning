from stable_baselines import PPO2
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.callbacks import BaseCallback
from stable_baselines.common.evaluation import evaluate_policy
import multiprocessing as mp
from multiprocessing import Process, Queue
from env import lineFollower


def evaluate_policy_process(model, n_eval_episodes,deterministic, queue):
    """
     :param model           : Trained model to be evaluated
     :param n_eval_episodes : How many times to evaluate the environment
     :param deterministic   : Should the model be stochastic or deterministic
     :param queue           : Queue to allow values to be exchanged
    """

    # Load separate environment for evaluation
    eval_env = lineFollower()

    # calculate mean reward
    mean_reward, _ = evaluate_policy(
        model,
        eval_env,
        n_eval_episodes = n_eval_episodes,
        deterministic   = deterministic
    )

    # shutdown environment
    eval_env.shutdown()

    # Put reward value into queue
    queue.put(mean_reward)


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
        self._eval_freq        = eval_freq
        self._deterministic    = deterministic
        self._reward_threshold = reward_threshold
        self._path             = path
        self.queue             = queue

    def _on_step(self):

        if self.n_calls % self._eval_freq == 0:

            # Create a separate evaluation process
            p = Process(name = "eval",
                        target = evaluate_policy_process,
                        args=(self.model,
                              self._n_eval_episodes,
                              self._deterministic,
                              self.queue,))

            # start process
            p.start()

            # collect mean_reward from queue
            mean_reward = self.queue.get()

            # Wait for the process to stop
            p.join()

            if mean_reward >= self._reward_threshold:
                self.model.save(self._path)
                return False

        # Continue to train
        return True

def train(queue):
    """
    :param queue: Queue to collect and output results
    """

    # Create env to train
    train_env = lineFollower()


    # Specify model and feed the environment
    model = PPO2(CnnPolicy,
                 train_env,
                 n_steps=256)


    # Specify callback to evaluate training
    eval_callback = eval(n_eval_episodes  = 3,
                         deterministic    = True,
                         reward_threshold = 100000,
                         path             = "lego_model",
                         eval_freq        = 10,
                         queue            = queue)

    # train model
    model.learn(total_timesteps = int(200000),
                callback        = eval_callback)

if __name__ == '__main__':

    # Make sure to start a brand new process
    mp.set_start_method('spawn')

    # Queue for holding values in processes
    queue_process = Queue()

    # execute training
    train(queue_process)