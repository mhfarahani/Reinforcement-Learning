import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import sys
import operator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        self.initializeQ()
        self.alpha = 0.6
        self.gamma = 0.4
        self.epsilon = 0.01
        self.reward = 0.0

    def getMaxQ(self,state):
        q_max = 0
        a_max = None
        for action in self.env.valid_actions:
            qt = self.Q[(state,action)]
            if qt > q_max:
                q_max = qt
                a_max = action
        return q_max,a_max

    def initializeQ (self):
        # Inintialize Q. Q is a dictionary that includes all possible combination of state variables and actions
        self.Q = {}
        val = 5 # random.randint(0,16)
        print 'val = ', val
        for light in ['red','green']:
            for oncoming in self.env.valid_actions:
                for left in self.env.valid_actions:
                    for waypoint in ['left','right','forward']:
                        for action in self.env.valid_actions:
                    #self.Q[((light,waypoint),action)] = val
                            self.Q[((light,oncoming,left,waypoint),action)] = val
        

    def reset(self, destination=None):
        # Prepare for a new trip; reset any variables here
        self.planner.route_to(destination)
        self.reward = 0.0

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
       
        # Update state
        #self.state = (inputs['light'], self.next_waypoint)
        self.state = (inputs['light'], inputs['oncoming'],inputs['left'], self.next_waypoint)
 
        # Select action according to the policy
        #action = random.choice(self.env.valid_actions)
        Qmax, action  = self.getMaxQ(self.state)
        if random.random() < self.epsilon:
            # Epsilon-Greedy Exploration: A semi-uniform random exploration
            action = random.choice(self.env.valid_actions)
            Qmax = self.Q[(self.state,action)]
        immediate_reward = self.env.act(self, action)
        self.reward += immediate_reward
        self.Q[(self.state,action)] = (1.-self.alpha)*self.Q[(self.state,action)]+(self.gamma*Qmax+immediate_reward)*self.alpha
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, self.reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""
    random.seed(22)

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=1000)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
