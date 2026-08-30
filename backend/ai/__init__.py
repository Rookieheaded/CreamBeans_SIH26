"""
STAND-IN AI PACKAGE
====================
This module is a DROP-IN REPLACEMENT PLACEHOLDER for the real AI/ML matching
engine that (per the project spec) already exists elsewhere in the Cream
Beans repository.

Per "DEVELOPMENT STRATEGY" in the backend engineering brief:

    Initially implement the backend with mock AI results if necessary.
    Then replace the mock implementation with:
        from ai import find_matches
    The final backend must use the real AI engine.

This file exists ONLY so that `backend/` is independently runnable and
testable right now. It implements the EXACT contract described in the spec
(same function name, same Item fields, same output fields, same score
range, same sort order) so that swapping in the real `ai` package is a
zero-code-change operation for the backend: just delete/replace this
directory with the real one.

DO NOT extend this file with real ML logic. If you are Person 4 (backend)
and the real ai/ package lands in the repo, delete this file's contents
and let the real package take over — no backend code should need to change
because backend/services/match_service.py only ever imports:

    from ai import find_matches, Item

which is exactly what the real package also exposes.
"""

from .engine import find_matches, MatchingEngine, Item

__all__ = ["find_matches", "MatchingEngine", "Item"]
