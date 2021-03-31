import cspy
from collections import namedtuple


class ACTORS:
    RACC = ('Raccoon','RACC')
    WOLF = ('Wolf','WOLF')

class _ENVIRONMENT:
    NONE = ('None','NONE')
    AQUA = ('Aquatic (Underwater)','AQUA')
    SURF = ('Aquatic (Surface)','SURF')
    LAND = ('Terrestrial','LAND')
    SUBT = ('Subterranean','SUBT')
    TREE = ('Arboreal','TREE')
    AERL = ('Aerial','AERL')

class _CATEGORY:
    NONE = ('None','NONE')
    BIND = ('Bind Pose','BIND')
    DEAD = ('Dead','DEAD')
    VOCL = ('Vocalize','VOCL')
    EMOT = ('Emotion','EMOT')
    SENS = ('Sense','SENS')
    IDLE = ('Idle','IDLE')
    ACTV = ('Activity','ACTV')
    MOVE = ('Motion','MOVE')
    TRNS = ('Transition','TRNS')
    CMBT = ('Combat','CMBT')

class _MASK:
    FULL = ('Full Character','FULL')
    HEAD = ('Head Only','HEAD')
    BODY = ('Body Only','BODY')
    BRHT = ('Body Only (Right)','BRHT')
    BLFT = ('Body Only (Left)','BLFT')

class _STAGE:
    NONE = ('None','NONE')
    LOOP = ('Loop','LOOP')
    STRT = ('Start','STRT')
    STOP = ('Stop','STOP')
    ONCE = ('Once','ONCE')

class _POSE:
    NONE = ('None','NONE')

    DEDW = ('Dead (Aquatic)','DEDW')
    DEDS = ('Dead (Aquatic Surface)','DEDS')
    DEDT = ('Dead (Terrestrial)','DEDT')

    PELT = ('Animal Pelt','PELT')

    IDLG = ('Idle (Ground)','IDLG')
    IDLW = ('Idle (Ground Wounded)','IDLW')
    SITG = ('Sitting (Ground)','SITG')
    RSTG = ('Resting (Ground)','RSTG')
    SLPG = ('Sleeping (Ground)','SLPG')

    IDLF = ('Idle (Float)','IDLF')
    IDLT = ('Idle (Tread Water)','IDLT')
    RSTW = ('Resting (Water)','RSTW')
    SLPW = ('Sleeping (Water)','SLPW')

    IDLT = ('Idle (Tree)','IDLT')
    SITT = ('Sitting (Tree)','SITT')
    RSTT = ('Resting (Tree)','RSTT')
    SLPT = ('Sleeping (Tree)','SLPT')

    HOVR = ('Hover','HOVR')

    BRRW = ('Burrow','BRRW')
    JUMP = ('Jump','JUMP')

    CLMB = ('Climb','CLMB')
    WLKT = ('Walk In Tree','WLKT')
    HANG = ('Hang','HANG')

    FLYY = ('Fly','FLYY')
    GLDE = ('Glide','GLDE')
    DIVE = ('Dive','DIVE')

    FLHI = ('Fall High','FLHI')
    FLLO = ('Fall Low','FLLO')
    FLDE = ('Fall Dead','FLDE')
    LAND = ('Land','LAND')
    CRSH = ('Crashed','CRSH')

    SWIM = ('Swim','SWIM')
    PDDL = ('Paddle','PDDL')

    CMBT = ('Combat','CMBT')
    CMTW = ('Combat Walk','CMTW')
    CMTT = ('Combat Trot','CMTT')

    BIPD = ('Bipedal','BIPD')
    STLK = ('Stalk','STLK')
    WALK = ('Walk','WALK')
    WWLK = ('Walk (Wounded)','WWLK')
    WFST = ('Walk Fast','WFST')
    PACE = ('Pace','PACE')
    TROT = ('Trot','TROT')
    CNTR = ('Canter','CNTR')
    GLLP = ('Gallop','GLLP')

    RCTL = ('Rectilinear','RCTL')
    UNDL = ('Undulatory','UNDL')

class _SUBSTATE:
    NONE = ('None', 'NONE')

    BIND = ('Bind Pose', 'BIND')

    WAIT = ('Wait', 'WAIT')
    MOVE = ('Move', 'MOVE')

    AGGR = ('Aggressive', 'AGGR')
    STUN = ('Stunned', 'STUN')
    SCRD = ('Scared', 'SCRD')
    EXHS = ('Exhausted', 'EXHS')
    SLPY = ('Sleepy', 'SLPY')
    NEUT = ('Neutral', 'NEUT')
    FCSD = ('Focused', 'FCSD')
    EXCI = ('Excited', 'EXCI')

    CALL = ('Call/Howl', 'CALL')
    BARK = ('Conflict Bark', 'BARK')
    NTFY = ('Notify Bark', 'NTFY')
    GRWL = ('Warn/Growl', 'GRWL')
    WHNE = ('Whine', 'WHNE')
    YELP = ('Yelp', 'YELP')

    BITE = ('Bite', 'BITE')
    BUCK = ('Buck', 'BUCK')
    AMBS = ('Ambush', 'AMBS')
    CLAW = ('Claws', 'CLAW')
    KICK = ('Kick', 'KICK')
    HEAD = ('Headbutt', 'HEAD')
    HORN = ('Horns', 'HORN')
    LEAP = ('Pounce', 'LEAP')
    REAR = ('Rear', 'REAR')

    DGDE = ('Dodge', 'DGDE')
    FAKE = ('Fake/Feint', 'FAKE')
    IMPT = ('Impact', 'IMPT')
    PSTN = ('Position', 'PSTN')


    ASND = ('Ascend', 'ASND')
    DSND = ('Descend', 'DSND')

    ENTR = ('Enter', 'ENTR')
    EXIT = ('Exit', 'EXIT')

    FALL = ('Fall', 'FALL')
    JUMP = ('Jump','JUMP')

    DIVE = ('Dive', 'DIVE')
    SBMR = ('Submerge', 'SBMR')
    EMRG = ('Emerge', 'EMRG')

    TKOF = ('Takeoff', 'TKOF')
    LAND = ('Land', 'LAND')
    CRSH = ('Crash', 'CRSH')

    CLEN = ('Clean', 'CLEN')
    DEFE = ('Defecate', 'DEFE')
    DIGG = ('Dig', 'DIGG')
    DRNK = ('Drink', 'DRNK')
    EATT = ('Eat', 'EATT')
    GROO = ('Groom', 'GROO')
    LICK = ('Lick', 'LICK')
    REST = ('Rest', 'REST')
    MARK = ('Urinate Mark', 'MARK')
    URIN = ('Urinate', 'URIN')
    SCTR = ('Scratch Tree', 'SCTR')
    SLEP = ('Sleep', 'SLEP')
    CGHT = ('Caught/Captured', 'CGHT')
    GRAB = ('Grab', 'GRAB')

    DIEC = ('Death (Combat)', 'DIEC')
    DIEI = ('Death (Injury)', 'DIEI')

    LSTN = ('Listen', 'LSTN')
    LOOK = ('Look', 'LOOK')
    SMAR = ('Smell (Air)', 'SMEA')
    SMGR = ('Smell (Ground)', 'SMEG')
    SMEL = ('Smell', 'SMEL')

class _DIRECTION:
    NONE = ('None','NONE')
    LEFT = ('Left','LEFT')
    RGHT = ('Right','RGHT')
    FRNT = ('Front','FRNT')
    BACK = ('Back','BACK')
    UPWR = ('Up','UPWR')
    DOWN = ('Down','DOWN')
    UPLT = ('Up Left','UPLT')
    UPRT = ('Up Right','UPRT')
    DNLT = ('Down Left','DNLT')
    DNRT = ('Down Right','DNRT')
    FRLT = ('Front Left','FRLT')
    FRRT = ('Front Right','FRRT')
    BKLT = ('Back Left','BKLT')
    BKRT = ('Back Right','BKRT')
    LOWW = ('Low','LOWW')
    HIGH = ('High','HIGH')
    MIDD = ('Middle','MIDD')


class AM_ENUM:
    @classmethod
    def create_enum_dict(cls, enum_tuples):
        enums = []
        default = ''

        for key in enum_tuples.keys():
            description = enum_tuples[key]
            if default == '':
                default = key

            item = (key, description, description)
            enums.append(item)

        get_enums = lambda: (enums)
        get_default = lambda: (default)
        return enums, default, get_enums, get_default

    def __init__(self):
        self.VALS = {}
        self.ENUM, self.DEFAULT, self.GET_ENUM, self.GET_DEFAULT = self.create_enum_dict(self.VALS)

    def refresh(self):
        self.ENUM, self.DEFAULT, self.GET_ENUM, self.GET_DEFAULT = self.create_enum_dict(self.VALS)

    def get_enum(self):
        return self.ENUM

    def get_default(self):
        return self.DEFAULT

class AM_Pose():
    def __init__(self):
        self.substate_enum = AM_ENUM()
        self.direction_enum = AM_ENUM()

class AM_Category():
    def __init__(self):
        self.mask_enum = AM_ENUM()
        self.stage_enum = AM_ENUM()
        self.pose_enum = AM_ENUM()
        self.poses = {}

class AM_Environment():
    def __init__(self):
        self.category_enum = AM_ENUM()
        self.categories = {}

class AM_ENVS:
    def _get_env_set(self):
        _E, _C, _M, _S, _P, _SS,_D = _ENVIRONMENT, _CATEGORY, _MASK, _STAGE, _POSE, _SUBSTATE,_DIRECTION
        environments = {}
        EnvMetadata = namedtuple('EnvMetadata', 'all_categories all_masks all_stages all_poses')
        PoseMetadata = namedtuple('PoseMetadata', 'all_substates all_directions')

        # Environment: None
        environments[_E.NONE] = EnvMetadata(
            #all_categories =
            [
                _C.BIND,_C.VOCL,_C.EMOT,_C.SENS
            ],
            #all_masks =
            [
                [_M.FULL], #_C.BIND
                [_M.HEAD], #_C.VOCL
                [_M.HEAD], #_C.EMOT
                [_M.HEAD], #_C.SENS
            ],
            #all_stages =
            [
                [_S.LOOP], #_C.BIND
                [_S.ONCE], #_C.VOCL
                [_S.LOOP], #_C.EMOT
                [_S.ONCE], #_C.SENS
            ],
            #all_poses =
            [
                {  #_C.BIND
                    _P.NONE : PoseMetadata( [ _SS.NONE ], [ _D.NONE ] ),
                    _P.PELT : PoseMetadata( [ _SS.NONE ], [ _D.NONE ] ),
                },
                {   #_C.VOCL
                    _P.NONE : PoseMetadata(
                        [ _SS.CALL,_SS.BARK,_SS.NTFY,_SS.GRWL,_SS.WHNE,_SS.YELP ],  [ _D.NONE ] ),
                },
                {   #_C.EMOT
                    _P.NONE : PoseMetadata(
                        [ _SS.AGGR,_SS.STUN,_SS.SCRD,_SS.EXHS,_SS.SLPY,_SS.NEUT,_SS.FCSD,_SS.EXCI ],  [ _D.NONE ] ),
                },
                {   #_C.SENS
                    _P.NONE : PoseMetadata(
                        [ _SS.LSTN,_SS.LOOK,_SS.SMEL ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.UPWR,_D.DOWN ] ),
                },
            ]
        )

        # Environment: Aquatic
        environments[_E.AQUA] = EnvMetadata(
            #all_categories =
            [
                _C.IDLE,_C.MOVE,_C.TRNS,_C.CMBT,_C.DEAD
            ],
            #all_masks =
            [
                [_M.FULL], # _C.IDLE
                [_M.FULL], # _C.MOVE
                [_M.FULL], # _C.TRNS
                [_M.FULL], # _C.CMBT
                [_M.FULL], # _C.DEAD
            ],
            #all_stages =
            [
                [_S.LOOP], # _C.IDLE
                [_S.LOOP], # _C.MOVE
                [_S.ONCE], # _C.TRNS
                [_S.ONCE], # _C.CMBT
                [_S.ONCE], # _C.DEAD
            ],
            #all_poses =
            [
                {   # _C.IDLE
                    _P.IDLF : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),  # IDLF = ('Float','IDLF')
                },
                {   # _C.MOVE
                    _P.SWIM : PoseMetadata( [ _SS.MOVE ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.UPWR,_D.DOWN ] ), # SWIM = ('Swim','SWIM')
                },
                {   # _C.TRNS
                    _P.SWIM : PoseMetadata( [ _SS.EMRG ],  [ _D.NONE ] ),
                },
                {   # _C.CMBT
                    _P.IDLF : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                    [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.SWIM : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.CLAW ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ), # DIEC = ('Death (Combat)', 'DIEC')
                },
                {   # _C.DEAD
                    _P.DEDW : PoseMetadata( [ _SS.NONE ],  [ _D.NONE ] ), # DEDW = ('Dead (Aquatic)','DEDW')
                },
            ]
        )

        # Environment: Aquatic Surface
        environments[_E.SURF] = EnvMetadata(
            #all_categories =
            [
                _C.IDLE,_C.ACTV,_C.MOVE,_C.TRNS,_C.CMBT,_C.DEAD
            ],
            #all_masks =
            [
                [_M.FULL], # _C.IDLE
                [_M.FULL], # _C.ACTV
                [_M.FULL], # _C.MOVE
                [_M.FULL], # _C.TRNS
                [_M.FULL], # _C.CMBT
                [_M.FULL], # _C.DEAD
            ],
            #all_stages =
            [
                [_S.LOOP], # _C.IDLE
                [_S.ONCE], # _C.ACTV
                [_S.LOOP], # _C.MOVE
                [_S.ONCE], # _C.TRNS
                [_S.ONCE], # _C.CMBT
                [_S.ONCE], # _C.DEAD
            ],
            #all_poses =
            [
                {   # _C.IDLE
                    _P.IDLF : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                    _P.IDLT : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                },
                {   # _C.ACTV
                    _P.IDLF : PoseMetadata( [ _SS.DRNK, _SS.EATT, _SS.CLEN, _SS.GROO ],  [ _D.NONE ] ),
                    _P.RSTW : PoseMetadata( [ _SS.REST ],  [ _D.NONE ] ),
                    _P.SLPW : PoseMetadata( [ _SS.SLEP ],  [ _D.NONE ] ),
                },
                {   # _C.MOVE
                    _P.PDDL : PoseMetadata( [ _SS.MOVE ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.UPWR,_D.DOWN ] ), # PDDL = ('Paddle','PDDL')
                },
                {   # _C.TRNS
                    _P.PDDL : PoseMetadata( [ _SS.SBMR, _SS.EXIT ],  [ _D.NONE ] ),
                },
                {   # _C.CMBT
                    _P.IDLF : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                    [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.RSTW : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                    [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.SLPW : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                    [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.IDLT : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.CLAW ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.PDDL : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.CLAW ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                },
                {   # _C.DEAD
                    _P.DEDW : PoseMetadata( [ _SS.NONE ],  [ _D.NONE ] ), # DEDW = ('Dead (Aquatic)','DEDW')
                },
            ]
        )

        # Environment: Terrestrial
        environments[_E.LAND] = EnvMetadata(
            #all_categories =
            [
                _C.IDLE,_C.ACTV,_C.MOVE,_C.TRNS,_C.CMBT,_C.DEAD
            ],
            #all_masks =
            [
                [_M.FULL], # _C.IDLE
                [_M.FULL], # _C.ACTV
                [_M.FULL], # _C.MOVE
                [_M.FULL], # _C.TRNS
                [_M.FULL], # _C.CMBT
                [_M.FULL], # _C.DEAD
            ],
            #all_stages =
            [
                [_S.LOOP], # _C.IDLE
                [_S.ONCE], # _C.ACTV
                [_S.LOOP], # _C.MOVE
                [_S.ONCE], # _C.TRNS
                [_S.ONCE], # _C.CMBT
                [_S.ONCE], # _C.DEAD
            ],
            #all_poses =
            [
                {   # _C.IDLE
                    _P.IDLG : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                    _P.IDLW : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                    _P.SITG : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                    _P.RSTG : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                },

                {   # _C.ACTV
                    _P.IDLG : PoseMetadata( [ _SS.CLEN,_SS.DEFE,_SS.DIGG,_SS.DRNK,_SS.EATT,_SS.GROO,_SS.LICK,_SS.MARK,_SS.URIN,_SS.SCTR ],  [ _D.NONE ] ),
                    _P.SITG : PoseMetadata( [ _SS.CLEN,_SS.EATT,_SS.GROO ],                                                                 [ _D.NONE ] ),
                    _P.RSTG : PoseMetadata( [ _SS.CLEN,_SS.EATT,_SS.GROO,_SS.REST ],                                                        [ _D.NONE ] ),
                    _P.SLPG : PoseMetadata( [ _SS.SLEP ],                                                                                   [ _D.NONE ] ),
                },

                {   # _C.MOVE
                    _P.BIPD : PoseMetadata( [ _SS.MOVE,         ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT ] ),
                    _P.STLK : PoseMetadata( [ _SS.MOVE,         ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT ] ),
                    _P.WALK : PoseMetadata( [ _SS.MOVE,_SS.JUMP ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT,_D.UPWR,_D.DOWN ] ),
                    _P.WWLK : PoseMetadata( [ _SS.MOVE          ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.WFST : PoseMetadata( [ _SS.MOVE,_SS.JUMP ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT,_D.UPWR,_D.DOWN ] ),
                    _P.PACE : PoseMetadata( [ _SS.MOVE,_SS.JUMP ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT,_D.UPWR,_D.DOWN ] ),
                    _P.TROT : PoseMetadata( [ _SS.MOVE,_SS.JUMP ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT,_D.UPWR,_D.DOWN ] ),
                    _P.CNTR : PoseMetadata( [ _SS.MOVE,_SS.JUMP ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT,_D.UPWR,_D.DOWN ] ),
                    _P.GLLP : PoseMetadata( [ _SS.MOVE,_SS.JUMP ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT,_D.UPWR,_D.DOWN ] ),
                    _P.RCTL : PoseMetadata( [ _SS.MOVE ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT,_D.UPWR,_D.DOWN ] ),
                    _P.UNDL : PoseMetadata( [ _SS.MOVE ], [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK,_D.FRLT,_D.FRRT,_D.BKLT,_D.BKRT,_D.UPWR,_D.DOWN ] ),
                },
                {   # _C.TRNS

                    _P.WALK : PoseMetadata( [ _SS.ASND, _SS.ENTR ], [ _D.NONE ] ),
                    _P.FLLO : PoseMetadata( [ _SS.DIVE ], [ _D.NONE ] ),
                    _P.IDLG : PoseMetadata( [ _SS.TKOF ], [ _D.NONE ] )
                },
                {   # _C.CMBT
                    _P.BIPD : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.CNTR : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.GLLP : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.IDLG : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.PACE : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.RSTG : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.SITG : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.SLPG : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.STLK : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.TROT : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.WALK : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.WFST : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],           [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.IDLW : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.DIEI ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.WWLK : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.DIEI ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.CMBT : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.BUCK,_SS.AMBS,_SS.CLAW,_SS.KICK,_SS.HEAD,_SS.HORN,_SS.LEAP,_SS.REAR,_SS.STUN ], [ _D.NONE,_D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.CMTW : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.DIEI,_SS.BITE,_SS.HEAD,_SS.HORN ],                                              [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.CMTT : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.BUCK,_SS.AMBS,_SS.CLAW,_SS.KICK,_SS.HEAD,_SS.HORN,_SS.LEAP,_SS.REAR ], [ _D.NONE,_D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                },
                {   # _C.DEAD
                    _P.DEDT : PoseMetadata( [ _SS.NONE ],  [ _D.NONE ] ),
                },
            ]
        )

        # Environment: Subterranean
        environments[_E.SUBT] = EnvMetadata(
            #all_categories =
            [
                _C.IDLE,_C.TRNS
            ],
            #all_masks =
            [
                [_M.FULL], # _C.IDLE
                [_M.FULL], # _C.TRNS
            ],
            #all_stages =
            [
                [_S.LOOP], # _C.IDLE
                [_S.ONCE], # _C.TRNS
            ],
            #all_poses =
            [
                {   # _C.IDLE
                    _P.BRRW : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                },
                {   # _C.TRNS
                    _P.BRRW : PoseMetadata( [ _SS.EXIT ],  [ _D.NONE ] ),
                },
            ]
        )

        # Environment: Arboreal
        environments[_E.TREE] = EnvMetadata(
            #all_categories =
            [
                _C.IDLE,_C.ACTV,_C.MOVE,_C.TRNS,_C.CMBT
            ],
            #all_masks =
            [
                [_M.FULL], # _C.IDLE
                [_M.FULL], # _C.ACTV
                [_M.FULL], # _C.MOVE
                [_M.FULL], # _C.TRNS
                [_M.FULL], # _C.CMBT
            ],
            #all_stages =
            [
                [_S.LOOP], # _C.IDLE
                [_S.ONCE], # _C.ACTV
                [_S.LOOP], # _C.MOVE
                [_S.ONCE], # _C.TRNS
                [_S.ONCE], # _C.CMBT
            ],
            #all_poses =
            [
                {   # _C.IDLE
                    _P.IDLT : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                    _P.SITT : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                    _P.RSTT : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                    _P.HANG : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                },
                {   # _C.ACTV
                    _P.IDLT : PoseMetadata( [ _SS.CLEN,_SS.DEFE,_SS.EATT,_SS.GROO,_SS.SCTR ],  [ _D.NONE ] ),
                    _P.SITT : PoseMetadata( [ _SS.CLEN,_SS.DEFE,_SS.EATT,_SS.GROO ],           [ _D.NONE ] ),
                    _P.RSTT : PoseMetadata( [ _SS.REST, _SS.CLEN, _SS.GROO ],                  [ _D.NONE ] ),
                    _P.SLPT : PoseMetadata( [ _SS.SLEP ],                                      [ _D.NONE ] ),
                },
                {   # _C.MOVE
                    _P.CLMB : PoseMetadata( [ _SS.MOVE,_SS.WAIT ],  [ _D.LEFT,_D.RGHT,_D.UPWR,_D.DOWN,_D.UPLT,_D.UPRT,_D.DNLT,_D.DNRT ] ),
                    _P.WLKT : PoseMetadata( [ _SS.MOVE ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.HANG : PoseMetadata( [ _SS.MOVE ],  [ _D.UPWR ] ),
                },
                {   # _C.TRNS
                    _P.IDLT : PoseMetadata( [ _SS.FALL ],  [ _D.NONE ] ),
                    _P.SITT : PoseMetadata( [ _SS.FALL ],  [ _D.NONE ] ),
                    _P.RSTT : PoseMetadata( [ _SS.FALL ],  [ _D.NONE ] ),
                    _P.SLPT : PoseMetadata( [ _SS.FALL ],  [ _D.NONE ] ),
                    _P.CLMB : PoseMetadata( [ _SS.DSND, _SS.JUMP, _SS.FALL ],  [ _D.NONE ] ),
                    _P.HANG : PoseMetadata( [ _SS.FALL ],  [ _D.NONE ] ),
                },
                {   # _C.CMBT
                    _P.IDLT : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                    [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.SITT : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                    [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.RSTT : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                    [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.SLPT : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                    [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.CLMB : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.CLAW ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.WLKT : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.CLAW ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] )
                }
            ]
        )

        # Environment: Aerial
        environments[_E.AERL] = EnvMetadata(
            #all_categories =
            [
                _C.IDLE,_C.MOVE,_C.TRNS,_C.CMBT
            ],
            #all_masks =
            [
                [_M.FULL], # _C.IDLE
                [_M.FULL], # _C.MOVE
                [_M.FULL], # _C.TRNS
                [_M.FULL], # _C.CMBT
            ],
            #all_stages =
            [
                [_S.LOOP], # _C.IDLE
                [_S.LOOP], # _C.MOVE
                [_S.ONCE], # _C.TRNS
                [_S.ONCE], # _C.CMBT
            ],
            #all_poses =
            [
                {   # _C.IDLE
                    _P.HOVR : PoseMetadata( [ _SS.WAIT ],  [ _D.NONE ] ),
                },
                {   # _C.MOVE
                    _P.HOVR : PoseMetadata( [ _SS.MOVE ],  [ _D.LEFT,_D.RGHT,_D.UPWR,_D.DOWN,_D.UPLT,_D.UPRT,_D.DNLT,_D.DNRT ] ),
                    _P.FLYY : PoseMetadata( [ _SS.MOVE ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.UPWR,_D.DOWN,_D.UPLT,_D.UPRT,_D.DNLT,_D.DNRT,_D.FRLT,_D.FRRT ] ),
                    _P.GLDE : PoseMetadata( [ _SS.MOVE ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.UPWR,_D.DOWN,_D.UPLT,_D.UPRT,_D.DNLT,_D.DNRT,_D.FRLT,_D.FRRT ] ),
                    _P.DIVE : PoseMetadata( [ _SS.MOVE ],  [ _D.LEFT,_D.RGHT,_D.FRNT,_D.DOWN,_D.DNLT,_D.DNRT,_D.FRLT,_D.FRRT ] ),
                },
                {   # _C.TRNS
                    _P.LAND : PoseMetadata( [ _SS.LAND ],  [ _D.NONE ] ),
                    _P.FLHI : PoseMetadata( [ _SS.CRSH ],  [ _D.NONE ] ),
                    _P.FLDE : PoseMetadata( [ _SS.CRSH ],  [ _D.NONE ] ),
                },
                {   # _C.CMBT
                    _P.FLYY : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.CLAW ],            [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.GLDE : PoseMetadata( [ _SS.IMPT,_SS.DIEC,_SS.BITE,_SS.CLAW, _SS.GRAB ],  [ _D.NONE,_D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                    _P.DIVE : PoseMetadata( [ _SS.IMPT,_SS.DIEC ],                              [ _D.LEFT,_D.RGHT,_D.FRNT,_D.BACK ] ),
                }
            ]
        )

        return environments

    def _set_enum_only(self, pp, pkv):
        pp.VALS[pkv[1]] = pkv[0]

    def _set(self, p, pp, pkv, pnew):
        pp.VALS[pkv[1]] = pkv[0]
        p[pkv[1]] = pnew
        p_var = p[pkv[1]]

        return p_var

    def __init__(self):
        self.actors_enum = AM_ENUM()

        for actor_key in dir(ACTORS):
            val = getattr(ACTORS, actor_key, None)
            if val and type(val) == tuple:
                self._set_enum_only(self.actors_enum, val)

        self.actors_enum.refresh()

        self.env_enum = AM_ENUM()
        self.envs = {}

        e, ee = self.envs, self.env_enum

        environments = self._get_env_set()

        for env_key in environments.keys():
            env_data = environments[env_key]

            env = self._set(e, ee, env_key, AM_Environment())
            c = env.categories
            ce = env.category_enum

            for index, category_key in enumerate(env_data.all_categories):
                category   = self._set(c, ce, category_key, AM_Category())
                mask_enum  = category.mask_enum
                stage_enum = category.stage_enum
                poses      = category.poses
                pose_enum  = category.pose_enum

                length_categories = len(env_data.all_categories)
                length_masks = len(env_data.all_masks)
                length_stages = len(env_data.all_stages)
                length_poses = len(env_data.all_poses)

                if length_categories != length_masks:
                    print('[{0}]: Length mismatch: Categories: {1}  vs. Masks: {2}'.format(env_key, length_categories, length_masks))
                if length_categories != length_stages:
                    print('[{0}]: Length mismatch: Categories: {1}  vs. Stages: {2}'.format(env_key, length_categories, length_stages))
                if length_categories != length_poses:
                    print('[{0}]: Length mismatch: Categories: {1}  vs. Poses: {2}'.format(env_key, length_categories, length_poses))

                for mask_key in env_data.all_masks[index]:
                    self._set_enum_only(mask_enum, mask_key)

                for stage_key in env_data.all_stages[index]:
                    self._set_enum_only(stage_enum, stage_key)


                pose_values = env_data.all_poses[index]

                for pose_key in pose_values.keys():

                    pose = self._set(poses, pose_enum, pose_key, AM_Pose())

                    substate_enum = pose.substate_enum
                    direction_enum = pose.direction_enum

                    pose_data = pose_values[pose_key]

                    for substate_key in pose_data.all_substates:
                        self._set_enum_only(substate_enum, substate_key)

                    for direction_key in pose_data.all_directions:
                        self._set_enum_only(direction_enum, direction_key)

                    substate_enum.refresh()
                    direction_enum.refresh()

                mask_enum.refresh()
                stage_enum.refresh()
                pose_enum.refresh()

            ce.refresh()
        ee.refresh()