"""Use case interface contract."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class IUseCase(ABC, Generic[InputType, OutputType]):
    """
    Abstract interface for all use cases.
    Defines the contract for use case execution.
    """
    
    @abstractmethod
    async def execute(self, input_data: InputType) -> OutputType:
        """
        Execute the use case.
        
        Args:
            input_data: Input data for the use case
            
        Returns:
            Output data from the use case
        """
        pass
