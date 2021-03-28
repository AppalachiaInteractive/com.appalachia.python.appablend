import bpy
import cspy
from cspy.animation_metadata import AnimationMetadataBase
from cspy import subtypes

class Constants:
    ICON_PANEL = 'IMGDISPLAY'
    ICON_SHEET = "FILE_BLANK"

    LINE_STRIP_CHARS = [ '\t', '\r', '\n', ' ']

    PREFIXES = ['.', '-', ' ', '_', ',']

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

class Utils:
    @classmethod
    def get_casing_set(cls, v):
        vals = []
        vals.append(v)
        vals.append(v.lower())
        vals.append(v.upper())
        vals.append(v.title())
        return vals

    @classmethod
    def get_full_key_set(cls, d, need_empty_prefix):
        fullkeys = []
        for key in d.keys():
            value = d[key]
            keys = cls.get_casing_set(key)

            for xkey in keys:
                if need_empty_prefix:
                    fullkeys.append([key, xkey, value])
                for pfx in Constants.PREFIXES:
                    fullkey = '{0}{1}'.format(pfx, xkey)
                    fullkeys.append([key, fullkey, value])
        return fullkeys

    @classmethod
    def replacement_collection(cls, clip_name, d, need_empty_prefix, format_string):
        c= clip_name.strip()
        hits = set()

        for okey, key, value in cls.get_full_key_set(d, need_empty_prefix):
            c = c.strip()
            if okey in hits:
                continue
            if key in c:
                hits.add(okey)
                c = c.replace(key, '').strip()
                c = format_string.format(c, value)
                c = c.strip()

        c = c.strip()
        return c

    @classmethod
    def strip_many(cls, string, chars):

        hit = True

        while(hit):
            hit = False
            for char in chars:
                new = string.strip(char)
                if new != string:
                    hit = True
                    string = new

        return string



