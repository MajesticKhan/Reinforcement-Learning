from stable_baselines import PPO2
from stable_baselines.common.policies import CnnPolicy
from stable_baselines.common.callbacks import EvalCallback, StopTrainingOnRewardThreshold
from BeautifulBlueSquare.BlueGymEnv import simpleAvoidance

# Separate evaluation env
eval_env = simpleAvoidance()

# Stop training when the model reaches the reward threshold, 800 * .9 = 720
callback_on_best = StopTrainingOnRewardThreshold(reward_threshold=720, verbose=1)

# Create call back that will eval model and save the best one and stop training once reward has reached 490
eval_callback    = EvalCallback(eval_env,
                                n_eval_episodes      = 20,
                                eval_freq            = int(800*50),
                                callback_on_new_best = callback_on_best,
                                best_model_save_path = "model",
                                log_path             = "model",
                                verbose              = 1)

# Almost infinite number of timesteps, but the training will stop
# early as soon as the reward threshold is reached
env =simpleAvoidance()

model = PPO2(CnnPolicy,
             env,
             gamma = .99,
             n_steps =256)
model.learn(total_timesteps= int(20e6), callback=eval_callback)