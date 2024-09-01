import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 形状パラメータの設定
w_m = 1.0  # 適宜変更
d = 1.0  # 適宜変更
h_t = 0.1  # 適宜変更
w_t = 9990.0 # 適宜変更
w_d = 0.1  # 適宜変更

# バネマスダンパ系パラメータ設定
m = 1.0  # 質量 [kg]
c = 0.5  # ダンパの減衰係数 [N･s/s]
k = 0.8  # ばね定数 [N/m]
g_d =2.0   # distance gain
N = 100


def mun(x, y, w_m, d):
    return np.exp(-w_m * ((np.abs(x) - d)**2 + y**2))

def tik(x, y, h_t, w_t, d):
    return h_t * np.exp(-w_t * ((np.abs(x) - d)**2 + y**2)**2)

def dou(x,w_d):
    return -w_d * x**4

def opp(x, y, w_m, d, h_t, w_t, w_d):
    return mun(x, y, w_m, d) + tik(x, y, h_t, w_t, d) + dou(x,w_d)

def impulse_response(t, m, c, k):
    return (1 / m) * np.exp((-c / (2 * m)) * t) * np.sin(np.sqrt(k / m - (c / (2 * m))**2) * t)


# サンプルのx, yの値
x = np.linspace(-2.0, 2.0, 50)
y = np.linspace(-2.0, 2.0, 50)
x,y=np.meshgrid(x,y)
y_init=y


st.title("Oppaython")
st.sidebar.title("Opparameters")
w_m=st.sidebar.slider("Mun constant",2.0,0.1,value=w_m)
d=st.sidebar.slider("Mun distance",2.0,0.1,value=d)
h_t=st.sidebar.slider("Tik constant",1.0,0.01,value=h_t)
w_t=st.sidebar.slider("Tik distance",10000.0,10.0,value=w_t)
red_value = st.sidebar.slider("Tik color", 0, 255, value=255)
w_d=st.sidebar.slider("Dou constant",1.0,0.01,value=w_d)
m=st.sidebar.slider("Mass",10.0,0.1,value=m)
c=st.sidebar.slider("Damping",5.0,0.1,value=c)
k=st.sidebar.slider("Oppy constant",5.0,0.1,value=k)
g_d=st.sidebar.slider("Distance gain",5.0,1.0,value=g_d)


# カスタムカラーのスケール
colorscale = [
    [0, '#ffcd94'],  # zが小さいときの色（薄だいだい色）
    [0.9, '#ffcd94'],  # zが0.8以下のときの色（薄だいだい色）
    [2, f'rgb({red_value}, 0, 0)']          # zが最大のときの色（赤色）
]

z_init = opp(x, y, w_m, d, h_t, w_t,  w_d) 

# 時間の範囲を設定
t_values = np.linspace(0, 20, 20)

# フレームデータの準備
frames = []
for i, t in enumerate(t_values):
    y = np.linspace(-2.0, 2.0, 50)
    z = opp(x, y_init, w_m, d, h_t, w_t,  w_d)  # yの範囲とステップサイズを定義します
    y = np.where(z > 0.1, impulse_response(t, m, c, k) * z * g_d + y_init, y_init)
    # フレームの作成
    frames.append(go.Frame(data=[go.Surface(x=x, y=y,z=z,colorscale=colorscale)], name=str(i)))

# 初期フレーム
initial_frame = go.Surface(x=x, y=y_init,z=z_init ,colorscale=colorscale)

# レイアウト設定
layout = go.Layout(
    title="アニメーションサンプル",
    width=800,  # グラフの幅
    height=800,  # グラフの高さ
    scene=dict(
    xaxis=dict(range=[-2, 2], autorange=False),  # x軸の範囲を設定
    yaxis=dict(range=[-2, 2], autorange=False),  # y軸の範囲を設定
    zaxis=dict(range=[-1.5, 1], autorange=False),  # z軸の範囲を設定
    ),
    updatemenus=[
        dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True, "mode": "immediate"}]),  # durationを100ミリ秒に設定
                dict(label="Pause",
                     method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}])
            ]
        )
    ],
    sliders=[{
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Frame:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 1, "easing": "cubic-in-out"},  # transitionのdurationを100ミリ秒に設定
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [{
            "args": [
                [str(i)],
                {"frame": {"duration": 0.1, "redraw": True},  # frameのdurationを100ミリ秒に設定
                 "mode": "immediate",
                 "transition": {"duration": 0.1}}
            ],
            "label": str(i),
            "method": "animate"
        } for i in range(len(t_values))]
    }]
)

# 図の作成
fig = go.Figure(data=[initial_frame], layout=layout, frames=frames)

# 表示
st.plotly_chart(fig)