from env import lineFollower
from stable_baselines import PPO2
import imageio
import numpy as np

# Load separate environment for evaluation
env = lineFollower()

# load model
model = PPO2.load("model_output/model_final.zip")

# Store image
images_raw         = []

# Set environment
obs    = env.reset()

done = False
while not done:
    action, _states = model.predict(obs, deterministic=True)
    obs, _, done, info = env.step(action)
    images_raw.append(obs)

# shutdown environment
env.shutdown()

# convert images to gif
imageio.mimsave('simulation_raw.gif', [np.array(img) for i, img in enumerate(images_raw) if i%4 == 0], fps=29)