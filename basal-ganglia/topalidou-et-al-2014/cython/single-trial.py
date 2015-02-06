# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License.
#
# Contributors: Nicolas P. Rougier (Nicolas.Rougier@inria.fr)
# -----------------------------------------------------------------------------
# References:
#
# * Interaction between cognitive and motor cortico-basal ganglia loops during
#   decision making: a computational study. M. Guthrie, A. Leblois, A. Garenne,
#   and T. Boraud. Journal of Neurophysiology, 109:3025–3040, 2013.
# -----------------------------------------------------------------------------
import numpy as np
from cdana import *

tau     = 0.01
clamp   = Clamp(min=0, max=1000)
sigmoid = Sigmoid(Vmin=0, Vmax=20, Vh=16, Vc=3)

CTX = AssociativeStructure(
                 tau=tau, rest=- 3.0, noise=0.010, activation=clamp )
STR = AssociativeStructure(
                 tau=tau, rest=  0.0, noise=0.001, activation=sigmoid )
STN = Structure( tau=tau, rest=-10.0, noise=0.001, activation=clamp )
GPI = Structure( tau=tau, rest=+10.0, noise=0.030, activation=clamp )
THL = Structure( tau=tau, rest=-40.0, noise=0.001, activation=clamp )
structures = (CTX, STR, STN, GPI, THL)

CUE = np.zeros(4, dtype=[("mot", float), ("cog", float),
                         ("value" , float), ("reward", float)])
CUE["mot"]    = 0,1,2,3
CUE["cog"]    = 0,1,2,3
CUE["value"]  = 0.5
CUE["reward"] = 3/3.,2/3.,1/3.,0/3.


def weights(shape):
    Wmin, Wmax = 0.25, 0.75
    N = np.random.normal(0.5, 0.005, shape)
    N = np.minimum(np.maximum(N, 0.0),1.0)
    return (Wmin+(Wmax-Wmin)*N)

W1 = weights(4)
W2 = (2*np.eye(4) - np.ones((4,4))).ravel()
W3 = (2*np.eye(4) - np.ones((4,4))).ravel()
W4 = (2*np.eye(16) - np.ones((16,16))).ravel()
W5 = np.ones(4)
# W5[...] = [2.0,1.75,1.50,1.25]

connections = [
    OneToOne( CTX.cog.V, STR.cog.Isyn, W1,           gain=+1.0 ),
    OneToOne( CTX.mot.V, STR.mot.Isyn, weights(4),   gain=+1.0 ),
    OneToOne( CTX.ass.V, STR.ass.Isyn, weights(4*4), gain=+1.0 ),
    CogToAss( CTX.cog.V, STR.ass.Isyn, weights(4),   gain=+0.2 ),
    MotToAss( CTX.mot.V, STR.ass.Isyn, weights(4),   gain=+0.2 ),
    OneToOne( CTX.cog.V, STN.cog.Isyn, np.ones(4),   gain=+1.0 ),
    OneToOne( CTX.mot.V, STN.mot.Isyn, np.ones(4),   gain=+1.0 ),
    OneToOne( STR.cog.V, GPI.cog.Isyn, np.ones(4),   gain=-2.0 ),
    OneToOne( STR.mot.V, GPI.mot.Isyn, np.ones(4),   gain=-2.0 ),
    AssToCog( STR.ass.V, GPI.cog.Isyn, np.ones(4),   gain=-2.0 ),
    AssToMot( STR.ass.V, GPI.mot.Isyn, np.ones(4),   gain=-2.0 ),
    OneToAll( STN.cog.V, GPI.cog.Isyn, np.ones(4),   gain=+1.0 ),
    OneToAll( STN.mot.V, GPI.mot.Isyn, np.ones(4),   gain=+1.0 ),

    OneToOne( GPI.cog.V, THL.cog.Isyn, np.ones(4),   gain=-0.25 ),
    OneToOne( GPI.mot.V, THL.mot.Isyn, np.ones(4),   gain=-0.25 ),

    OneToOne( THL.cog.V, CTX.cog.Isyn, np.ones(4),   gain=+0.4 ),
    OneToOne( THL.mot.V, CTX.mot.Isyn, np.ones(4),   gain=+0.4 ),
    OneToOne( CTX.cog.V, THL.cog.Isyn, np.ones(4),   gain=+0.1 ),
    OneToOne( CTX.mot.V, THL.mot.Isyn, np.ones(4),   gain=+0.1 ),

    AllToAll( CTX.mot.V, CTX.mot.Isyn, W2,           gain=+0.5 ),
    AllToAll( CTX.cog.V, CTX.cog.Isyn, W3,           gain=+0.5 ),
    AllToAll( CTX.ass.V, CTX.ass.Isyn, W4,           gain=+0.5 ),

    AssToCog( CTX.ass.V, CTX.cog.Isyn, np.ones(4),   gain=+0.00 ),
    AssToMot( CTX.ass.V, CTX.mot.Isyn, np.ones(4),   gain=+0.01 ),
    CogToAss( CTX.cog.V, CTX.ass.Isyn, W4,           gain=+0.01 ),
    MotToAss( CTX.mot.V, CTX.ass.Isyn, np.ones(4),   gain=+0.00 ),
]


CUE = np.zeros(4, dtype=[("mot", float),
                         ("cog", float),
                         ("value" , float),
                         ("reward", float)])
CUE["mot"]    = 0,1,2,3
CUE["cog"]    = 0,1,2,3
CUE["value"]  = 0.5
CUE["reward"] = 3,2,1,0

cues_mot = np.array([0,1,2,3])
cues_cog = np.array([0,1,2,3])
cues_value = np.ones(4) * 0.5
cues_reward = np.array([3.0,2.0,1.0,0.0])/3.0

def set_trial():
    global cues_mot, cues_cog, cues_values, cues_reward

    np.random.shuffle(cues_cog)
    np.random.shuffle(cues_mot)
    c1,c2 = cues_cog[:2]
    m1,m2 = cues_mot[:2]
    v = 7
    noise = 0.001
    CTX.mot.Iext = 0
    CTX.cog.Iext = 0
    CTX.ass.Iext = 0
    CTX.mot.Iext[m1]  = v + np.random.normal(0,v*noise)
    CTX.mot.Iext[m2]  = v + np.random.normal(0,v*noise)
    CTX.cog.Iext[c1]  = v + np.random.normal(0,v*noise)
    CTX.cog.Iext[c2]  = v + np.random.normal(0,v*noise)
    CTX.ass.Iext[c1*4+m1] = v + np.random.normal(0,v*noise)
    CTX.ass.Iext[c2*4+m2] = v + np.random.normal(0,v*noise)


def iterate(dt):
    global connections, structures

    # Flush connections
    for connection in connections:
        connection.flush()

    # Propagate activities
    for connection in connections:
        connection.propagate()

    # Compute new activities
    for structure in structures:
        structure.evaluate(dt)

def reset():
    global cues_values, structures
    cues_value = np.ones(4) * 0.5
    for structure in structures:
        structure.reset()

dt = 0.001
for j in range(1):
    reset()
    for i in xrange(0,500):
        iterate(dt)
    set_trial()
    for i in xrange(500,3000):
        iterate(dt)


# -----------------------------------------------------------------------------
from display import *

dtype = [ ("CTX", [("mot", float, 4), ("cog", float, 4), ("ass", float, 16)]),
          ("STR", [("mot", float, 4), ("cog", float, 4), ("ass", float, 16)]),
          ("GPI", [("mot", float, 4), ("cog", float, 4)]),
          ("THL", [("mot", float, 4), ("cog", float, 4)]),
          ("STN", [("mot", float, 4), ("cog", float, 4)])]
history = np.zeros(3000, dtype=dtype)
history["CTX"]["mot"]   = CTX.mot.history[:3000]
history["CTX"]["cog"]   = CTX.cog.history[:3000]
history["CTX"]["ass"]   = CTX.ass.history[:3000]
history["STR"]["mot"] = STR.mot.history[:3000]
history["STR"]["cog"] = STR.cog.history[:3000]
history["STR"]["ass"] = STR.ass.history[:3000]
history["STN"]["mot"]      = STN.mot.history[:3000]
history["STN"]["cog"]      = STN.cog.history[:3000]
history["GPI"]["mot"]      = GPI.mot.history[:3000]
history["GPI"]["cog"]      = GPI.cog.history[:3000]
history["THL"]["mot"] = THL.mot.history[:3000]
history["THL"]["cog"] = THL.cog.history[:3000]

if 1:
    display_ctx(history, 3.0, "single-trial.pdf")
if 0:
    display_all(history, 3.0, "single-trial-all.pdf")
