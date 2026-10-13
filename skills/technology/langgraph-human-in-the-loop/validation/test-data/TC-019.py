"""TC-019: Version-dependent behavior not reported as confirmed without evidence."""
# In v0.2.x interrupt() returns resume payload; review must verify version before claiming behavior
def review_node(state):
    # UNCERTAIN: Review should verify LangGraph runtime version rather than assuming breaking signature
    pass

