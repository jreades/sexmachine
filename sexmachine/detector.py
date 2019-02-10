import os
import gzip
import operator
from .mapping import map_name

class NoCountryError(Exception):
    """Raised when unknown country is queried"""
    pass

class Detector(object):
    """Get gender by first name"""

    names     = {}
    countries = {}

    default_fn = os.path.join('data','nam_dict.txt.gz')

    male        = 'M'
    female      = 'F'
    androgynous = 'A'
    unknown     = 'U'
    mmale       = 'MM'
    mfemale     = 'MF'

    COUNTRIES = [ x.strip() for x in """Great Britain, Ireland, USA, Italy, Malta, Portugal, Spain, France, 
                   Belgium, Luxembourg, The Netherlands, East Frisia, Germany, Austria, 
                   Switzerland, Iceland, Denmark, Norway, Sweden, Finland, Estonia, Latvia, 
                   Lithuania, Poland, Czech Republic, Slovakia, Hungary, Romania, 
                   Bulgaria, Bosnia and Croatia, Kosovo, Macedonia, Montenegro, Serbia, 
                   Slovenia, Albania, Greece, Russia, Belarus, Moldova, Ukraine, Armenia, 
                   Azerbaijan, Georgia, The Stans, Turkey, Arabia, Israel, China, India, 
                   Japan, Korea, Vietnam, Other
                 """.split(",") ]

    def __init__(self):

        """Creates a detector parsing given data file"""

        if len(Detector.countries) == 0:
            Detector.countries = {k: v for v, k in enumerate(Detector.COUNTRIES)}
            for v, k in enumerate(Detector.COUNTRIES):
                Detector.countries[k.lower().replace(" ","_")] = v

        self.mapping = {
            'M':  Detector.male,
            'F':  Detector.female,
            '1M': Detector.mmale,
            '?M': Detector.mmale,
            '1F': Detector.mfemale,
            '?F': Detector.mfemale,
            '?':  Detector.androgynous
        }

        self.load()

    def _parse(self, filename):
        """Opens data file and for each line, calls _eat_name_line"""
        with gzip.open(filename, 'r') as f:
            for line in f:
                self._eat_name_line(line.decode('iso8859-1').strip())

    def _eat_name_line(self, line):
        """Parses one line of data file"""
        if line[0] not in "#=":
            gender = line[0:2].strip()
            name   = map_name(line[3:29].strip())
            freq   = line[30:-1].replace(" ","0")

            self._set(name, gender, freq)

    def _set(self, name, gender, country_values):
        """Sets gender and relevant country values for names dictionary of detector"""

        if '+' in name:
            for replacement in ['', ' ', '-']:
                self._set(name.replace('+', replacement), gender, country_values)
        else:
            if name not in Detector.names:
                Detector.names[name] = {}

            # g = Detector.unknown
            # if gender=='M':
            #     g = Detector.male
            # elif gender=='F':
            #     g = Detector.female
            # elif gender=='1M':
            #     g = Detector.mmale
            # elif gender=='?M':
            #     g = Detector.mmale
            # elif gender=='1F':
            #     g = Detector.mfemale
            # elif gender=='?F':
            #     g = Detector.mfemale
            # elif gender=='?':
            #     g = Detector.androgynous

            Detector.names[name][self.mapping[gender]] = country_values
    
    def dump_name(self, name):
        if len(Detector.names) == 0:
            self._parse(os.path.join(os.path.dirname(__file__), Detector.default_fn))

        for key, val in Detector.names[name].items(): 
            print(key)
            for i in range(0, len(Detector.COUNTRIES)):
                if val[i] != '0': print("\t" + Detector.COUNTRIES[i] + " -> " + str(int(val[i],16)))
    
    def _name_freq(self, country_values):
        return sum(list(map(lambda c: int(c,16), country_values)))

    def _max_prob(self, ds):
        mv = max(ds.items(), key=operator.itemgetter(1))[0]
        
        if ds[mv] == 0:
            return Detector.unknown
        else:
            return mv

    def _global_prob(self, name, strict=False):

        glob_results = {} # Store the global results 

        for key, val in Detector.names[name].items():
            glob_results[key] = self._name_freq(val)

        return self._max_prob(glob_results)

    # Needs a tie-breaker option based on default values? Or a 'U' value
    # for 'we don't know'? Something different from Androgyne? Guess this is 
    # where the number of countries comes into it, though seems to me you
    # also want to weight by country population! Maybe a strict=T/F param
    # based on whether you want it to infer a value or be specific to that 
    # country?
    def _country_prob(self, name, ctry, strict=False):
        
        ctry_results = {} # Store the by-country results
        glob_results = {} # Store the global results 

        ix = self.countries[ctry]
        for key, val in Detector.names[name].items():
            ctry_results[key] = int(val[ix],16)
            glob_results[key] = self._name_freq(val)
        
        if strict is False and max(ctry_results.values()) == 0: 
            return self._max_prob(glob_results)
        else:
            return self._max_prob(ctry_results)

    def load(self):
        if len(Detector.names) == 0:
            self._parse(os.path.join(os.path.dirname(__file__), Detector.default_fn))
    
    def reload(self):
        Detector.names = {}
        self.load()

    def get_gender(self, name, country=None, strict=False):
        """Returns best gender for the given name and country pair"""
        if len(Detector.names) == 0:
            self._parse(os.path.join(os.path.dirname(__file__), Detector.default_fn))

        if name not in Detector.names:
            return Detector.unknown

        elif not country:
            return self._global_prob(name)

        elif country in Detector.countries:
            return self._country_prob(name, country, strict)

        else:
            raise NoCountryError("No such country: %s" % country)
