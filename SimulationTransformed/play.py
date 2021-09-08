from env import lineFollower
from stable_baselines import PPO2
import imageio
import numpy as np

# Load separate environment for evaluation
env = lineFollower()

# load model
model = PPO2.load("lego_model_transformed_final.zip")

images = []
obs    = env.reset()
images.append(obs)

done = False
while not done:
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, done, info = env.step(action)
    images.append(obs)

# shutdown environment
env.shutdown()
imageio.mimsave('foundation.gif', [np.array(img) for i, img in enumerate(images) if i%2 == 0], fps=29)


