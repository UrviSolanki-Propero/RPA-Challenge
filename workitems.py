from RPA.Robocorp.WorkItems import WorkItems


def workitems() -> dict:
    """ Returns:
            workitems.
    """

    work_item = WorkItems()
    work_item.get_input_work_item()
    workitem = work_item.get_work_item_variables()

    return workitem
