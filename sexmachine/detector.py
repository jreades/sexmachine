import os
import gzip
import operator
from .mapping import map_name

class NoCountryError(Exception):
    """Raised when unknown country is queried"""
    pass

class Detector:
    """Get gender by first name"""

    names     = {}
    countries = {}

    default_fn = os.path.join('data','nam_dict.txt.gz')

    gmappings = {
        'M':  'M',
        '1M': 'MM',
        '?M': 'MM',
        'F':  'F',
        '1F': 'MF',
        '?F': 'MF',
        '?':  'A',
        'NA': 'U'
    }

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

        self.unknown_value = self.gmappings['NA']

        if len(self.countries) == 0:
            self.countries = {k: v for v, k in enumerate(self.COUNTRIES)}
            for v, k in enumerate(self.COUNTRIES):
                self.countries[k.lower().replace(" ","_")] = v

        if len(self.names) == 0:
            self._parse(os.path.join(os.path.dirname(__file__), self.default_fn))

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

            self._set(name, self.gmappings[gender], freq)

    def _set(self, name, gender, country_values):
        """Sets gender and relevant country values for names dictionary of detector"""
        if '+' in name:
            for replacement in ['', ' ', '-']:
                self._set(name.replace('+', replacement), gender, country_values)
        else:
            if name not in self.names:
                self.names[name] = {}
            self.names[name][gender] = country_values
    
    def dump_name(self, name):
        for key, val in self.names[name].items(): 
            print(key)
            for i in range(0, len(self.COUNTRIES)):
                if val[i] != '0': print("\t" + self.COUNTRIES[i] + " -> " + str(int(val[i],16)))
    
    def _name_freq(self, country_values):
        return sum(list(map(lambda c: int(c,16), country_values)))

    def _max_prob(self, ds):
        mv = max(ds.items(), key=operator.itemgetter(1))[0]
        
        if ds[mv] == 0:
            return self.gmappings['NA']
        else:
            return mv

    def _global_prob(self, name, strict=False):

        glob_results = {} # Store the global results 

        for key, val in self.names[name].items():
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
        for key, val in self.names[name].items():
            ctry_results[key] = int(val[ix],16)
            glob_results[key] = self._name_freq(val)
        
        if strict is False and max(ctry_results.values()) == 0: 
            return self._max_prob(glob_results)
        else:
            return self._max_prob(ctry_results)

    def get_gender(self, name, country=None, strict=False):
        """Returns best gender for the given name and country pair"""
        if name not in self.names:
            return self.unknown_value

        elif not country:
            return self._global_prob(name)

        elif country in self.countries:
            return self._country_prob(name, country, strict)

        else:
            raise NoCountryError("No such country: %s" % country)
