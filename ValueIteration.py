# import libraries
import numpy as np
import pandas as pd

WATCH = [[0.8,0.1,0.05,0.05,0,0],
         [0.6,0.3,0,0.05,0,0.05],
         [0.4,0,0.1,0.3,0,0.2],
         [0.7,0,0,0,0.3,0],
         [0.3,0.2,0,0.1,0.1,0.3],
         [0.9,0.1,0,0,0,0]]

SKIP = [[0.8,0.1,0.05,0.05,0,0],
         [0.6,0.3,0,0.05,0,0.05],
         [0.4,0,0.1,0.3,0,0.2],
         [0.7,0,0,0,0.3,0],
         [0.3,0.2,0,0.1,0.1,0.3],
         [0.9,0.1,0,0,0,0]]

WATCH_REWARD = np.array([1,.5, .1 , .1 , -1 ,.1]).reshape((-1,1))
SKIP_REWARD  = np.array([-3,-1, -.1 , -.1 , 20,-.1]).reshape((-1,1))

Pr     = np.array([WATCH, SKIP])

pr_transition_states = Pr
reward_states = np.hstack([WATCH_REWARD,SKIP_REWARD])

beta = .98

def value_iteration(Pr, reward_states, beta, error_tol):
    """
    :param pr_transition_states:
    :param reward_states:
    :param beta:
    :return:
    """

    # TODO: Create function to check if the requirements are satisified

    updated_value_states = np.zeros(Pr.shape[1]).reshape((-1,1))

    while True:

        # set difference to 0 and set updated value states to current
        max_difference_value = 0
        current_value_states = updated_value_states

        # calculate the value state(k+1) (see david silver equation, MDP slide 28)
        action_reward         = reward_states + (beta * np.einsum('ij,kji->jk', current_value_states, Pr))

        # Find the max value given action
        current_value_action  = action_reward.argmax(axis = 1)
        updated_value_states  = action_reward[np.arange(Pr.shape[1]),current_value_action].reshape((-1,1))

        # Find the max difference of value states among update
        current_max_value_diff = np.abs(updated_value_states - current_value_states).max()



        if current_max_value_diff > max_difference_value:
            max_difference_value = current_max_value_diff

        if max_difference_value > (error_tol * (1 - beta) / beta):
            break

    print(updated_value_states)
    print(current_value_action)