from Products.CMFCore.utils import getToolByName
from bika.lims import logger
from bika.lims.workflow import isBasicTransitionAllowed


def guard_to_be_preserved(obj):
    # TODO Worlkflow - Sample guard_to_be_preserved needs some love
    return True


def guard_schedule_sampling(obj):
    """
    Prevent the transition if:
    - if the user isn't part of the sampling coordinators group
      and "sampling schedule" checkbox is set in bika_setup
    - if no date and samples have been defined
      and "sampling schedule" checkbox is set in bika_setup
    """
    if obj.bika_setup.getScheduleSamplingEnabled() and \
            isBasicTransitionAllowed(obj):
        return True
    return False


def guard_receive(obj):
    return isBasicTransitionAllowed(obj)


def guard_sample_prep(obj):
    """Allow the sampleprep automatic transition to fire.
    """
    if not isBasicTransitionAllowed(obj):
        return False
    return obj.getPreparationWorkflow()


def guard_sample_prep_complete(obj):
    """ This relies on user created workflow.  This function must
    defend against user errors.

    AR and Analysis guards refer to this one.

    - If error is encountered, do not permit object to proceed.  Break
      this rule carelessly and you may see recursive automatic workflows.

    - If sampleprep workflow is badly configured, primary review_state
      can get stuck in "sample_prep" forever.

    """
    wftool = getToolByName(obj, 'portal_workflow')
    try:
        # get sampleprep workflow object.
        sp_wf_name = obj.getPreparationWorkflow()
        sp_wf = wftool.getWorkflowById(sp_wf_name)
        # get sampleprep_review state.
        sp_review_state = wftool.getInfoFor(obj, 'sampleprep_review_state')
        assert sp_review_state
    except WorkflowException as e:
        logger.warn("guard_sample_prep_complete_transition: "
                    "WorkflowException %s" % e)
        return False
    except AssertionError:
        logger.warn("'%s': cannot get 'sampleprep_review_state'" %
                    sampleprep_wf_name)
        return False

    # get state from workflow - error = allow transition
    # get possible exit transitions for state: error = allow transition
    transitions = sp_wf
    if len(transitions) > 0:
        return False
    return True


def guard_reject(obj):
    """Returns true if the 'reject' transition can be performed to the obj
    (Sample) passed in.

    Returns True if the following conditions are met:
    - The Sample is active (neither inactive nor cancelled state)
    - Rejection Workflow is enabled in bika_setup

    :param obj: the Sample the 'reject' transition has to be evaluated against.
    :type obj: Sample
    :returns: True or False
    :rtype: bool
    """
    if not isBasicTransitionAllowed(obj):
        return False
    return obj.bika_setup.isRejectionWorkflowEnabled()