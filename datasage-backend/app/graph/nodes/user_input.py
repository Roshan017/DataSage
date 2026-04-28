from app.graph.state import DataSageState

def user_input_node(state: DataSageState) -> DataSageState:
    
    """
        Just Normalize and pass on the user input forward
    """

    print("[user_input_node] raw query:", state["user_query"])

    user_query = state['user_query'].strip()


    return {

        **state,
        "user_query":user_query 
    }