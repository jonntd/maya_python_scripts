import maya.cmds as cmds


# -----------------------------------------------------------------------------
def armFK(char, tp):
    hand_rot = cmds.xform(char + tp + '_fk_hand_joint', a=True, q=True, ws=True, ro=True)
    cmds.xform(char + tp + '_hand', ws=True, ro=hand_rot)
    hand_tr = cmds.xform(char + tp + '_wrist', a=True, q=True, ws=True, t=True)
    cmds.xform(char + tp + '_hand', ws=True, t=hand_tr)
    elbow_tr = cmds.xform(char + tp + '_forearm', a=True, q=True, ws=True, t=True)
    cmds.xform(char + tp + '_elbow', ws=True, t=elbow_tr)


# -----------------------------------------------------------------------------
def armIK(char, tp):
    dop = 'Aim' if tp == 'r' else ''
    arm_rot = cmds.xform(char + tp + '_ik_arm_joint' + dop, a=True, q=True, ws=True, ro=True)
    cmds.xform(char + tp + '_arm', ws=True, ro=arm_rot)
    forearm_rot = cmds.xform(char + tp + '_ik_forearm_joint' + dop, a=True, q=True, ws=True, ro=True)
    cmds.xform(char + tp + '_forearm', ws=True, ro=forearm_rot)
    wrist_rot = cmds.xform(char + tp + '_ik_hand_joint' + dop, a=True, q=True, ws=True, ro=True)
    cmds.xform(char + tp + '_wrist', ws=True, ro=wrist_rot)


# -----------------------------------------------------------------------------
def legFK(char, tp):
    foot_rot = cmds.xform(char + tp + '_fk_foot_joint', a=True, q=True, ws=True, ro=True)
    cmds.xform(char + tp + '_foot', ws=True, ro=foot_rot)
    foot_tr = cmds.xform(char + tp + '_fk_foot_joint', a=True, q=True, ws=True, t=True)
    cmds.xform(char + tp + '_foot', ws=True, t=foot_tr)
    knee_tr = cmds.xform(char + tp + '_leg', a=True, q=True, ws=True, t=True) 
    cmds.xform(char + tp + '_knee', ws=True, t=knee_tr)


# -----------------------------------------------------------------------------
def legIK(char, tp):
    dop = 'Aim' if tp == 'r' else ''
    upLeg_rot = cmds.xform(char + tp + '_ik_upLeg_joint' + dop, a=True, q=True, ws=True, ro=True) 
    cmds.xform(char + tp + '_upLeg', ws=True, ro=upLeg_rot)
    leg_rot = cmds.xform(char + tp + '_ik_leg_joint' + dop, a=True, q=True, ws=True, ro=True)
    cmds.xform(char + tp + '_leg', ws=True, ro=leg_rot)
    heel_rot = cmds.xform(char + tp + '_ik_foot_joint' + dop, a=True, q=True, ws=True, ro=True)
    cmds.xform(char + tp + '_heel', ws=True, ro=heel_rot)


# -----------------------------------------------------------------------------
def spineFK(char):
    spineD_tr = cmds.xform(char + 'FKSpine_joint1', a=True, q=True, ws=True, t=True)
    cmds.xform(char + 'spine_down', ws=True, t=spineD_tr)
    spineD_rot = cmds.xform(char + 'spine1', a=True, q=True, ws=True, ro=True)
    cmds.xform(char + 'spine_down', ws=True, ro=spineD_rot)
    spineM_tr = cmds.xform(char + 'spine3', a=True, q=True, ws=True, t=True)
    cmds.xform(char + 'spine_middle', ws=True, t=spineM_tr)
    spineU_tr = cmds.xform(char + 'FKSpine_joint9', a=True, q=True, ws=True, t=True)
    cmds.xform(char + 'spine_up', ws=True, t=spineU_tr)
    spineU_rot = cmds.xform(char + 'spine4', a=True, q=True, ws=True, ro=True)
    cmds.xform(char + 'spine_up', ws=True, ro=spineU_rot)
    

# -----------------------------------------------------------------------------
def spineIK(char):
    spine1_tr = cmds.xform(char + 'IKSpineCurveLocator1', a=True, q=True, ws=True, t=True) 
    cmds.xform(char + 'spine1', ws=True, t=spine1_tr)
    spine1_rot = cmds.xform(char + 'spine_down', a=True, q=True, ws=True, ro=True)
    cmds.xform(char + 'spine1', ws=True, ro=spine1_rot)
    spine2_tr = cmds.xform(char + 'IKSpineCurveLocator2', a=True, q=True, ws=True, t=True)
    cmds.xform(char + 'spine2', ws=True, t=spine2_tr)
    spine3_tr = cmds.xform(char + 'IKSpineCurveLocator3', a=True, q=True, ws=True, t=True)
    cmds.xform(char + 'spine3', ws=True, t=spine3_tr)
    spine4_tr = cmds.xform(char + 'IKSpineCurveLocator4', a=True, q=True, ws=True, t=True)
    cmds.xform(char + 'spine4', ws=True, t=spine4_tr)
    spine4_rot = cmds.xform(char + 'spine_up', a=True, q=True, ws=True, ro=True) 
    cmds.xform(char + 'spine4', ws=True, ro=spine4_rot)


# -----------------------------------------------------------------------------
fkIkData = {'r_fkArmOffset': ['r_arm_control.fkIk', 1, lambda c: armFK(c, 'r')],
            'l_fkArmOffset': ['l_arm_control.fkIk', 1, lambda c: armFK(c, 'l')],
            'r_handIKOffset': ['r_arm_control.fkIk', 0, lambda c: armIK(c, 'r')],
            'l_handIKOffset': ['l_arm_control.fkIk', 0, lambda c: armIK(c, 'l')],
            
            'r_fkUpLegOffset': ['r_leg_control.fkIk', 1, lambda c: legFK(c, 'r')],
            'l_fkUpLegOffset': ['l_leg_control.fkIk', 1, lambda c: legFK(c, 'l')],
            'r_footIKOffset': ['r_leg_control.fkIk', 0, lambda c: legIK(c, 'r')],
            'l_footIKOffset': ['l_leg_control.fkIk', 0, lambda c: legIK(c, 'l')],
            
            'FK_spineControlsGrp': ['spine_control.fkIk', 1, spineFK],
            'IK_spineControlsGrp': ['spine_control.fkIk', 0, spineIK]}
