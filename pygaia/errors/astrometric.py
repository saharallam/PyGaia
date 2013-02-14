__all__ = ['parallaxErrorSkyAvg', 'parallaxErrorSkyAvgAltStartGate', 'positionErrorSkyAvg',
           'properMotionErrorSkyAvg', 'parallaxError', 'positionError', 'properMotionError']

from numpy import sqrt, sin, array, floor
from utils import calcZ, calcZAltStartGate
from numpy import genfromtxt
from pkg_resources import resource_stream

_table = resource_stream('pygaia', 'data/errorFactorVariationBetaIncludingNumberOfTransits.txt')
_astrometricErrorFactors = genfromtxt(_table,
    skip_header=4, skip_footer=1,
    names=['sinBeta','alphaStar','delta','parallax','muAlphaStar','muDelta'])
_numStepsSinBeta = len(_astrometricErrorFactors['sinBeta'])

# Scaling factors for sky averaged position and proper motion errors. The errors are scaled with respect
# to the parallax error values. Note that the error are quoted in true arc terms (using phi*) for the
# longitude like component.
_scalingForPositions = {'Total':0.743, 'AlphaStar':0.787, 'Delta':0.699}
_scalingForProperMotions = {'Total':0.526, 'AlphaStar':0.556, 'Delta':0.496}

def errorScalingFactor(observable, beta):
  """
  Look up the numerical factors to apply to the sky averaged parallax error in order to obtain error
  values taking the Ecliptic latitude and the number of transits into account.

  Parameters
  ----------

  observable - Name of astrometric observable (one of: alphaStar, delta, parallax, muAlphaStar, muDelta)
  beta       - Values(s) of the Ecliptic latitude.

  Returns
  -------

  Numerical factors to apply to the errors of the given observable.
  """
  indices = array(floor(abs(sin(beta))*_numStepsSinBeta), dtype=int)
  indices[(indices==_numStepsSinBeta)] = _numStepsSinBeta-1
  return _astrometricErrorFactors[observable][indices]

def parallaxErrorSkyAvg(G, vmini):
  """
  Calculate the sky averaged parallax error from G and (V-I).

  Parameters
  ----------

  G     - Value(s) of G-band magnitude.
  vmini - Value(s) of (V-I) colour.

  Returns
  -------

  The parallax error in micro-arcseconds.
  """
  z=calcZ(G)
  return sqrt(9.3 + 658.1*z + 4.568*z*z)*(0.986 + (1.0 - 0.986)*vmini)

def parallaxError(G, vmini, beta):
  """
  Calculate the parallax error from G and (V-I) and the Ecliptic latitude beta of the source. The
  parallax error is calculated by applying numerical factors to the sky average error. These factors
  depend on beta and the average number of transits across a source for that value of beta.

  The code implements table 6 from the Gaia science performance pages:
  http://www.rssd.esa.int/SA/GAIA/docs/SciencePerformance/table6.htm

  Parameters
  ----------

  G     - Value(s) of G-band magnitude.
  vmini - Value(s) of (V-I) colour.
  beta  - Value(s) of the Ecliptic latitude.

  Returns
  -------

  The parallax error in micro-arcseconds.
  """
  return parallaxErrorSkyAvg(G, vmini)*errorScalingFactor('parallax',beta)


def parallaxErrorSkyAvgAltStartGate(G, vmini):
  """
  Calculate the sky averaged parallax error from G and (V-I). In this case assume gating starts at G=13.3
  (to simulate bright star worst performance)

  Parameters
  ----------

  G     - Value(s) of G-band magnitude.
  vmini - Value(s) of (V-I) colour.

  Returns
  -------

  The parallax error in micro-arcseconds.
  """
  z=calcZAltStartGate(G)
  return sqrt(9.3 + 658.1*z + 4.568*z*z)*(0.986 + (1.0 - 0.986)*vmini)

def positionErrorSkyAvg(G, vmini):
  """
  Calculate the sky averaged position errors from G and (V-I).

  NOTE! THE ERRORS ARE FOR SKY POSITIONS IN THE ICRS (I.E., RIGHT ASCENSION, DECLINATION). MAKE SURE YOUR
  SIMULATED ASTROMETRY IS ALSO ON THE ICRS.

  Parameters
  ----------

  G     - Value(s) of G-band magnitude.
  vmini - Value(s) of (V-I) colour.

  Returns
  -------

  The error in alpha* and the error in delta, in that order, in micro-arcsecond.
  """
  parallaxError = parallaxErrorSkyAvg(G, vmini)
  return _scalingForPositions['AlphaStar']*parallaxError, \
         _scalingForPositions['Delta']*parallaxError

def positionError(G, vmini, beta):
  """
  Calculate the position errors from G and (V-I) and the Ecliptic latitude beta of the source.

  NOTE! THE ERRORS ARE FOR SKY POSITIONS IN THE ICRS (I.E., RIGHT ASCENSION, DECLINATION). MAKE SURE YOUR
  SIMULATED ASTROMETRY IS ALSO ON THE ICRS.

  Parameters
  ----------

  G     - Value(s) of G-band magnitude.
  vmini - Value(s) of (V-I) colour.
  beta  - Value(s) of the Ecliptic latitude.

  Returns
  -------

  The error in alpha* and the error in delta, in that order, in micro-arcsecond.
  """
  parallaxError = parallaxErrorSkyAvg(G, vmini)
  return errorScalingFactor('alphaStar',beta)*parallaxError, \
         errorScalingFactor('delta',beta)*parallaxError

def properMotionErrorSkyAvg(G, vmini):
  """
  Calculate the sky averaged proper motion errors from G and (V-I).

  NOTE! THE ERRORS ARE FOR PROPER MOTIONS IN THE ICRS (I.E., RIGHT ASCENSION, DECLINATION). MAKE SURE
  YOUR SIMULATED ASTROMETRY IS ALSO ON THE ICRS.

  Parameters
  ----------

  G     - Value(s) of G-band magnitude.
  vmini - Value(s) of (V-I) colour.

  Returns
  -------

  The error in mu_alpha* and the error in mu_delta, in that order, in micro-arcsecond/year.
  """
  parallaxError = parallaxErrorSkyAvg(G, vmini)
  return _scalingForProperMotions['AlphaStar']*parallaxError, \
         _scalingForProperMotions['Delta']*parallaxError

def properMotionError(G, vmini, beta):
  """
  Calculate the proper motion errors from G and (V-I) and the Ecliptic latitude beta of the source.

  NOTE! THE ERRORS ARE FOR PROPER MOTIONS IN THE ICRS (I.E., RIGHT ASCENSION, DECLINATION). MAKE SURE
  YOUR SIMULATED ASTROMETRY IS ALSO ON THE ICRS.

  Parameters
  ----------

  G     - Value(s) of G-band magnitude.
  vmini - Value(s) of (V-I) colour.
  beta  - Value(s) of the Ecliptic latitude.

  Returns
  -------

  The error in mu_alpha* and the error in mu_delta, in that order, in micro-arcsecond/year.
  """
  parallaxError = parallaxErrorSkyAvg(G, vmini)
  return errorScalingFactor('muAlphaStar',beta)*parallaxError, \
         errorScalingFactor('muDelta',beta)*parallaxError