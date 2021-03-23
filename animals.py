import bpy
from bpy.types import Header, Menu, Panel
from bpy.props import *
import cspy
from cspy import utils
C = bpy.context
D = bpy.data

class Constants:
    ICON_SHEET = "FILE_BLANK"

    TYPOS = {
        'Bind':'BIND',
        'Pose':'BIND',
        'Fight Idle':'CMBT WAIT',
        'Sleeping':'ACTV SLEP eLAND',
        'Go To Sleep':'ACTV SLEP eLAND',
        'Go To Sleep':'ACTV SLEP eLAND',
        'Stund Up':'ACTV Stop SLEP eLAND',
        'Crawling':'MOVE CRWL eLAND',
        'Walking':'MOVE WALK eLAND',
        'Swiming':'MOVE PDDL eSURF',
        'Swimming':'MOVE PDDL eSURF',
        'Strafe':'MOVE STRF eLAND',
        'side':'',
        'Side':'',
        'Hit':'CMBT IMPT eLAND',
        'Eating':'ACTV EATT eLAND',
        'Death':'CMBT DIEC eLAND',
        'Diging':'ACTV DIGG eLAND',
        'Jumping':'MOVE JUMP eLAND',
        'Scraching':'IDLE GROO eLAND',
        'Walk':'MOVE WALK eLAND',
        'Runing':'Running',
        'Running Fast':'MOVE GLLP eLAND',
        'Running':'MOVE CNTR eLAND',
        'Run':'MOVE CNTR eLAND',
        'Walk Back':'RVRS',
        'Forward_Back':'MOVE TURN180 eLAND',
        'Jump Attack':'ATCK LEAP eLAND',
        'Attack Jaw':'ATCK BITE eLAND MIDD',
        'Idle':'IDLE eLAND',
        'idle':'IDLE eLAND',
        'Attack':'ATCK eLAND',
        'Fight':'CMBT eLAND',
        'Barking':'VOCL BARK eLAND',
    }

    CHAR_REPLACEMENTS = {
        ' ':'-',
        '_':'-',
        '(':'-',
        ')':'-',
        '-------':'-',
        '------':'-',
        '-----':'-',
        '----':'-',
        '---':'-',
        '--':'-'
    }

    ORIENTATIONS = {
        'TURNRIGHT':(0, 90),
        'TURN90':(0, 90),
        'TURNLEFT':(0, -90),
        'TURN-90':(0, -90),
        'TURN180':(0, 180),
    }

    VARIATIONS = {
        '01':2,
        '02':3,
        '03':4,
        '04':5,
        '05':6,
    }


    LINE_STRIP_CHARS = [ '\t', '\r', '\n', ' ']

    PREFIXES = ['.', '-', ' ', '_', ',']



    ENVIRONMENTS = {
        'AQUATIC':'eAQUA',
        'AQUATIC-SURFACE':'eSURF',
        'AERIAL':'eAERL',
        'TERRESTRIAL':'eLAND',
        'ARBOREAL':'eTREE',
        'SUBTERRANEAN':'eSUBT'
    }

    ENVIRONMENTS_ENUM =  cspy.utils.create_enum_dict(ENVIRONMENTS)
    ENVIRONMENTS_ENUM_DEF = 'eLAND'

    DIRECTIONS = {
        'left':'LEFT',
        'right':'RIGHT',
        'front':'FRONT',
        'back':'BACK',
        'up':'UPWR',
        'down':'DOWN',
        'none':'NONE',
        'center':'CENT',
        'low':'LOWW',
        'high':'HIGH',
        'mid':'MIDD',
    }

    DIRECTIONS_ENUM = cspy.utils.create_enum_dict(DIRECTIONS)
    DIRECTIONS_ENUM_DEF = 'NONE'

    STAGES = {
        'loop':'LOOP',
        'start':'STRT',
        'end':'STOP',
        'stop':'STOP'
    }

    STAGES_ENUM =  cspy.utils.create_enum_dict(STAGES)
    STAGES_ENUM_DEF = 'LOOP'

    STATES = {
        'idle':'IDLE',
        'idle-sitting':'SITT',
        'motion':'MOVE',
        'activity':'ACTV',
        'combat':'CMBT',
        'attack':'ATCK',
        'vocalize':'VOCL',
        'sense':'SENS',
        'emotion':'EMOT',
    }

    STATES_ENUM =  cspy.utils.create_enum_dict(STATES)
    STATES_ENUM_DEF = 'IDLE'

    SUBSTATES = {
        'BIND-POSE':'BIND',
        'GENERIC':'GNRC',
        'CIRCLE':'CIRC',
        'DIG':'DIGG',
        'CLEAN':'CLEAN',
        'GROOM':'GROO',
        'SCRATCH-TREE':'SCTR',
        'TASTE-PLANT':'PLNT',
        'EAT':'EATT',
        'DRINK':'DRNK',
        'LICK':'LICK',
        'REST':'REST',
        'SLEEP':'SLEP',
        'URINATE':'URIN',
        'URINATE-MARK':'MARK',
        'DEFECATE':'DEFE',
        'HEAD-BUTT':'HEAD',
        'HEAD-HORN':'HORN',
        'HEAD-BITE':'BITE',
        'PAW-CLAW':'CLAW',
        'PAW-KICK':'KICK',
        'BUCK':'BUCK',
        'REAR':'REAR',
        'POUNCE':'LEAP',
        'DODGE':'DGDE',
        'FALL':'FALL',
        'IMPACT':'IMPT',
        'FLEE':'FLEE',
        'WAIT':'WAIT',
        'FAKE-FEINT':'FAKE',
        'CLOSE-SPACE':'CLSE',
        'BACK UP':'BACK',
        'POSITION':'PSTN',
        'CALL/HOWL':'CALL',
        'NOTIFY-BARK':'YIPP',
        'CONFLICT-BARK':'BARK',
        'WARN-GROWL':'GRWL',
        'WHINE':'WHNE',
        'YELP':'YELP',
        'BURROW':'BRRW',
        'CLIMB':'CLMB',
        'JUMP':'JUMP',
        'CRASH':'CRSH',
        'DESCEND':'DSND',
        'DIVE':'DIVE',
        'EMERGE':'EMRG',
        'ENTER':'ENTR',
        'EXIT':'EXIT',
        'FALL':'FALL',
        'LAND':'LAND',
        'SINK':'SINK',
        'SUBMERGE':'SBMR',
        'TAKEOFF':'TKOF',	
        'NEUTRAL':'NEUT',
        'INTERESTED':'INTR',
        'EXCITED':'EXCI',
        'BORED':'BORD',
        'TIRED':'TIRD',
        'EXHAUSTED':'EXHS',
        'SLEEPY':'SLPY',
        'CONFUSED':'CONF',
        'PANIC':'PANC',
        'SCARED':'SCRD',
        'DEFENSIVE':'DFNS',
        'AGGRESSIVE	':'AGGR',
        'DEFEATED':'DFTD',
        'INJURED':'INJR',
        'DEATH COMBAT':'DIEC',
        'DEATH INURTY':'DIEI',
        'LOOK':'LOOK',
        'LISTEN':'LSTN',
        'SMELL-AIR':'SMAR',
        'SMELL-GROUND':'SMGR',
        'SWIM':'SWIM',
        'PDDLT':'PDDL',
        'FLY':'FLYY',
        'GLIDE':'GLDE',
        'SOAR':'SOAR',
        'REVERSE':'RVRS',
        'CRAWL':'CRWL',
        'STALK':'STLK',
        'STRAFE':'STRF',
        'WALK-SLOW':'WSLW',
        'BIPEDAL':'BIPD',
        'WALK':'WALK',
        'AMBLE':'AMBL',
        'PACE':'PACE',
        'PACE-FAST':'PFST',
        'TROT':'TROT',
        'TROT-FAST':'TFST',
        'CANTER':'CNTR',
        'GALLOP':'GLLP',
        'RECTILINEAR':'RCTL',
        'UNDULATORY':'UNDL',
    }

    SUBSTATES_ENUM =  cspy.utils.create_enum_dict(SUBSTATES)
    SUBSTATES_ENUM_DEF = 'GNRC'

    SUBSTATES_REV = {}

    for key in SUBSTATES.keys():
        value = SUBSTATES[key]
        SUBSTATES_REV[value] = key