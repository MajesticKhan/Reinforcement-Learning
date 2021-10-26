# import libraries
import numpy as np


def value_iteration(P, R, beta, error_tol = 1e-4):
    """
    :param pr_transition_states:
    :param R:
    :param beta:
    :return:
    """

    # TODO: Create function to check if the requirements are satisified

    # initalize state value to 0
    updated_value_states = np.zeros(P.shape[1]).reshape((-1,1))

    # Create immediate reward
    immediate_reward = (R*P).sum(2).T

    while True:

        # set updated value states to current
        current_value_states = updated_value_states.copy()

        # calculate the value state(k+1) (see david silver equation, MDP slide 28)
        action_reward         = immediate_reward + (beta * np.einsum('ij,kji->jk', current_value_states, P))

        # Find the max value given action
        current_value_action  = action_reward.argmax(axis = 1)
        updated_value_states  = action_reward[np.arange(P.shape[1]),current_value_action].reshape((-1,1))

        # Find the max difference of value states among update
        current_max_value_diff = np.abs(updated_value_states - current_value_states).max()

        # If the difference is
        if current_max_value_diff < (error_tol * (1 - beta) / beta):
            break

    print(updated_value_states)
    print(current_value_action)