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
        """Create a new Gender Detector object

        Args:

        Returns:
            :obj: Object ot type Detector
        """

        # If the countries dictionary hasn't been loaded
        # yet then we will load it here -- this is shared
        # between all objects of this class and so should
        # be read-only
        if len(Detector.countries) == 0:
            Detector.countries = {k: v for v, k in enumerate(Detector.COUNTRIES)}
            for v, k in enumerate(Detector.COUNTRIES):
                Detector.countries[k.lower().replace(" ","_")] = v

        # This maps the inputs from the nam_dict.txt
        # file in to a standard gender descriptor --
        # these can be modified fairly easily prior
        # to instantiation of the first object of this
        # class. After that the results may be fairly
        # unpredictable: there is a reload method that
        # may enable this to be changed afterwards but
        # I have not properly tested it.
        self.mapping = {
            'M':  Detector.male,
            'F':  Detector.female,
            '1M': Detector.mmale,
            '?M': Detector.mmale,
            '1F': Detector.mfemale,
            '?F': Detector.mfemale,
            '?':  Detector.androgynous
        }
        
        # Load the nam_dict data file.
        self.load()

    def _parse(self, filename):
        """Private method: opens data file and for each line, calls _eat_name_line"""
        with gzip.open(filename, 'r') as f:
            for line in f:
                self._eat_name_line(line.decode('iso8859-1').strip())

    def _eat_name_line(self, line):
        """Parses one line of data file and converts
        it into a data representation.
        
        Lines starting '#' or '=' are skipped.
        
        The rest of the line is handled as follows:
        - Characters 0-2 are interpreted as gender (M, F, 1M, 1F, ?M, ?F, ?)
        - Characters 3-29 are interpreted as the name
        - Characters 30-End are interpreted as data (each column/character is a hexadecimal number for a country)
        """
        if line[0] not in "#=":
            gender = line[0:2].strip()
            name   = map_name(line[3:29].strip())
            freq   = line[30:-1].replace(" ","0")

            self._set(name, gender, freq)

    def _set(self, name, gender, country_values):
        """Sets gender and relevant country values into the data structure."""
        
        # Sets variations on spelling/hyphenation
        if '+' in name:
            for replacement in ['', ' ', '-']:
                self._set(name.replace('+', replacement), gender, country_values)
        else:
            if name not in Detector.names:
                Detector.names[name] = {}

            Detector.names[name][self.mapping[gender]] = country_values
    
    def dump_name(self, name):
        """Useful debugging/inspection tool for the data structure.

        Args:
            name (str): The name to inspect.

        Returns:
            None: No return value, it simply outputs information for each country.

        """
        if len(Detector.names) == 0:
            self._parse(os.path.join(os.path.dirname(__file__), Detector.default_fn))

        for key, val in Detector.names[name].items(): 
            print(key)
            for i in range(0, len(Detector.COUNTRIES)):
                if val[i] != '0': print("\t" + Detector.COUNTRIES[i] + " -> " + str(int(val[i],16)))
    
    def _name_freq(self, country_values):
        """Calculates a sum across all hexadecimal country values for a given name."""
        return sum(list(map(lambda c: int(c,16), country_values)))

    def _max_prob(self, ds):
        """Works out which gender is 'most likely' (max probability)
        based on a data structure that contains either the sum for
        each gender or the value for a specific country."""
        mv = max(ds.items(), key=operator.itemgetter(1))[0]
        
        if ds[mv] == 0:
            return Detector.unknown
        else:
            return mv

    def _global_prob(self, name, strict=False):
        """Private: works out a likelihood for a given name.

        Args:
            name (str): The name to search for.
            strict (bool): Should search only on specified country. Ignored by this method but ensures consistent interface.

        Returns:
            str: The gender thought most likely to be associated with the name.

        """
        glob_results = {} # Store the global results 

        for key, val in Detector.names[name].items():
            glob_results[key] = self._name_freq(val)

        return self._max_prob(glob_results)

    def _country_prob(self, name, ctry, strict=False):
        """Private: works out a likelihood for a given name.

        I'm unclear as to whether these results should be weighted by the
        population of the countries (e.g. a '1' for USA and a '1' for 
        Luxembourg should not be treated equally when trying to work out
        the likely gender).
        
        The strict parameter set to True means that _only_ the specified 
        country is considered when inferring gender. If false (the default)
        then _if_ no specific country value is found then the global 
        distribution will be used. If true (the other option) then it 
        will return _only_ the country value _even if_ that value is 0.

        Args:
            name (str): The name to search for.
            strict (bool): Should search be confined to only the specified country. Defaults to False.

        Returns:
            str: The gender thought most likely to be associated with the name.

        """
        
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
        """Used to load the data. Normally called by __init__."""
        if len(Detector.names) == 0:
            self._parse(os.path.join(os.path.dirname(__file__), Detector.default_fn))
    
    def reload(self):
        """May enable the data set to be reloaded with a new set of return values based on the class variables."""
        Detector.names = {}
        self.load()

    def get_gender(self, name, country=None, strict=False):
        """Returns best gender for the given name and country pair.
        
        The strict parameter set to True means that _only_ the specified
        country is considered when inferring gender. If false (the default)
        then _if_ no specific country value is found then the global
        distribution will be used. If true (the other option) then it
        will return _only_ the country value _even if_ that value is 0.

        Args:
            name (str): The name to search for.
            ctry (str): The name of the country. Defaults to None for a global search.
            strict (bool): Should search be confined to only the specified country. Defaults to False.

        Returns:
            str: The gender thought most likely to be associated with the name.
        """
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
