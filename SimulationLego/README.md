# Lego Car
![Alt Text](legoCar.png)


### Objective:
Using CoppeliaSim, the lego car should be able to follow the blue line (masked tape) by using the trained simulated model.


### Side note:
When training a model on a simulated environment, you want to mimic the real world as much as possible. The simulated car in `car_2.ttt`
is not that similar to the lego car however the actions are close enough to the point that the model can be transferable to the actual lego car.
This is just an experiment for me to understand the basic components needed to train a simulated model and then applying it to a real robot. 


What makes this model different compared to the Simulation folder is that the input is transformed into a simplified image.
This allows the model to be used in the real world by easily transforming the image into a similar format. As a result,
the model can easily be transferred to the lego car without any further complicated modifications.

Finally, one can easily criticize how the objective was completed. For example, isolating the blue masked tape was done through simple filtering using 
RGB values which is incredibly sensitive to light. It's a naive approach but the main focus is experimentation on applying a simulated model to an actual robot.


### Folder structure

- Car.py : contains class that connects pyrep to coppeliasim
- env.py : contains the Gym environment that will be used to train the agent in the simulated environment
- car_2.ttt : contains the actual file that creates the simulated environment for the agent to ride on. 
  This environment is different to handle more different kinds of turns.
- train.py : trains and evaluates the agent producing model files (model_eval.zip and mode_final.zip)
- play.py : executes the trained agent and captures the frames to produce a gif
- pi.py: file to run on raspberry pi to control the robot based on the model's output
- laptop.py: file to run on a separate computer that can run the model and communicate with the raspberry pi


### Simulated Car lego in new environment!
![Alt Text](simulation_raw.gif)
![Alt Text](simulation_transformed.gif)




### Take the new trained model and apply it to the lego car
![Alt Text](Lego_raw.gif)
![Alt Text](Lego_transformed.gif)
