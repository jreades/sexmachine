=========== 
Sex Machine
===========

This package uses the underlying name frequency data from the program "gender" by Jorg Michael (described `here <http://www.autohotkey.com/community/viewtopic.php?t=22000>`_), and has been adapted from the original `Sex Machine <https://pypi.org/project/SexMachine/>`_ codebase to work with Python 3. Its use remains pretty straightforward::

    >>> import sexmachine.detector as gender
    >>> d = gender.Detector()
    >>> d.get_gender("Bob")
    'M'
    >>> d.get_gender("Sally")
    'F'
    >>> d.get_gender("Pauley") # should be androgynous
    'A'
    >>> d.get_gender("Tracey") # usually/mostly female
    'MF'

The result will be one of ``A`` (Androgynous), ``M`` (Male), ``F`` (Female), ``MM`` (Mostly Male), ``MF`` (Mostly Female) or ``U`` (Unknown). These values can be set to whatever you want using class-level variables as long as you do so before creating an actual detector::
    
    >>> import sexmachine.detector as g
    >>> gender.Detector.male  = 'Male'
    >>> gender.Detector.mmale = 'Male'
    >>> d = gender.Detector()
    >>> d.get_gender("Jon")
    'Male'

I18N is fully supported::

    >>> d.get_gender("Álfrún")
    'F'

Additionally, you can give preference to specific countries::

    >>> d.get_gender("Jamie")
    'MF'
    >>> d.get_gender("Jamie", 'Great Britain') # or 'great_britain' for backwards compatibility
    'MM'

Unlike the original SexMachine library this version uses a shared read-only dictionary so there is no particular penalty for creating multiple instances. Of course, if you want to change anything on the fly (e.g. a default return value) then you hae a very big problem.

As well, in the interests of keeping the package distribution as small as possible, the name_dict.txt file has been gzipped with concommitant changes to the code and reuqirements.

You can also now check the version::

    >>> import sexmachine
    >>> sexmachine.__version__
    '0.1.3'

Licenses
========

The generator code is distributed under the GPLv3.  The data file nam_dict.txt is released under the GNU Free Documentation License.
