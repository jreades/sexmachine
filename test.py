import os
import gzip

names = {}

gmappings = {
    'M':  'M',
    '1M': 'MM',
    '?M': 'MM',
    'F':  'F',
    '1F': 'MF',
    '?F': 'MF',
    '?':  'U'
}

mappings = ((256, ["<A/>"]),
            (257, ["<a/>"]),
            (258, ["<Â>"]),
            (259, ["<â>"]),
            (260, ["<A,>"]),
            (261, ["<a,>"]),
            (262, ["<C´>"]),
            (263, ["<c´>"]),
            (268, ["<C^>", "<CH>"]),
            (269, ["<c^>", "<ch>"]),
            (271, ["<d´>"]),
            (272, ["<Ð>", "<DJ>"]),
            (273, ["<ð>", "<dj>"]),
            (274, ["<E/>"]),
            (275, ["<e/>"]),
            (278, ["<E°>"]),
            (279, ["<e°>"]),
            (280, ["<E,>"]),
            (281, ["<e,>"]),
            (282, ["<Ê>"]),
            (283, ["<ê>"]),
            (287, ["<g^>"]),
            (290, ["<G,>"]),
            (286, ["<G^>"]),
            (291, ["<g´>"]),
            (298, ["<I/>"]),
            (299, ["<i/>"]),
            (304, ["<I°>"]),
            (305, ["<i>"]),
            (306, ["<IJ>"]),
            (307, ["<ij>"]),
            (310, ["<K,>"]),
            (311, ["<k,>"]),
            (315, ["<L,>"]),
            (316, ["<l,>"]),
            (317, ["<L´>"]),
            (318, ["<l´>"]),
            (321, ["<L/>"]),
            (322, ["<l/>"]),
            (325, ["<N,>"]),
            (326, ["<n,>"]),
            (327, ["<N^>"]),
            (328, ["<n^>"]),
            (336, ["<Ö>"]),
            (337, ["<ö>"]),
            (338, ["<OE>"]),
            (339, ["<oe>"]),
            (344, ["<R^>"]),
            (345, ["<r^>"]),
            (350, ["<S,>"]),
            (351, ["<s,>"]),
            (352, ["<S^>", "<SCH>", "<SH>"]),
            (353, ["<s^>", "<sch>", "<sh>"]),
            (354, ["<T,>"]),
            (355, ["<t,>"]),
            (357, ["<t´>"]),
            (362, ["<U/>"]),
            (363, ["<u/>"]),
            (366, ["<U°>"]),
            (367, ["<u°>"]),
            (370, ["<U,>"]),
            (371, ["<u,>"]),
            (379, ["<Z°>"]),
            (380, ["<z°>"]),
            (381, ["<Z^>"]),
            (382, ["<z^>"]),
            (7838, ["<ß>"]),
            )

def map_name(u):
    for code, patterns in mappings:
        for pattern in patterns:
            u = u.replace(pattern, chr(code))
    return u

COUNTRIES = [ x.strip() for x in """Great Britain, Ireland, USA, Italy, Malta, Portugal, Spain, France, 
                   Belgium, Luxembourg, The Netherlands, East Frisia, Germany, Austria, 
                   Switzerland, Iceland, Denmark, Norway, Sweden, Finland, Estonia, Latvia, 
                   Lithuania, Poland, Czech Republic, Slovakia, Hungary, Romania, 
                   Bulgaria, Bosnia and Croatia, Kosovo, Macedonia, Montenegro, Serbia, 
                   Slovenia, Albania, Greece, Russia, Belarus, Moldova, Ukraine, Armenia, 
                   Azerbaijan, Georgia, The Stans, Turkey, Arabia, Israel, China, India, 
                   Japan, Korea, Vietnam, Other
                 """.split(",") ]

def _parse(filename):
    """Opens data file and for each line, calls _eat_name_line"""
    with gzip.open(filename, 'r') as f:
        for line in f:
            _eat_name_line(line.decode('iso8859-1').strip())

def _eat_name_line(line):
    """Parses one line of data file"""
    if line[0] not in "#=":
        gender = line[0:2].strip()
        name   = map_name(line[3:29].strip())
        freq   = line[30:-1].replace(" ","0")

        _set(name, gmappings[gender], freq)

def _set(name, gender, country_values):
    """Sets gender and relevant country values for names dictionary of detector"""
    if '+' in name:
        for replacement in ['', ' ', '-']:
            _set(name.replace('+', replacement), gender, country_values)
    else:
        if name not in names:
            names[name] = {}
        names[name][gender] = country_values

def dump_name(country_values):
    for key, val in country_values.items(): 
        print(key)
        for i in range(0, len(COUNTRIES)):
            if val[i] != '0': print("\t" + COUNTRIES[i] + " -> " + val[i] + " -> " + str(int(val[i],16)))

# def get_gender(name, country=None):
#         """Returns best gender for the given name and country pair"""
#         if name not in names:
#             return Null
#         elif not country:
#             def counter(country_values):
#                 print(",".join(country_values))
#                 country_values = country_values.replace(" ", "")
#                 #print(sum(list(map(lambda c: int(c) > 64 and int(c)-55 or int(c)-48, country_values))))
#                 return (len(list(country_values)),
#                         sum(list(map(lambda c: int(c) > 64 and int(c)-55 or int(c)-48, country_values))))
#             return self._most_popular_gender(name, counter)
#         elif country in self.__class__.COUNTRIES:
#             index = self.__class__.COUNTRIES.index(country)
#             print("Index: " + str(index))
#             counter = lambda e: (try_int(e[index])-32, 0)
#             return self._most_popular_gender(name, counter)
#         else:
#             raise NoCountryError("No such country: %s" % country)

_parse(os.path.join(os.path.dirname(__file__), "sexmachine/data/nam_dict.txt.gz"))

#print(names['Yun Cha'])
#print(names['Yun-Cha'])
#print(names['Maria'])
print(names['Jamie'])

#dump_name(names['Maria'])
#print(" ")

def name_freq(country_values):
    print(sum(list(map(lambda c: int(c,16), country_values))))

# print("Jamie")
# dump_name(names['Jamie'])

# print(len(list(names['Jamie']['MF'].replace(" ",""))))

# # sum(list(map(lambda c: int(c) > 64 and int(c)-55 or int(c)-48, country_values)))
# print(sum(list(map(lambda c: ord(c) > 64 and ord(c)-55 or ord(c)-48, list(names['Jamie']['MF'].replace(" ",""))))))

# print(sum(list(map(lambda c: ord(c) > 64 and ord(c)-55 or ord(c)-48, list(names['Jamie']['F'].replace(" ",""))))))

# print(sum(list(map(lambda c: ord(c) > 64 and ord(c)-55 or ord(c)-48, list(names['Jamie']['MM'].replace(" ",""))))))

print("Maria")
dump_name(names['Maria'])

print(sum(list(map(lambda c: ord(c) > 64 and ord(c)-55 or ord(c)-48, list(names['Maria']['MF'].replace(" ","0"))))))

name_freq(list(names['Maria']['F'].replace(" ","0")))

# Needs a tie-breaker option based on default values? Or a 'U' value
# for 'we don't know'? Something different from Androgyne? Guess this is 
# where the number of countries comes into it, though seems to me you
# also want to weight by country population! Maybe a most_common=T/F param
# based on whether you want it to guess a value or be specific to that 
# country?
def country_prob(lkp, ctry):
    #print(lkp)
    results = [] # Store the by-country results
    ix = COUNTRIES.index(ctry)
    for key, val in lkp.items():
        results.append( [key, int(val[ix],16)] )
    return min(results, key=lambda x: x[1])[0]

print(country_prob(names['Maria'],'Vietnam'))