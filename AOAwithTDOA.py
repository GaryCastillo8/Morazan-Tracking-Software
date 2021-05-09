from numpy import arange, arctan2, arccos, array, cos, matrix, mean, pi, random, savetxt, sin, std, sqrt, zeros, transpose
from pypredict.dpl import Dpl
from pypredict.sat import Sat
from pypredict.dpl import Dpl
from matplotlib.pyplot import axis, plot, setp, show, subplots, subplots_adjust, tight_layout, xticks
from datetime import datetime, timedelta
from pkg_resources import resource_filename

class Locate(object):
    def __init__(self):
        print("Initializing AOA with TDOA")

    def __call__(self):
        return self

    def get_distance(self, u, s):
        d = sqrt((u[0,0] - s[0,0])**2 + (u[1,0] - s[1,0])**2 + (u[2,0] - s[2,0])**2)
        return d

    def get_real_vector(self, u, s1, s2):
        d1 = self.get_distance(u, s1)
        d2 = self.get_distance(u, s2)
        d21 = d2 - d1
        theta1 = arctan2(u[1,0] - s1[1,0], u[0,0] - s1[0,0])
        phi1 = arctan2(u[2,0] - s1[2,0], sqrt((u[0,0] - s1[0,0])**2 + (u[1,0] - s1[1,0])**2))
        theta2 = arctan2(u[1,0] - s2[1,0], u[0,0] - s2[0,0])
        phi2 = arctan2(u[2,0] - s2[2,0], sqrt((u[0,0] - s2[0,0])**2 + (u[1,0] - s2[1,0])**2))
        return d21, theta1, phi1, theta2, phi2

    def get_b(self, theta, phi):
        return matrix([[cos(phi)*cos(theta)], [cos(phi)*sin(theta)], [sin(phi)]])

    def get_Gm(self, theta, phi):
        Gm = matrix([[sin(theta), sin(phi)*cos(theta)],
                     [-cos(theta), sin(phi)*sin(theta)],
                     [0, -cos(phi)]])
        return Gm

    def get_G(self, b1, b2, G1, G2):
        G = matrix([[2*(b2 - b1)[0,0], G1[0,0], G1[0,1], G2[0,0], G2[0,1]],
                    [2*(b2 - b1)[1,0], G1[1,0], G1[1,1], G2[1,0], G2[1,1]],
                    [2*(b2 - b1)[2,0], G1[2,0], G1[2,1], G2[2,0], G2[2,1]]])
        return G

    def get_h(self, d21, s1, s2, b1, b2, G1, G2):
        s1TG1 = s1.transpose()*G1
        s2TG2 = s2.transpose()*G2
        h = matrix([[((b2 - b1).transpose()*(s1 + s2 - d21*b1))[0,0]],
                    [s1TG1[0,0]], [s1TG1[0,1]], [s2TG2[0,0]], [s2TG2[0,1]]])
        return h

    def get_Lm(self, theta, phi):
        Lm = matrix([[-cos(phi)*sin(theta), -sin(phi)*cos(theta)],
                     [cos(phi)*cos(theta), -sin(phi)*sin(theta)],
                     [0, cos(phi)]])
        return Lm

    def get_Tm(self, d, phi):
        Tm = -d*matrix([[cos(phi), 0],
                        [0, 1]])
        return Tm

    def get_T(self, d1, d2, b1, b2, L1, L2, T1, T2):
        r1b2TL1 = d1*b2.transpose()*L1
        r2b1TL2 = d2*b1.transpose()*L2
        b2_m_b1_t = ((b2 - b1).transpose()*b1)[0,0]
        T = matrix([[-b2_m_b1_t, r1b2TL1[0,0], r1b2TL1[0,1], -r2b1TL2[0,0], -r2b1TL2[0,1]],
                    [0, T1[0,0], T1[0,1], 0, 0],
                    [0, T1[1,0], T1[1,1], 0, 0],
                    [0, 0, 0, T2[0,0], T2[0,1]],
                    [0, 0, 0, T2[1,0], T2[1,1]]])
        return T

    def get_Q(self, std_RD, std_AOA):
        Q = matrix([[std_RD**2, 0, 0, 0, 0],
                    [0, std_AOA**2, 0, 0, 0],
                    [0, 0, std_AOA**2, 0, 0],
                    [0, 0, 0, std_AOA**2, 0],
                    [0, 0, 0, 0, std_AOA**2]])
        return Q

    def get_W(self, Q, T):
        W = T*Q*T.transpose()
        return W

    def get_error_vector(self, std_RD, std_AOA, L):
        e = random.randn(5, L)
        e[0,:] = std_RD*(e[0,:] - mean(e[0,:]))
        e[1,:] = std_AOA*(e[1,:] - mean(e[1,:]))
        e[2,:] = std_AOA*(e[2,:] - mean(e[2,:]))
        e[3,:] = std_AOA*(e[3,:] - mean(e[3,:]))
        e[4,:] = std_AOA*(e[4,:] - mean(e[4,:]))
        return e

    def get_MSE(self, u, s1, s2, k, Q):
        b1 = self.get_b(k[1], k[2])
        b2 = self.get_b(k[3], k[4])
        G1 = self.get_Gm(k[1], k[2])
        G2 = self.get_Gm(k[3], k[4])
        G  = self.get_G(b1, b2, G1, G2)
        d1 = self.get_distance(u, s1)
        d2 = self.get_distance(u, s2)
        L1 = self.get_Lm(k[1], k[2])
        L2 = self.get_Lm(k[3], k[4])
        T1 = self.get_Tm(d1, k[2])
        T2 = self.get_Tm(d2, k[4])
        T = self.get_T(d1, d2, b1, b2, L1, L2, T1, T2)
        MSE = ((T.I*G.transpose()).transpose()*Q.I*T.I*G.transpose()).I
        return MSE

    def get_lm(self, u, sm):
        lm = sqrt((u[0,0] - sm[0,0])**2 + (u[1,0] - sm[1,0])**2)
        return lm

    def get_Dm(self, u, sm, lm, dm):
        aux = (u[2,0] - sm[2,0])/(dm**2*lm)
        Dm = matrix([[-(u[1,0] - sm[1,0])/lm**2, (u[0,0] -  sm[0,0])/lm**2, 0],
                     [-(u[0,0] - sm[0,0])*aux, -(u[1,0] - sm[1,0])*aux, lm/dm**2]])
        return Dm

    def get_FIM(self, u, s1, s2, Q):
        d1 = self.get_distance(u, s1)
        d2 = self.get_distance(u, s2)
        c = (u - s2)/d2 - (u - s1)/d1
        l1 = self.get_lm(u, s1)
        l2 = self.get_lm(u, s2)
        D1 = self.get_Dm(u, s1, l1, d1)
        D2 = self.get_Dm(u, s2, l2, d2)
        dk_duT = matrix([[c[0,0], c[1,0], c[2,0]],
                         [D1[0,0], D1[0,1], D1[0,2]],
                         [D1[1,0], D1[1,1], D1[1,2]],
                         [D2[0,0], D2[0,1], D2[0,2]],
                         [D2[1,0], D2[1,1], D2[1,2]]])
        FIM = dk_duT.transpose()*Q.I*dk_duT
        return FIM

    def estimate(self, s1, s2, k, e, Q):#, G):
        d21_hat = k[0] + e[0]
        theta1_hat = k[1] + e[1]
        phi1_hat = k[2] + e[2]
        theta2_hat = k[3] + e[3]
        phi2_hat = k[4] + e[4]
        b1_hat = self.get_b(theta1_hat, phi1_hat)
        b2_hat = self.get_b(theta2_hat, phi2_hat)
        G1_hat = self.get_Gm(theta1_hat, phi1_hat)
        G2_hat = self.get_Gm(theta2_hat, phi2_hat)
        G_hat  = self.get_G(b1_hat, b2_hat, G1_hat, G2_hat)
        h_hat = self.get_h(d21_hat, s1, s2, b1_hat, b2_hat, G1_hat, G2_hat)
        initial_estimate = (G_hat*G_hat.transpose()).I*G_hat*h_hat
        for i in range(2):
            d1 = self.get_distance(initial_estimate, s1)
            d2 = self.get_distance(initial_estimate, s2)
            L1 = self.get_Lm(theta1_hat, phi1_hat)
            L2 = self.get_Lm(theta2_hat, phi2_hat)
            T1 = self.get_Tm(d1, phi1_hat)
            T2 = self.get_Tm(d2, phi2_hat)
            T = self.get_T(d1, d2, b1_hat, b2_hat, L1, L2, T1, T2)
            W = self.get_W(Q, T)
            u_hat = (G_hat*W.I*G_hat.transpose()).I*G_hat*W.I*h_hat
            initial_estimate = u_hat
        #MSE = ((T.I*G.transpose()).transpose()*Q.I*T.I*G.transpose()).I
        return u_hat#, MSE

    def RMSE(self, u, estimations, L):
        aux = 0
        for est in estimations:
            aux += (est[0,0] - u[0,0])**2 + (est[1,0] - u[1,0])**2 + (est[2,0] - u[2,0])**2
        return aux/L
    
    def Bias(self, u, estimations, L):
        acum_u_hat = matrix([[0.0], [0.0], [0.0]])
        for est in estimations:
            acum_u_hat += est
        mean_u_hat = acum_u_hat/L
        bias = self.get_distance(mean_u_hat, u)
        return bias**2

    def get_GNSS_noise(self, std_GNSS, L):
        """
        Creates an L length vector of zero mean Gaussian noise.
        It considers the standard deviation of a GNSS device.
        """
        accuracy_by_axis = std_GNSS/sqrt(3)
        e = random.randn(6, L)
        e[0,:] = accuracy_by_axis*(e[0,:] - mean(e[0,:]))
        e[1,:] = accuracy_by_axis*(e[1,:] - mean(e[1,:]))
        e[2,:] = accuracy_by_axis*(e[2,:] - mean(e[2,:]))
        e[3,:] = accuracy_by_axis*(e[3,:] - mean(e[3,:]))
        e[4,:] = accuracy_by_axis*(e[4,:] - mean(e[4,:]))
        e[5,:] = accuracy_by_axis*(e[5,:] - mean(e[5,:]))
        return e

    def add_GNSS_error(self, s1, s2, e):
        """
        Adds noise to the reference positions s1 and s2 considering the accuracy of
        the GNSS device.
        """
        noisy_s1 = matrix([[0.0], [0.0], [0.0]])
        noisy_s2 = matrix([[0.0], [0.0], [0.0]])
        noisy_s1[0,0] = s1[0,0] + e[0]
        noisy_s1[1,0] = s1[1,0] + e[1]
        noisy_s1[2,0] = s1[2,0] + e[2]
        noisy_s2[0,0] = s2[0,0] + e[3]
        noisy_s2[1,0] = s2[1,0] + e[4]
        noisy_s2[2,0] = s2[2,0] + e[5]
        return noisy_s1, noisy_s2

    def get_deployment_noise(self, std_ADS, std_ACS, N):
        """
        Creates an N length vector of zero mean Gaussian noise.
        It considers the standard deviation of the attitude
        determination and control system of the CubeSat that
        deploys the femto-satellite.
        """
        deg2rad = pi/180
        e = random.randn(2, N)
        e[0,:] = sqrt(std_ADS**2 + std_ACS**2)*deg2rad*(e[0,:] - mean(e[0,:]))
        e[1,:] = sqrt(std_ADS**2 + std_ACS**2)*deg2rad*(e[1,:] - mean(e[1,:]))
        return e

    def noisy_dep_velocity(self, v, e):
        """
        Adds noise to the ideal deployment velocity to simulate the error of the attitude
        determination and control system of the CubeSat that deploys the femto-satellite.
        """
        yaw_noise = e[0]#e[0] + e[1]
        pitch_noise = e[1]#e[2] + e[3]
        yaw = arctan2(v[1], v[0]) + yaw_noise
        pitch = arctan2(v[2], sqrt(v[0]**2 + v[1]**2)) + pitch_noise
        radius = sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        new_vel = [radius*cos(yaw)*cos(pitch), radius*sin(yaw)*cos(pitch), radius*sin(pitch)]
        return new_vel

    def sat_simulation(self, sat_u, sat_s1, sat_s2, L, std_RD, std_AOA, std_GNSS, mins, date0):
        rmse = zeros(len(mins))
        bias = zeros(len(mins))
        Q = self.get_Q(std_RD, std_AOA)
        #date0 += timedelta(days=1)
        #date0 += timedelta(minutes=95)
        for i, m in enumerate(mins):
            estimations = []
            date = date0 + timedelta(minutes=m)
            sat_u.updateOrbitalParameters(date)
            sat_s1.updateOrbitalParameters(date)
            sat_s2.updateOrbitalParameters(date + timedelta(seconds=4))
            u = sat_u.getXYZ()
            s1 = sat_s1.getXYZ()
            s2 = sat_s2.getXYZ()
            e = self.get_error_vector(std_RD, std_AOA, L)
            GNSS_noise = self.get_GNSS_noise(std_GNSS, L)
            for j in range(L):
                noisy_s1, noisy_s2 = self.add_GNSS_error(s1, s2, GNSS_noise[:,j])
                k_w_GNSS_error = self.get_real_vector(u, noisy_s1, noisy_s2)
                u_hat = self.estimate(noisy_s1, noisy_s2, k_w_GNSS_error, e[:,j], Q)
                estimations.append(u_hat)
            rmse[i] = self.RMSE(u, estimations, L)
            bias[i] = self.Bias(u, estimations, L)
        return rmse, bias

    def sim_deployment(self, L, v, date):
        std_ADS = 20/3600 # STT of 20 arcseconds.
        std_ACS = 1       # RW of 1°.
        std_RD = 10.0
        std_AOA = 1.0*pi/180.0
        std_GNSS = 10.0
        dpl = Dpl()
        s1_mass = 3.2
        u_mass = 0.08
        minutes = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        rmse = zeros(len(minutes))
        bias = zeros(len(minutes))
        finer_minutes = arange(38, 199, dtype="float")*0.5 + 1.0
        rcrb = zeros(len(finer_minutes))
        dist_u_s1 = zeros(len(finer_minutes))
        data_path = resource_filename("pypredict","data/")
        sat_s2 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
        dep_noise = self.get_deployment_noise(std_ADS, std_ACS, 10)
        for i in range(10):
            sat_s1 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
            dep_date = date + timedelta(minutes=10*i)
            sat_s1.updateOrbitalParameters(dep_date)
            sat_s2.updateOrbitalParameters(dep_date)
            vel = self.noisy_dep_velocity(v, dep_noise[:,i])
            sat_u = dpl.deploy("Femto", sat_s1, s1_mass, u_mass, "FE1", vel, dep_date)
            r, b = self.sat_simulation(sat_u, sat_s1, sat_s2, L, std_RD, std_AOA, std_GNSS, minutes, dep_date)
            rmse += r
            bias += b
            r, d1, d2, al = self.simulation_RCRB(sat_u, sat_s1, sat_s2, finer_minutes, dep_date, std_RD, std_AOA)
            rcrb += r
            dist_u_s1 += d1
        rmse = sqrt(rmse/10.0)
        bias = sqrt(bias/10.0)
        rcrb = sqrt(rcrb/10.0)
        dist_u_s1 = dist_u_s1/10.0
        fig, ax = subplots(1, 1)#, sharex=True, sharey=True)
        ax.semilogy(finer_minutes, dist_u_s1, '-', linewidth=2.0, markersize=12,
                         label="Distance u-s1", color="tab:purple")
        ax.semilogy(minutes, rmse, 'o', linewidth=2.0, markersize=12, clip_on=False,
                         fillstyle="none", label="RMSE")
        ax.semilogy(finer_minutes, rcrb, '-', linewidth=2.0, markersize=12,
                         label="Root CRB")
        ax.semilogy(minutes, bias, '+', linewidth=2.0, markersize=12, clip_on=False,
                         label="Bias")
        ax.grid()
        ax.legend(fontsize=14, loc="upper center", bbox_to_anchor=(0.65,1.0))
        ax.set(xlabel="Time [min]", ylabel="RMSE and bias [m]",
               title="Deployment at [{:0.1f}, {:0.1f}, {:0.1f}] m/s".format(v[0], v[1], v[2]))
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=True)
        ax.set_xticks([20, 30, 40, 50, 60, 70, 80, 90, 100])
        axis((20, 100, 4*10**0, 2*10**4))
        tight_layout()

    def sim_deployment_in_1_geom(self, L, v, date):
        """
        Noisy deployments from the same point in orbit.
        """
        std_ADS = 36/3600 # STT of 36 arcseconds.
        std_ACS = 0.1     # RW of 0.1°.
        std_RD = 10.0
        std_AOA = 1.0*pi/180.0
        std_GNSS = 10.0
        dpl = Dpl()
        s1_mass = 3.2
        u_mass = 0.08
        L0 = 50
        minutes = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
        rmse = zeros(len(minutes))
        bias = zeros(len(minutes))
        div = 32
        finer_minutes = arange(0, div*100+1, dtype="float")/div
        rcrb = zeros(len(finer_minutes))
        dist_u_s1 = zeros(len(finer_minutes))
        dist_u_s2 = zeros(len(finer_minutes))
        alpha_max = zeros(len(finer_minutes))
        alpha_mean = zeros(len(finer_minutes))
        alpha_min = zeros(len(finer_minutes)) + 180
        data_path = resource_filename("pypredict","data/")
        sat_s2 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
        dep_noise = self.get_deployment_noise(std_ADS, std_ACS, L0)
        dep_date = date + timedelta(minutes=70)
        for i in range(L0):
            sat_s1 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
            sat_s1.updateOrbitalParameters(dep_date)
            sat_s2.updateOrbitalParameters(dep_date)
            vel = self.noisy_dep_velocity(v, dep_noise[:,i])
            sat_u = dpl.deploy("Femto", sat_s1, s1_mass, u_mass, "FE1", vel, dep_date)
            r, b = self.sat_simulation(sat_u, sat_s1, sat_s2, L, std_RD, std_AOA, std_GNSS, minutes, dep_date)
            rmse += r
            bias += b
            r, d1, d2, al = self.simulation_RCRB(sat_u, sat_s1, sat_s2, finer_minutes, dep_date, std_RD, std_AOA)
            rcrb += r
            dist_u_s1 += d1
            dist_u_s2 += d2
            alpha_mean += al
            if (max(al) > max(alpha_max)):
                alpha_max = al
            if (min(al) < min(alpha_min)):
                alpha_min = al
        rmse = sqrt(rmse/L0)
        bias = sqrt(bias/L0)
        rcrb = sqrt(rcrb/L0)
        dist_u_s1 = dist_u_s1/L0
        dist_u_s2 = dist_u_s2/L0*0.001
        alpha_mean = alpha_mean/L0
        #savetxt('rmse_bias.csv', transpose([rmse, bias]),
        #        delimiter=',', newline='\n', fmt='%.18e')
        #savetxt('rcrb_dist.csv', transpose([rcrb, dist_u_s1]),
        #        delimiter=',', newline='\n', fmt='%.18e')
        fig, ax = subplots(1, 1)#, sharex=True, sharey=True)
        ax.set_xlim(0, 100)
        ax.set_ylim(7, 8000)
        ax2 = ax.twinx()
        ax2.set_ylim(0, 180)
        ax.set_zorder(10)
        ax.patch.set_visible(False)
        ln5 = ax2.plot(finer_minutes, alpha_max, '-', linewidth=2.0, markersize=12,
                         label="{} (max)".format(r'$\alpha$'), color="k")
        ln6 = ax2.plot(finer_minutes, alpha_mean, '-', linewidth=2.0, markersize=12,
                label="{} (mean)".format(r'$\alpha$'), color="dimgrey")
        ln7 = ax2.plot(finer_minutes, alpha_min, '-', linewidth=2.0, markersize=12,
                         label="{} (min)".format(r'$\alpha$'), color="lightgrey")
        ln1 = ax.semilogy(minutes, rmse, 'o', linewidth=2.0, markersize=12,# clip_on=False,
                         fillstyle="none", label="RMSE")
        ln2 = ax.semilogy(finer_minutes, rcrb, '-', linewidth=2.0, markersize=12,
                         label="Root CRB", alpha=0.7)
        ln3 = ax.semilogy(minutes, bias, '+', linewidth=2.0, markersize=12,# clip_on=False,
                         label="Bias")
        ln4 = ax.semilogy(finer_minutes, dist_u_s1, '-', linewidth=2.0, markersize=12,
                         label=r'$||\mathbf{u} - \mathbf{s_1}||$', color="tab:purple", alpha=0.7)
        ln8 = ax.semilogy(finer_minutes, dist_u_s2, '-', linewidth=2.0, markersize=12,
                         label=r'$||\mathbf{u} - \mathbf{s_2}||$', color="tab:red")
        lines = ln1 + ln2 + ln3 + ln4 + ln5 + ln6 + ln7 + ln8
        labels = [l.get_label() for l in lines]
        ax.grid()
        ax.legend(lines, labels, fontsize=14, loc="upper center",
                  bbox_to_anchor=(0.48,1.0), ncol=2)
        #ax.legend(lines, labels, fontsize=12, loc="upper left", ncol=3)
        ax.set(xlabel="Time [min]", ylabel="RMSE, bias and {} [m]\n{} [km]".format(r'$||\mathbf{u} - \mathbf{s_1}||$', r'$||\mathbf{u} - \mathbf{s_2}||$'),
               title="Deployment at [{:0.1f}, {:0.1f}, {:0.1f}] m/s".format(v[0], v[1], v[2]))
        ax2.set_ylabel("{} [deg]".format(r'$\alpha$'))
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax2.yaxis.label.set_size(16)
        #ax.tick_params(which="both", direction="in", labelsize=14,
        #               bottom=True, top=True, left=True, right=True)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=False)
        ax2.tick_params(which="both", direction="in", labelsize=14,
                        bottom=False, top=False, left=False, right=True)
        #ax2.set_ylim(0, 180)
        ax.set_xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        #axis((0, 100, 7, 10**4))
        tight_layout()

    def simulation2(self, s1, s2, L, std_RD):
        rmse = zeros(len(std_RD))
        bias = zeros(len(std_RD))
        rcrb = zeros(len(std_RD))
        u = matrix([[1000.0], [1000.0], [1000.0]])
        k = self.get_real_vector(u, s1, s2)
        std_AOA = 0.5*pi/180.0
        for i, sigma in enumerate(std_RD):
            estimations = []
            Q = self.get_Q(sigma, std_AOA)
            MSE = self.get_MSE(u, s1, s2, k, Q)
            e = self.get_error_vector(sigma, std_AOA, L)
            for j in range(L):
                u_hat = self.estimate(s1, s2, k, e[:,j], Q)
                estimations.append(u_hat)
            rmse[i] = self.RMSE(u, estimations, L)
            bias[i] = self.Bias(u, estimations, L)
            rcrb[i] = MSE[0,0] + MSE[1,1] + MSE[2,2]
        return rmse, bias, rcrb

    def plot_fig2(self, L):
        """
        Figure 2 of A simple and accurate TDOA- AOA localization method using two stations.
        """
        rmse = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        bias = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        rcrb = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        std_RD = [10**0.5, 10, 10**1.5, 10**2, 10**2.5, 10**3]
        rmse = zeros(len(std_RD))
        bias = zeros(len(std_RD))
        rcrb = zeros(len(std_RD))
        radius = 300.0
        deg2rad = pi/180.0
        L0 = 10
        for i in range(L0):
            theta_s = random.uniform(-179, 179)*deg2rad
            phi_s = random.uniform(-89, 89)*deg2rad
            #s1 = radius*matrix([[cos(theta_s)*cos(phi_s)],
            #                   [sin(theta_s)*cos(phi_s)],
            #                   [sin(phi_s)]])
            s1 = radius*matrix([[cos(theta_s)], [sin(theta_s)], [0]])
            s2 = -s1
            rm, b, rc = self.simulation2(s1, s2, L, std_RD)
            rmse += rm
            bias += b
            rcrb += rc
        rmse = sqrt(rmse/L0)
        bias = sqrt(bias/L0)
        rcrb = sqrt(rcrb/L0)
        fig, ax = subplots(1, 1, sharey=False)
        ax.loglog(std_RD, rmse, 'o', linewidth=2.0, markersize=12, clip_on=False,
                  fillstyle="none", label="RMSE of the proposed method")
        ax.loglog(std_RD, rcrb, '-', linewidth=2.0, markersize=12,
                  label="Root CRB")
        ax.loglog(std_RD, bias, '+', linewidth=2.0, markersize=12, clip_on=False,
                  label="Bias of the proposed method")
        ax.grid()
        ax.legend(fontsize=14, loc="center right")
        ax.set(xlabel="{} [m]".format(r'$\sigma_{RD}$'), ylabel="RMSE and bias [m]")
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=True)
        axis((10**0.5, 10**3, 10**(-1), 10**2))
        tight_layout()

    def simulation3(self, s1, s2, L, std_AOA):
        rmse = zeros(len(std_AOA))
        bias = zeros(len(std_AOA))
        rcrb = zeros(len(std_AOA))
        u = matrix([[1000.0], [1000.0], [1000.0]])
        k = self.get_real_vector(u, s1, s2)
        std_RD = 10.0
        for i, sigma in enumerate(std_AOA):
            estimations = []
            Q = self.get_Q(std_RD, sigma)
            MSE = self.get_MSE(u, s1, s2, k, Q)
            e = self.get_error_vector(std_RD, sigma, L)
            for j in range(L):
                u_hat = self.estimate(s1, s2, k, e[:,j], Q)
                estimations.append(u_hat)
            rmse[i] = self.RMSE(u, estimations, L)
            bias[i] = self.Bias(u, estimations, L)
            rcrb[i] = MSE[0,0] + MSE[1,1] + MSE[2,2]
        return rmse, bias, rcrb

    def plot_fig3(self, L):
        """
        Figure 3 of A simple and accurate TDOA- AOA localization method using two stations.
        """
        std_AOA_deg = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]
        deg2rad = pi/180.0
        std_AOA = [i*deg2rad for i in std_AOA_deg]
        rmse = zeros(len(std_AOA))
        bias = zeros(len(std_AOA))
        rcrb = zeros(len(std_AOA))
        radius = 300.0
        L0 = 10
        for i in range(L0):
            theta_s = random.uniform(-179, 179)*deg2rad
            phi_s = random.uniform(-89, 89)*deg2rad
            #s1 = radius*matrix([[cos(theta_s)*cos(phi_s)],
            #                    [sin(theta_s)*cos(phi_s)],
            #                    [sin(phi_s)]])
            s1 = radius*matrix([[cos(theta_s)], [sin(theta_s)], [0]])
            s2 = -s1
            rm, b, rc = self.simulation3(s1, s2, L, std_AOA)
            rmse += rm
            bias += b
            rcrb += rc
        rmse = sqrt(rmse/L0)
        bias = sqrt(bias/L0)
        rcrb = sqrt(rcrb/L0)
        fig, ax = subplots(1, 1, sharey=False)
        ax.semilogy(std_AOA_deg, rmse, 'o', linewidth=2.0, markersize=12, clip_on=False,
              fillstyle="none", label="RMSE of the proposed method")
        ax.semilogy(std_AOA_deg, rcrb, '-', linewidth=2.0, markersize=12,
                  label="Root CRB")
        ax.semilogy(std_AOA_deg, bias, '+', linewidth=2.0, markersize=12, clip_on=False,
                  label="Bias of the proposed method")
        ax.grid()
        ax.legend(fontsize=14, loc="center right")
        ax.set(xlabel="{} [deg]".format(r'$\sigma_{AOA}$'), ylabel="RMSE and bias [m]")
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=True)
        axis((0.5, 2.5, 10**(-1), 10**3))
        xticks([0.5, 1, 1.5, 2, 2.5])
        tight_layout()

    def simulation4(self, s1, s2, L, ratio):
        rmse = zeros(len(ratio))
        bias = zeros(len(ratio))
        rcrb = zeros(len(ratio))
        std_RD = 10.0
        std_AOA = 1.0*pi/180.0
        Q = self.get_Q(std_RD, std_AOA)
        base_u = sqrt(3)*matrix([[100.0], [100.0], [100.0]])
        for i, a in enumerate(ratio):
            estimations = []
            u = a*base_u
            k = self.get_real_vector(u, s1, s2)
            MSE = self.get_MSE(u, s1, s2, k, Q)
            e = self.get_error_vector(std_RD, std_AOA, L)
            for j in range(L):
                u_hat = self.estimate(s1, s2, k, e[:,j], Q)
                estimations.append(u_hat)
            rmse[i] = self.RMSE(u, estimations, L)
            bias[i] = self.Bias(u, estimations, L)
            rcrb[i] = MSE[0,0] + MSE[1,1] + MSE[2,2]
        return rmse, bias, rcrb

    def plot_fig4(self, L):
        """
        Figure 4 of A simple and accurate TDOA- AOA localization method using two stations.
        """
        ratio = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        rmse = zeros(len(ratio))
        bias = zeros(len(ratio))
        rcrb = zeros(len(ratio))
        radius = 300.0
        deg2rad = pi/180.0
        L0 = 10
        for i in range(L0):
            theta_s = random.uniform(-179, 179)*deg2rad
            phi_s = random.uniform(-89, 89)*deg2rad
            #s1 = radius*matrix([[cos(theta_s)*cos(phi_s)],
            #                    [sin(theta_s)*cos(phi_s)],
            #                    [sin(phi_s)]])
            s1 = radius*matrix([[cos(theta_s)], [sin(theta_s)], [0]])
            s2 = -s1
            rm, b, rc = self.simulation4(s1, s2, L, ratio)
            rmse += rm
            bias += b
            rcrb += rc
        rmse = sqrt(rmse/L0)
        bias = sqrt(bias/L0)
        rcrb = sqrt(rcrb/L0)
        fig, ax = subplots(1, 1, sharey=False)
        ax.semilogy(ratio, rmse, 'o', linewidth=2.0, markersize=12, clip_on=False,
                  fillstyle="none", label="RMSE of the proposed method")
        ax.semilogy(ratio, rcrb, '-', linewidth=2.0, markersize=12,
                  label="Root CRB")
        ax.semilogy(ratio, bias, '+', linewidth=2.0, markersize=12, clip_on=False,
                  label="Bias of the proposed method")
        ax.grid()
        ax.legend(fontsize=14, loc="center right")
        ax.set(xlabel="Source-to-station-range ratio a", ylabel="RMSE and bias [m]")
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=True)
        axis((2, 10, 10**(-1.2), 10**3))
        xticks([2, 4, 6, 8, 10])
        tight_layout()

    def simulation_GNSS(self, sat_u, sat_s1, sat_s2, L, std_GNSS, date0):
        """
        Varies the accuracy of the GNSS device used by the CubeSats.
        """
        rmse = zeros(len(std_GNSS))
        bias = zeros(len(std_GNSS))
        rcrb = zeros(len(std_GNSS))
        std_RD = 10.0
        std_AOA = 1.0*pi/180.0
        Q = self.get_Q(std_RD, std_AOA)
        date = date0 + timedelta(minutes=100)
        sat_u.updateOrbitalParameters(date)
        sat_s1.updateOrbitalParameters(date)
        sat_s2.updateOrbitalParameters(date + timedelta(seconds=4))
        u = sat_u.getXYZ()
        s1 = sat_s1.getXYZ()
        s2 = sat_s2.getXYZ()
        k = self.get_real_vector(u, s1, s2)
        MSE = self.get_MSE(u, s1, s2, k, Q)
        for i, std in enumerate(std_GNSS):
            estimations = []
            e = self.get_error_vector(std_RD, std_AOA, L)
            GNSS_noise = self.get_GNSS_noise(std, L)
            for j in range(L):
                noisy_s1, noisy_s2 = self.add_GNSS_error(s1, s2, GNSS_noise[:,j])
                k_w_GNSS_error = self.get_real_vector(u, noisy_s1, noisy_s2)
                u_hat = self.estimate(noisy_s1, noisy_s2, k_w_GNSS_error, e[:,j], Q)
                estimations.append(u_hat)
            rmse[i] = self.RMSE(u, estimations, L)
            bias[i] = self.Bias(u, estimations, L)
            rcrb[i] = MSE[0,0] + MSE[1,1] + MSE[2,2]
        return rmse, bias, rcrb

    def plot_fig_GNSS(self, L, v, date0):
        """
        Varies the accuracy of the GNSS device used by the CubeSats.
        """
        std_GNSS = 10**(arange(11)*0.125 + 1.0)
        std_ADS = 36/3600 # STT with 36 arcseconds of accuracy.
        std_ACS = 0.1     # RWs of 0.1° of accuracy.
        rmse = zeros(len(std_GNSS))
        bias = zeros(len(std_GNSS))
        rcrb = zeros(len(std_GNSS))
        dpl = Dpl()
        s1_mass = 3.2
        u_mass = 0.08
        L0 = 50
        data_path = resource_filename("pypredict","data/")
        sat_s2 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
        dep_noise = self.get_deployment_noise(std_ADS, std_ACS, L0)
        for i in range(L0):
            sat_s1 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
            sat_s1.updateOrbitalParameters(date0)
            sat_s2.updateOrbitalParameters(date0)
            vel = self.noisy_dep_velocity(v, dep_noise[:,i]) # STT of 20 arcseconds. RW of 1°.
            sat_u = dpl.deploy("Femto", sat_s1, s1_mass, u_mass, "FE1", vel, date0)
            rm, b, rc = self.simulation_GNSS(sat_u, sat_s1, sat_s2, L, std_GNSS, date0)
            rmse += rm
            bias += b
            rcrb += rc
        rmse = sqrt(rmse/L0)
        bias = sqrt(bias/L0)
        rcrb = sqrt(rcrb/L0)
        fig, ax = subplots(1, 1)
        ax.loglog(std_GNSS, rmse, 'o', linewidth=2.0, markersize=12,
                  clip_on=False, fillstyle="none", label="RMSE")
        ax.loglog(std_GNSS, rcrb, '-', linewidth=2.0, markersize=12,
                  label="Root CRB")
        ax.loglog(std_GNSS, bias, '+', linewidth=2.0, markersize=12,
                  clip_on=False, label="Bias")
        ax.grid()
        ax.legend(fontsize=14, loc="upper left")
        ax.set(xlabel="{} [m]".format(r'$\sigma_{GNSS}$'), ylabel="RMSE and bias [m]",
               title="100 minutes after deployment at [{:0.1f}, {:0.1f}, {:0.1f}] m/s".format(v[0], v[1], v[2]))
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=True)
        axis((10, 10**2.25, 10**1, 10**2))
        tight_layout()

    def simulation_ADCS(self, L, v, std_ADS, std_ACS, date_dep):
        """
        Studies the effect of the error of the ADCS system in the femto-satellite's
        deployment.
        """
        rcrb = zeros(len(std_ADS))
        MSE_acumulator = zeros(L)
        std_RD = 10.0
        std_AOA = 1.0*pi/180.0
        dpl = Dpl()
        s1_mass = 3.2
        u_mass = 0.08
        data_path = resource_filename("pypredict","data/")
        sat_s2 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
        Q = self.get_Q(std_RD, std_AOA)
        date = date_dep + timedelta(minutes=100)
        sat_s2.updateOrbitalParameters(date + timedelta(seconds=4))
        s2 = sat_s2.getXYZ()
        for i, std in enumerate(std_ADS):
            dep_noise = self.get_deployment_noise(std, std_ACS, L)
            for j in range(L):
                sat_s1 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
                sat_s1.updateOrbitalParameters(date_dep)
                vel = self.noisy_dep_velocity(v, dep_noise[:,j])
                sat_u = dpl.deploy("Femto", sat_s1, s1_mass, u_mass, "FE1", vel, date_dep)
                sat_u.updateOrbitalParameters(date)
                sat_s1.updateOrbitalParameters(date)
                u = sat_u.getXYZ()
                s1 = sat_s1.getXYZ()
                k = self.get_real_vector(u, s1, s2)
                MSE = self.get_MSE(u, s1, s2, k, Q)
                MSE_acumulator[j] = MSE[0,0] + MSE[1,1] + MSE[2,2]
            rcrb[i] = sum(MSE_acumulator)/L
        return rcrb

    def plot_fig_ADCS(self, L, v, date0):
        """
        Studies the effect of the error of the ADCS system in the femto-satellite's
        deployment.
        """
        std_ADS = 10**(arange(33)*0.0625 - 2.0)
        std_ACS = [0.01, 0.10, 0.20, 0.30, 0.40]
        dep_date = date0 + timedelta(minutes=70)
        rcrb1 = self.simulation_ADCS(L, v, std_ADS, std_ACS[0], dep_date)
        rcrb1 = sqrt(rcrb1)
        rcrb2 = self.simulation_ADCS(L, v, std_ADS, std_ACS[1], dep_date)
        rcrb2 = sqrt(rcrb2)
        rcrb3 = self.simulation_ADCS(L, v, std_ADS, std_ACS[2], dep_date)
        rcrb3 = sqrt(rcrb3)
        rcrb4 = self.simulation_ADCS(L, v, std_ADS, std_ACS[3], dep_date)
        rcrb4 = sqrt(rcrb4)
        rcrb5 = self.simulation_ADCS(L, v, std_ADS, std_ACS[4], dep_date)
        rcrb5 = sqrt(rcrb5)
        fig, ax = subplots(1, 1)
        ax.loglog(std_ADS, rcrb1, '-', linewidth=2.0, markersize=12,
                  label="{} = {:0.2f}°".format(r'$\sigma_{ACS}$', std_ACS[0]))
        ax.loglog(std_ADS, rcrb2, '-', linewidth=2.0, markersize=12,
                  label="{} = {:0.2f}°".format(r'$\sigma_{ACS}$', std_ACS[1]))
        ax.loglog(std_ADS, rcrb3, '-', linewidth=2.0, markersize=12,
                  label="{} = {:0.2f}°".format(r'$\sigma_{ACS}$', std_ACS[2]))
        ax.loglog(std_ADS, rcrb4, '-', linewidth=2.0, markersize=12,
                  label="{} = {:0.2f}°".format(r'$\sigma_{ACS}$', std_ACS[3]))
        ax.loglog(std_ADS, rcrb5, '-', linewidth=2.0, markersize=12,
                  label="{} = {:0.2f}°".format(r'$\sigma_{ACS}$', std_ACS[4]))
        ax.grid()
        ax.legend(fontsize=15, loc="upper left", ncol=2)
        ax.set(xlabel="{} [deg]".format(r'$\sigma_{ADS}$'), ylabel="Root CRB [m]",
               title="100 minutes after deployment at [{}, {}, {}] m/s".format(v[0], v[1], v[2]))
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=True)
        axis((10**-2.0, 10**0, 10**1, 5*10**1))
        tight_layout()

    def plot_fig_RCRB(self, date0):
        """
        Studies the effect of the deployment direction.
        """
        velocities = [[ 1.0,  0.0,  0.0],
                      [-1.0,  0.0,  0.0],
                      [ 0.0,  1.0,  0.0],
                      [ 0.0, -1.0,  0.0],
                      [ 0.0,  0.0,  1.0],
                      [ 0.0,  0.0, -1.0]]
        div = 32
        N = div*100 + 1
        minutes = arange(N, dtype="float")/div
        len_minutes = len(minutes)
        rcrb = zeros(len_minutes)
        all_rcrb = []
        std_RD = 10.0
        std_AOA = 1.0*pi/180.0
        dpl = Dpl()
        s1_mass = 3.2
        u_mass = 0.08
        data_path = resource_filename("pypredict","data/")
        sat_s2 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
        for vel in velocities:
            for i in range(10):
                sat_s1 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
                dep_date = date0 + timedelta(minutes=10*i)
                sat_s1.updateOrbitalParameters(dep_date)
                sat_s2.updateOrbitalParameters(dep_date)
                sat_u = dpl.deploy("Femto", sat_s1, s1_mass, u_mass, "FE1", vel, dep_date)
                r, d1, d2, al = self.simulation_RCRB(sat_u, sat_s1, sat_s2, minutes, dep_date, std_RD, std_AOA)
                rcrb += r
            all_rcrb.append(sqrt(rcrb/10.0))
            rcrb = rcrb*0.0

        fig, ax = subplots(1, 1)
        ax.semilogy(minutes, all_rcrb[0], '-', linewidth=1.8, markersize=12,
                    label="+x")
        ax.semilogy(minutes, all_rcrb[1], '-', linewidth=1.8, markersize=12,
                    label="-x")
        ax.semilogy(minutes, all_rcrb[2], '-', linewidth=1.8, markersize=12,
                    label="+y")
        ax.semilogy(minutes, all_rcrb[3], '-', linewidth=1.8, markersize=12,
                    label="-y")
        ax.semilogy(minutes, all_rcrb[4], '-', linewidth=1.8, markersize=12,
                    label="+z")
        ax.semilogy(minutes, all_rcrb[5], '-', linewidth=1.8, markersize=12,
                    label="-z")
        ax.grid()
        ax.legend(fontsize=14, loc="upper left", ncol=3)
        ax.set(xlabel="Time [min]", ylabel="Root CRB [m]",
               title="Root CRB for different deployment directions at 1 [m/s]")
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=True)
        axis((0, 100, 4, 3*10**6))
        tight_layout()

    def simulation_RCRB(self, sat_u, sat_s1, sat_s2, minutes, dep_date, std_RD, std_AOA):
        """
        Studies the effect of the deployment direction.
        """
        Q = self.get_Q(std_RD, std_AOA)
        rcrb = zeros(len(minutes))
        dist_u_s1 = zeros(len(minutes))
        dist_u_s2 = zeros(len(minutes))
        dist_s1_s2 = zeros(len(minutes))
        for j, m in enumerate(minutes):
            date = dep_date + timedelta(minutes=m)
            sat_u.updateOrbitalParameters(date)
            sat_s1.updateOrbitalParameters(date)
            sat_s2.updateOrbitalParameters(date + timedelta(seconds=4))
            u = sat_u.getXYZ()
            s1 = sat_s1.getXYZ()
            s2 = sat_s2.getXYZ()
            k = self.get_real_vector(u, s1, s2)
            MSE = self.get_MSE(u, s1, s2, k, Q)
            rcrb[j] = MSE[0,0] + MSE[1,1] + MSE[2,2]
            dist_u_s1[j] = self.get_distance(u, s1)
            dist_u_s2[j] = self.get_distance(u, s2)
            dist_s1_s2[j] = self.get_distance(s1, s2)
        alpha = arccos(-(dist_s1_s2**2 - dist_u_s1**2 - dist_u_s2**2)/(2*dist_u_s1*dist_u_s2))
        alpha = 180/pi*alpha
        return rcrb, dist_u_s1, dist_u_s2, alpha

    def simulation_multiple_points(self, vel, date0, minutes):
        all_rcrb = []
        std_RD = 10.0
        std_AOA = 1.0*pi/180.0
        dpl = Dpl()
        s1_mass = 3.2
        u_mass = 0.08
        data_path = resource_filename("pypredict","data/")
        sat_s2 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
        #sat_s2 = Sat(name="MOLNIYA 1-32", tlepath="{}molniya.txt".format(data_path), cat="Molniya")
        for i in range(10):
            sat_s1 = Sat(name="FLOCK 4P-1", tlepath="{}planet.txt".format(data_path), cat="Planet Labs")
            #sat_s1 = Sat(name="MOLNIYA 1-32", tlepath="{}molniya.txt".format(data_path), cat="Molniya")
            dep_date = date0 + timedelta(minutes=10*i)
            sat_s1.updateOrbitalParameters(dep_date)
            sat_s2.updateOrbitalParameters(dep_date)
            sat_u = dpl.deploy("Femto", sat_s1, s1_mass, u_mass, "FE1", vel, dep_date)
            rcrb, d1, d2, al = self.simulation_RCRB(sat_u, sat_s1, sat_s2, minutes, dep_date, std_RD, std_AOA)
            all_rcrb.append(sqrt(rcrb))
        return all_rcrb

    def plot_fig_point_in_orbit(self, vel, date0):
        """
        Studies the effect of the point of the orbit where the deployment is made
        for one particular direction.
        """
        div = 32
        N = div*100 + 1
        minutes = arange(N, dtype="float")/div
        all_rcrb = self.simulation_multiple_points(vel, date0, minutes)

        fig, ax = subplots(1, 1)
        ax.semilogy(minutes, all_rcrb[8], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 80 min")
        ax.semilogy(minutes, all_rcrb[3], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 30 min")
        ax.semilogy(minutes, all_rcrb[9], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 90 min")
        ax.semilogy(minutes, all_rcrb[6], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 60 min")
        ax.semilogy(minutes, all_rcrb[0], '-', linewidth=1.8, markersize=12,
                    label="Apogee")
        ax.semilogy(minutes, all_rcrb[1], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 10 min")
        ax.semilogy(minutes, all_rcrb[4], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 40 min")
        ax.semilogy(minutes, all_rcrb[5], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 50 min")
        ax.semilogy(minutes, all_rcrb[2], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 20 min")
        ax.semilogy(minutes, all_rcrb[7], '-', linewidth=1.8, markersize=12,
                    label="Apogee + 70 min")
        ax.grid()
        handles,labels = ax.get_legend_handles_labels()
        handles = [handles[4], handles[5], handles[8], handles[1], handles[6],
                   handles[7], handles[3], handles[9], handles[0], handles[2]]
        labels = [labels[4], labels[5], labels[8], labels[1], labels[6],
                  labels[7], labels[3], labels[9], labels[0], labels[2]]
        ax.legend(handles,labels, fontsize=13, loc="upper left", bbox_to_anchor=(0.015,1.0), ncol=2)
        ax.set(xlabel="Time [min]", ylabel="Root CRB [m]",
               title="Root CRB of the deployment in different points of the orbit")
        ax.xaxis.label.set_size(16)
        ax.yaxis.label.set_size(16)
        ax.tick_params(which="both", direction="in", labelsize=14,
                       bottom=True, top=True, left=True, right=True)
        axis((0, 100, 4.5, 4*10**3))
        tight_layout()


if __name__ == "__main__":
    print("Start: {}".format(datetime.utcnow()))
    L = 5000
    locate = Locate()
    #locate.plot_fig_sat_sim(L)
    #print("Done first plot")
    #locate.plot_fig2(L)
    #print("Done second plot")
    #locate.plot_fig3(L)
    #print("Done third plot")
    #locate.plot_fig4(L)
    #print("Done fourth plot")

    date0 = datetime(2020, 11, 17, 00, 13, 33, 0) # True anomaly = 0
    v = [0, 1, 0]
    locate.plot_fig_RCRB(date0)
    #locate.plot_fig_point_in_orbit(v, date0)
    #locate.plot_fig_ADCS(L, v, date0)
    #locate.plot_fig_GNSS(L, v, date0)
    #locate.sim_deployment_in_1_geom(L, v, date0)

    print("Finish: {}".format(datetime.utcnow()))
    show()
