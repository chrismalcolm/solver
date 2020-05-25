"""
    Custom exceptions.
"""

class SolverError(Exception):
    """Base class for Solver exceptions."""
    pass

class InvalidParameters(SolverError):
    """Raised when invalid parameters are given for a public method."""
    pass

class ExternalResource(SolverError):
    """Raised when issues occur when loading external resources."""
    pass

class SolvingExecution(SolverError):
    """Raised when any error occur during solving."""
    pass
