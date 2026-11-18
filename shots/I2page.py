"""I2 page comp 'you'd fight the gods and win' (180.208-182.958, 66 frames) -> media/comp/pages/I2_full.mp4. BOOK team, v3.

Full-frame version of the I2 page for the BED team to cut to / map (they own media/comp/I2.mp4). Two beats: the small
monkey, the smallest figure and the only diagonal, staff planted, defiant against the host of heaven under its banners
(Li Jing's pagoda, Nezha's fire-wheels, Erlang with hawk and hound, thunder generals), all in cloud, no ground line;
on 'win' the host is scattered (I2_b). Static couplet 强者为尊该让我 / 英雄只此敢争先 in the blank lower centre.

v3 alive pass (§13): the page moves: a minimax/h3 clip animated from this very page (locked camera, spec
media/gen/specs/bk3_alive_*.json) replaces the still inside the full-spread framing; camera, torch and all typeset
writing outside that are ours. Remove `clip=` to return to the still page.
"""
from shots._pages3 import *

T0, T1 = 4325 / 24, 4391 / 24
T_WIN = 182.39


def setup(ctx):
    global PS
    PS = PageShot(ctx, 'I2', T0, T1, z1=0.72, focus=(1500, 1120), radius=(2600, 1800), t_b=T_WIN, clip='media/gen/bk3_alive_I2_h3_t1_ae6d4f2788.mp4')


def render(t, ctx):
    return PS.render(t, ctx)
