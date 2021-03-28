import cspy
from cspy import utils

_MASKS = {
    'Face Only':'FACE',
    'Body Only':'BODY',
    'Limbs Only':'LIMB',
}

_ENVIRONMENTS = {
    'Aquatic':'AQUA',
    'Aquatic Surface':'SURF',
    'Aerial':'AERL',
    'Terrestrial':'LAND',
    'Arboreal':'TREE',
    'Subterranean':'SUBT'
}

_DIRECTIONS = {
    'None':'NONE',
    'Left':'LEFT',
    'Right':'RIGHT',
    'Front':'FRONT',
    'Back':'BACK',
    'Up':'UPWR',
    'Down':'DOWN',
    'Low':'LOWW',
    'High':'HIGH',
    'Middle':'MIDD',
    'Center':'MIDD',
}

_STAGES = {
    'Loop':'LOOP',
    'Start':'STRT',
    'End':'STOP',
    'Stop':'STOP'
}

_STATES = {
    'Idle':'IDLE',
    'Sitting':'SITT',
    'Laying':'LYNG',
    'Motion':'MOVE',
    'Activity':'ACTV',
    'Combat':'CMBT',
    'Attack':'ATCK',
    'Vocalize':'VOCL',
    'Sense':'SENS',
    'Emotion':'EMOT',
}

_IDLE_SUBSTATES = {
    'Bind Pose':'BIND',
    'Generic':'GNRC',   
    'Clean':'CLEAN',
    'Groom':'GROO',
    'Look':'LOOK',
    'Listen':'LSTN',
    'Smell (Air)':'SMAR',
    'Smell (Ground)':'SMGR',
}

_SITT_SUBSTATES = {        
    'Generic':'GNRC',   
    'Clean':'CLEAN',
    'Groom':'GROO',
    'Look':'LOOK',
    'Listen':'LSTN',
    'Smell (Air)':'SMAR',
    'Smell (Ground)':'SMGR',
}

_LYNG_SUBSTATES = {
    'Generic':'GNRC',   
    'Clean':'CLEAN',
    'Groom':'GROO',
    'Look':'LOOK',
    'Listen':'LSTN',
    'Smell (Air)':'SMAR',
    'Smell (Ground)':'SMGR',
}

_MOVE_SUBSTATES = {   
    'Burrow':'BRRW',
    'Climb':'CLMB',
    'Jump':'JUMP',
    'Crash':'CRSH',
    'Descend':'DSND',
    'Dive':'DIVE',
    'Emerge':'EMRG',
    'Enter':'ENTR',
    'Exit':'EXIT',
    'Fall':'FALL',
    'Land':'LAND',
    'Sink':'SINK',
    'Submerge':'SBMR',
    'Takeoff':'TKOF',
    'Swim':'SWIM',
    'Paddle':'PDDL',
    'Fly':'FLYY',
    'Glide':'GLDE',
    'Soar':'SOAR',
    'Reverse':'RVRS',
    'Crawl':'CRWL',
    'Stalk':'STLK',
    'Strafe':'STRF',
    'Walk Slow':'WSLW',
    'Bipedal':'BIPD',
    'Walk':'WALK',
    'Amble':'AMBL',
    'Pace':'PACE',
    'Pace Fast':'PFST',
    'Trot':'TROT',
    'Trot Fast':'TFST',
    'Canter':'CNTR',
    'Gallop':'GLLP',
    'Rectilinear':'RCTL',
    'Undulatory':'UNDL',
}

_ACTV_SUBSTATES = {
    'Dig':'DIGG',
    'Scratch Tree':'SCTR',
    'Taste Plant':'PLNT',
    'Eat':'EATT',
    'Drink':'DRNK',
    'Lick':'LICK',
    'Rest':'REST',
    'Sleep':'SLEP',
    'Urinate':'URIN',
    'Urinate Mark':'MARK',
    'Defecate':'DEFE',
    'Death (Injury)':'DIEI',
}

_CMBT_SUBSTATES = {
    'Dodge':'DGDE',
    'Fall':'FALL',
    'Impact':'IMPT',
    'Flee':'FLEE',
    'Wait':'WAIT',
    'Fake/Feint':'FAKE',
    'Close Space':'CLSE',
    'Back Up':'BACK',
    'Position':'PSTN',
    'Death (Combat)':'DIEC',
}

_ATCK_SUBSTATES = {
    'Headbutt':'HEAD',
    'Horns':'HORN',
    'Bite':'BITE',
    'Claws':'CLAW',
    'Kick':'KICK',
    'Buck':'BUCK',
    'Rear':'REAR',
    'Pounce':'LEAP',
    'Ambush':'AMBS',
}

_VOCL_SUBSTATES = {
    'Call/Howl':'CALL',
    'Notify Bark':'NTFY',
    'Conflict Bark':'BARK',
    'Warn/Growl':'GRWL',
    'Whine':'WHNE',
    'Yelp':'YELP',
}

_SENS_SUBSTATES = {
    'Look':'LOOK',
    'Listen':'LSTN',
    'Smell (Air)':'SMAR',
    'Smell (Ground)':'SMGR',
}

_EMOT_SUBSTATES = {
    'Neutral':'NEUT',
    'Interested':'INTR',
    'Excited':'EXCI',
    'Tired':'TIRD',
    'Exhausted':'EXHS',
    'Sleepy':'SLPY',
    'Confused':'CONF',
    'Panic':'PANC',
    'Scared':'SCRD',
    'Defensive':'DFNS',
    'Aggressive	':'AGGR',
    'Defeated':'DFTD',
    'Injured':'INJR',
}



MASKS_ENUM =             cspy.utils.create_enum_dict(_MASKS)
ENVIRONMENTS_ENUM =      cspy.utils.create_enum_dict(_ENVIRONMENTS)
DIRECTIONS_ENUM =        cspy.utils.create_enum_dict(_DIRECTIONS)
STAGES_ENUM =            cspy.utils.create_enum_dict(_STAGES)
STATES_ENUM =            cspy.utils.create_enum_dict(_STATES)
IDLE_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_IDLE_SUBSTATES)
SITT_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_SITT_SUBSTATES)
LYNG_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_LYNG_SUBSTATES)
MOVE_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_MOVE_SUBSTATES)
ACTV_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_ACTV_SUBSTATES)
CMBT_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_CMBT_SUBSTATES)
ATCK_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_ATCK_SUBSTATES)
VOCL_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_VOCL_SUBSTATES)
SENS_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_SENS_SUBSTATES)
EMOT_SUBSTATES_ENUM =    cspy.utils.create_enum_dict(_EMOT_SUBSTATES)

MASKS_ENUM_DEF           = 'FACE'
ENVIRONMENTS_ENUM_DEF    = 'LAND'
DIRECTIONS_ENUM_DEF      = 'NONE'
STAGES_ENUM_DEF          = 'LOOP'
STATES_ENUM_DEF          = 'IDLE'
IDLE_SUBSTATES_ENUM_DEF  = 'BIND'
SITT_SUBSTATES_ENUM_DEF  = 'GNRC'
LYNG_SUBSTATES_ENUM_DEF  = 'GNRC'
MOVE_SUBSTATES_ENUM_DEF  = 'WALK'
ACTV_SUBSTATES_ENUM_DEF  = 'REST'
CMBT_SUBSTATES_ENUM_DEF  = 'WAIT'
ATCK_SUBSTATES_ENUM_DEF  = 'HEAD'
VOCL_SUBSTATES_ENUM_DEF  = 'CALL'
SENS_SUBSTATES_ENUM_DEF  = 'LOOK'
EMOT_SUBSTATES_ENUM_DEF  = 'NEUT'