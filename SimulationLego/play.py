from env import lineFollower
from stable_baselines import PPO2
import imageio
import numpy as np

# Load separate environment for evaluation
env = lineFollower()

# load model
model = PPO2.load("model_final.zip")

# Store image
images_transformed = []
images_raw         = []

# Set environment
obs    = env.reset()

done = False
while not done:
    action, _states = model.predict(obs, deterministic=True)
    obs, _, done, info = env.step(action)
    images_transformed.append(obs)
    images_raw.append(info["raw_obs"])

# shutdown environment
env.shutdown()

# convert images to gif
imageio.mimsave('simulation_raw.gif', [np.array(img) for i, img in enumerate(images_raw) if i%4 == 0], fps=29)
imageio.mimsave('simulation_transformed.gif', [np.array(img) for i, img in enumerate(images_transformed) if i%4 == 0], fps=29)