# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import random
import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        # print('runValueIteration ', self.values)
        # prevValues = self.values
        for i in range(self.iterations):
            mdpStates = self.mdp.getStates()
            newValues = {}
            for state in mdpStates:
                legalActions = self.mdp.getPossibleActions(state)
                #what if legalActions is empty
                maxValue = 0
                if legalActions:
                    values = [self.computeQValueFromValues(state, action) for action in legalActions]
                    maxValue = max(values)

                # maxIndexes = [i for i in len(values) if values[i] is maxValue]
                newValues[state] = maxValue

            for state in mdpStates:
                self.values[state] = newValues[state]

        return



    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values.get(state, 0)


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        # print('computeQValueFromValues ')
        qValue = 0
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            qValue += prob*(self.mdp.getReward(state, action, nextState) + self.discount*self.getValue(nextState))
            # print("computeQValueFromValues ", nextState, prob, qValue)

        return qValue
        # util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        # print('computeActionFromValues ')
        legalActions = self.mdp.getPossibleActions(state)
        if not legalActions:
            return None
        values = [self.computeQValueFromValues(state, action) for action in legalActions]
        maxValue = max(values)
        maxIndexes = [i for i in range(len(values)) if values[i] is maxValue]
        actionTaken = legalActions[random.choice(maxIndexes)]

        return actionTaken

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        allStates = self.mdp.getStates()
        for i in range(self.iterations):
            state = allStates[i%len(allStates)]

            if not self.mdp.isTerminal(state):
                values = []
                allLegalActions = self.mdp.getPossibleActions(state)
                for action in allLegalActions:
                    qvalues = self.computeQValueFromValues(state, action)
                    values.append(qvalues)
                self.values[state] = max(values)

        return

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()
        adj_list = {}
        for state in states:
            for action in self.mdp.getPossibleActions(state):
                for nextState, _ in self.mdp.getTransitionStatesAndProbs(state, action):
                    if nextState in adj_list:
                        adj_list[nextState].add(state)
                    else:
                        adj_list[nextState] = set([state])

        pq = util.PriorityQueue()

        for state in states:
            if not self.mdp.isTerminal(state):
                qValues = [self.computeQValueFromValues(state, action) for action in self.mdp.getPossibleActions(state)]
                diff = abs(self.values[state] - max(qValues))
                pq.push(state, -diff)   
        
        for i in range(self.iterations):
            if pq.isEmpty():
                return
            state = pq.pop()
            if not self.mdp.isTerminal(state):
                qValues = [self.computeQValueFromValues(state, action) for action in self.mdp.getPossibleActions(state)]
                self.values[state] = max(qValues)
            for p in adj_list[state]:
                qValues = [self.computeQValueFromValues(p, action) for action in self.mdp.getPossibleActions(p)]
                diff = abs(self.values[p] - max(qValues))
                if diff > self.theta:
                    pq.update(p, -diff)
                    

        

