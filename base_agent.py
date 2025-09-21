from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the Triplix system.
    """

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        The main execution method for the agent.
        Each agent will implement this method to perform its specific task.
        """
        pass