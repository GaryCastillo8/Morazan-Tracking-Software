from pypredict.calcOrbitParam import Calc
from pypredict.sat import Sat
from numpy import asscalar, cos, matrix, pi, sin, sqrt

class Dpl(object):
    __slots__ = ["calc", "Q_pi", "Q_po",
                 "Q_op", "v", "r"]
    def __init__(self):
        self.calc = Calc()

    def __call__(self):
        return self

    def perifocal2inertial(self, sat, v):
        sin_RAAN = sin(sat.RAAN)
        cos_RAAN = cos(sat.RAAN)
        sin_i = sin(sat.incl)
        cos_i = cos(sat.incl)
        sin_w = sin(sat.w)
        cos_w = cos(sat.w)
        self.Q_pi = matrix([[-sin_RAAN*cos_i*sin_w + cos_RAAN*cos_w,
                             -sin_RAAN*cos_i*cos_w - cos_RAAN*sin_w,
                             sin_RAAN*sin_i],
                            [cos_RAAN*cos_i*sin_w + sin_RAAN*cos_w,
                             cos_RAAN*cos_i*cos_w - sin_RAAN*sin_w,
                             -cos_RAAN*sin_i],
                            [sin_i*sin_w, sin_i*cos_w, cos_i]])
        return self.Q_pi*v

    def perifocal2orbital(self, theta, v):
        phi = theta + pi/2
        self.Q_po = matrix([[cos(phi), sin(phi), 0],
                            [0, 0, -1],
                            [-sin(phi), cos(phi), 0]])
        return self.Q_po*v

    def orbital2perifocal(self, theta, v):
        phi = theta + pi/2
        self.Q_op = matrix([[cos(phi), 0, -sin(phi)],
                            [sin(phi), 0, cos(phi)],
                            [0, -1, 0]])
        return self.Q_op*v

    def calcPosAndVel(self, deployer, vel):
        aux = deployer.getXYZ()
        self.r = [aux[0,0], aux[1,0], aux[2,0]]
        v_p, v_q = deployer.getPerifocalVel()
        v_peri = matrix([[v_p], [v_q], [0]])
        v_orb = self.perifocal2orbital(deployer.theta, v_peri)
        v_orb[0,0] = v_orb[0,0] + vel[0]
        v_orb[1,0] = v_orb[1,0] + vel[1]
        v_orb[2,0] = v_orb[2,0] + vel[2]
        v_peri = self.orbital2perifocal(deployer.theta, v_orb)
        v = self.perifocal2inertial(deployer, v_peri)
        self.v = [v[0,0], v[1,0], v[2,0]]

    def updateSat(self, sat, date):
        self.calc.newCalc(r1=self.r, v=self.v)
        sat.setInclination(self.calc.i)
        sat.setRAAN0(self.calc.RAAN)
        sat.setRAAN(self.calc.RAAN)
        sat.setArgPerigee0(self.calc.w)
        sat.setArgPerigee(self.calc.w)
        sat.setEccentricity(self.calc.e_scalar)
        sat.setMeanAnomaly0(self.calc.MA)
        sat.setMeanAnomaly(self.calc.MA)
        sat.setTrueAnomaly(self.calc.theta)
        sat.setSemiMajorAxis(self.calc.a)
        sat.setMeanMotion(self.calc.n)
        sat.setSemilatusRectum(self.calc.a*(1 - self.calc.e_scalar**2))
        sat.setSpecAngMomentum(sqrt(sat.a*sat.mu*(1 - self.calc.e_scalar**2)))
        sat.updateEpoch(date=date)

    def deploy(self, cat, dplyr, dplyr_mass, dplyd_mass, name, vel, date=None):
        """
        Simulates a deployment of a satellite from another. Calculates
        the orbital parameters of the new satellite (the deployed
        satellite) and updates the deployer satellite due to the
        change in momentum considering the mass.

        Parameters
        ----------
        cat        : str
                     The new satellite's category.
        dplyr      : pypredict.sat.Sat object
                     The satellite that is deploying the new satellite.
        dplyr_mass : float
                     The mass of the deployer.
        dplyd_mass : float
                     The mass of the deployed satellite.
        name       : str
                     The name of the deployed satellite.
        vel        : list
                     A list with the 3 components of the velocity
                     of deployment from the deployer's perspective.
        date       : datetime.datetime object, optional
                     Defaults to datetime.utcnow().

        Returns
        -------
        newsat     : pypredict.sat.Sat object
                     A satellite object with the properties of the
                     deployed satellite.
        """
        self.calcPosAndVel(dplyr, vel)
        dplyr_name, line1, line2 = dplyr.createTLE(date)
        newSat = Sat(name=name, line1=line1, line2=line2, cat=cat)
        self.updateSat(newSat, date)
        B = (2*(0.034*0.084 + 0.034*0.028 + 0.084*0.028))/6/dplyd_mass
        newSat.setBallisticCoeff(B)
        newSat.createTLE(date)
        dplyr_mass = dplyr_mass - dplyd_mass
        dplyr_vel = [-vel[0]*dplyd_mass/dplyr_mass,
                     -vel[1]*dplyd_mass/dplyr_mass,
                     -vel[2]*dplyd_mass/dplyr_mass]
        self.calcPosAndVel(dplyr, dplyr_vel)
        self.updateSat(dplyr, date)
        B = (0.1*0.1*2 + 4*0.3*0.1)/6/dplyr_mass
        dplyr.setBallisticCoeff(B)
        dplyr.createTLE(date)
        return newSat
