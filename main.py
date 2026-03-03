"""
단상 유도전동기 시뮬레이션
2x2 subplot 구조
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
from parameters import *
import motor_model as motor

# ============================================
# 시뮬레이션 설정
# ============================================
current_slip = 0.2  # 현재 슬립 (조절 가능)

# 시간 축 설정
T = 1 / f  # 1주기 (초)
t_total = T  # 1주기만 표시
t = np.linspace(0, t_total, 200)

# 슬립 축 설정
s_array = np.linspace(0.001, 1.0, 200)  # 0에 가까운 값부터 1까지

# ============================================
# 그래프 설정 (2x2)
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
ax_motor = axes[0, 0]   # (1,1) 회전자계 + 모터
ax_torque = axes[0, 1]  # (1,2) 토크-슬립
ax_wave = axes[1, 0]    # (2,1) 전압/전류 파형
ax_power = axes[1, 1]   # (2,2) 전력-슬립

fig.suptitle(f'Single-Phase Induction Motor Simulation (slip = {current_slip})', fontsize=14)

# ============================================
# (1,1) 회전자계 + 모터 설정
# ============================================
ax_motor.set_xlim(-1.5, 1.5)
ax_motor.set_ylim(-1.5, 1.5)
ax_motor.set_aspect('equal')
ax_motor.grid(True, alpha=0.3)
ax_motor.set_title('Rotating Field & Rotor')

# 스테이터 외곽 (원)
theta_circle = np.linspace(0, 2*np.pi, 100)
ax_motor.plot(1.2*np.cos(theta_circle), 1.2*np.sin(theta_circle), 'k-', linewidth=2)

# 회전자계 벡터들
Bm = 1.0
omega_field = 0.1  # 애니메이션 속도용

vec_fwd = ax_motor.quiver(0, 0, Bm/2, 0, angles='xy', scale_units='xy', scale=1,
                          color='red', width=0.015, label='Forward')
vec_bwd = ax_motor.quiver(0, 0, Bm/2, 0, angles='xy', scale_units='xy', scale=1,
                          color='blue', width=0.015, label='Backward')
vec_sum = ax_motor.quiver(0, 0, Bm, 0, angles='xy', scale_units='xy', scale=1,
                          color='green', width=0.02, label='Resultant B')

# 로터 반지름
rotor_radius = 0.8

# 로터 도선 (6개) - 개별 점으로 생성
rotor_angles_init = np.linspace(0, 2*np.pi, n_rotor_bars, endpoint=False)
rotor_dots = []
for i in range(n_rotor_bars):
    dot, = ax_motor.plot(rotor_radius * np.cos(rotor_angles_init[i]),
                         rotor_radius * np.sin(rotor_angles_init[i]),
                         'o', markersize=15, color='gray', 
                         markeredgecolor='black', markeredgewidth=2, zorder=5)
    rotor_dots.append(dot)

# 로터 중심 표시 (회전 확인용)
rotor_marker, = ax_motor.plot([0, rotor_radius*0.5], [0, 0], 'k-', linewidth=3)

# 힘 벡터들은 동적으로 생성/삭제
force_artists = []  # 현재 프레임의 힘 벡터들

ax_motor.legend(loc='upper right', fontsize=8)

# ============================================
# (2,1) 전압/전류 파형 설정
# ============================================
ax_wave.set_xlim(0, t_total * 1000)  # ms 단위
ax_wave.set_ylim(-1.5, 1.5)
ax_wave.set_xlabel('Time (ms)')
ax_wave.set_ylabel('Normalized Amplitude')
ax_wave.set_title('Voltage & Current Waveforms')
ax_wave.grid(True, alpha=0.3)

# 전압 파형 (정규화)
v_wave = np.sin(2 * np.pi * f * t)
line_voltage, = ax_wave.plot(t * 1000, v_wave, 'b-', label='Voltage', linewidth=1.5)

# 전류 파형 (위상 지연 있음 - 나중에 계산)
i_wave = np.sin(2 * np.pi * f * t - np.pi/6)  # 임시 위상
line_current, = ax_wave.plot(t * 1000, i_wave, 'r-', label='Current', linewidth=1.5)

# 현재 시간 표시선
time_line = ax_wave.axvline(x=0, color='k', linestyle='--', linewidth=2)
time_dot_v, = ax_wave.plot(0, 0, 'bo', markersize=10)  # 전압 교점
time_dot_i, = ax_wave.plot(0, 0, 'ro', markersize=10)  # 전류 교점

ax_wave.legend(loc='upper right', fontsize=8)

# ============================================
# (1,2) 토크-슬립 그래프 설정
# ============================================
ax_torque.set_xlim(0, 1)
ax_torque.set_xlabel('Slip (s)')
ax_torque.set_ylabel('Torque (N·m)')
ax_torque.set_title('Torque vs Slip')
ax_torque.grid(True, alpha=0.3)

# 토크 곡선 계산
T_fwd = np.array([motor.forward_torque(s) for s in s_array])
T_bwd = np.array([motor.backward_torque(s) for s in s_array])
T_net = np.array([motor.net_torque(s) for s in s_array])

ax_torque.plot(s_array, T_fwd, 'r--', label='Forward', linewidth=1.5)
ax_torque.plot(s_array, T_bwd, 'b--', label='Backward', linewidth=1.5)
ax_torque.plot(s_array, T_net, 'g-', label='Net Torque', linewidth=2)

ax_torque.set_ylim(0, max(T_net) * 1.2)

# 현재 슬립 표시선
slip_line_torque = ax_torque.axvline(x=current_slip, color='k', linestyle='--', linewidth=2)
slip_dot_torque, = ax_torque.plot(current_slip, motor.net_torque(current_slip), 
                                   'go', markersize=12)

ax_torque.legend(loc='upper right', fontsize=8)

# ============================================
# (2,2) 전력-슬립 그래프 설정
# ============================================
ax_power.set_xlim(0, 1)
ax_power.set_xlabel('Slip (s)')
ax_power.set_ylabel('Power (W)')
ax_power.set_title('Power vs Slip')
ax_power.grid(True, alpha=0.3)

# 전력 곡선 계산
P_in = np.array([motor.input_power(s) for s in s_array])
P_out = np.array([motor.output_power(s) for s in s_array])

ax_power.plot(s_array, P_in, 'b-', label='Input Power', linewidth=1.5)
ax_power.plot(s_array, P_out, 'g-', label='Output Power', linewidth=1.5)

ax_power.set_ylim(0, max(P_in) * 1.1)

# 현재 슬립 표시선
slip_line_power = ax_power.axvline(x=current_slip, color='k', linestyle='--', linewidth=2)
slip_dot_in, = ax_power.plot(current_slip, motor.input_power(current_slip), 
                              'bo', markersize=10)
slip_dot_out, = ax_power.plot(current_slip, motor.output_power(current_slip), 
                               'go', markersize=10)

ax_power.legend(loc='upper right', fontsize=8)

# ============================================
# 힘벡터용 사전 계산 (이중 회전자계 분리)
# ============================================
T_fwd_val = motor.forward_torque(current_slip)
T_bwd_val = motor.backward_torque(current_slip)
T_net_val = T_fwd_val - T_bwd_val

# 힘 화살표 스케일링: 최대 화살표 길이 ≈ 0.3
max_force_per_bar = 2 * T_fwd_val / n_rotor_bars + 0.01
force_vis_scale = 0.3 / max_force_per_bar

# ============================================
# 애니메이션 업데이트 함수
# ============================================
def update(frame):
    global force_artists
    
    theta_field = omega_field * frame  # 자계 회전 각도 (동기속도)
    theta_rotor = theta_field * (1 - current_slip)  # 로터 회전 각도 (슬립만큼 느림)
    
    # --- (1,1) 회전자계 업데이트 ---
    fwd_x = (Bm/2) * np.cos(theta_field)
    fwd_y = (Bm/2) * np.sin(theta_field)
    bwd_x = (Bm/2) * np.cos(-theta_field)
    bwd_y = (Bm/2) * np.sin(-theta_field)
    sum_x = fwd_x + bwd_x
    sum_y = fwd_y + bwd_y
    
    vec_fwd.set_UVC(fwd_x, fwd_y)
    vec_bwd.set_UVC(bwd_x, bwd_y)
    vec_sum.set_UVC(sum_x, sum_y)
    
    # --- 로터 회전 업데이트 ---
    rotor_angles = np.linspace(0, 2*np.pi, n_rotor_bars, endpoint=False) + theta_rotor
    rotor_x = rotor_radius * np.cos(rotor_angles)
    rotor_y = rotor_radius * np.sin(rotor_angles)
    
    # 로터 중심 마커 (회전 확인용)
    rotor_marker.set_data([0, rotor_radius*0.5*np.cos(theta_rotor)],
                          [0, rotor_radius*0.5*np.sin(theta_rotor)])
    
    # --- 이전 힘 벡터 제거 ---
    for artist in force_artists:
        artist.remove()
    force_artists = []
    
    # --- 도선별 전류 및 힘 계산 ---
    for i, alpha in enumerate(rotor_angles):
        # 도선 위치 업데이트
        rotor_dots[i].set_data([rotor_x[i]], [rotor_y[i]])
        
        # 전류 계산 (자계와 도선의 상대적 위치 기반)
        I_val = np.sin(theta_field - alpha)
        
        # 전류 방향에 따른 색상
        if I_val > 0.15:
            rotor_dots[i].set_color('red')      # ⊙ 전류 나옴
        elif I_val < -0.15:
            rotor_dots[i].set_color('blue')     # ⊗ 전류 들어감
        else:
            rotor_dots[i].set_color('gray')
        
        # --- 이중 회전자계 기반 힘 계산 ---
        # 정방향 자계: 도선 근처에서 CCW 방향 힘 (항상 ≥ 0)
        # cos²(θ_fwd - α) 패턴: 자계 피크 위치에서 최대
        f_fwd = 1 + np.cos(2 * (theta_field - alpha))  # 0~2, 평균 1
        
        # 역방향 자계: 도선 근처에서 CW 방향 힘 (항상 ≥ 0)
        f_bwd = 1 + np.cos(2 * (theta_field + alpha))  # 0~2, 평균 1
        
        # 순 접선방향 힘 (양=CCW=정방향)
        # T_fwd > T_bwd이므로 대부분 양수 → 모터 동작!
        F_tang = (T_fwd_val * f_fwd - T_bwd_val * f_bwd) / n_rotor_bars
        
        if abs(F_tang) > 0.01:
            # 접선 방향 단위 벡터 (CCW)
            tangent_x = -np.sin(alpha)
            tangent_y = np.cos(alpha)
            
            dx = F_tang * tangent_x * force_vis_scale
            dy = F_tang * tangent_y * force_vis_scale
            
            arrow = ax_motor.arrow(rotor_x[i], rotor_y[i], dx, dy,
                                   head_width=0.05, head_length=0.025,
                                   fc='orange', ec='darkorange', linewidth=1.5,
                                   zorder=10)
            force_artists.append(arrow)
    
    # --- (2,1) 시간 표시 업데이트 ---
    frames_per_cycle = int(2 * np.pi / omega_field)
    current_time = (frame % frames_per_cycle) / frames_per_cycle * T
    current_time_ms = current_time * 1000
    
    time_line.set_xdata([current_time_ms, current_time_ms])
    
    v_now = np.sin(2 * np.pi * f * current_time)
    i_now = np.sin(2 * np.pi * f * current_time - np.pi/6)
    
    time_dot_v.set_data([current_time_ms], [v_now])
    time_dot_i.set_data([current_time_ms], [i_now])
    
    return []

# ============================================
# 애니메이션 시작
# ============================================
plt.tight_layout()

# 슬립을 고려한 프레임 수 계산
# s = 0.1이면 자계 10주기 = 로터 9주기 (최소공배수)
# 일반: 자계 n주기, 로터 n*(1-s)주기가 정수가 되는 최소 n
from math import gcd
# s = p/q 형태로 근사 (s=0.1 → 1/10)
s_frac_num = int(round(current_slip * 100))  # 분자 (예: 10)
s_frac_den = 100                              # 분모
g = gcd(s_frac_num, s_frac_den)
s_num = s_frac_num // g   # 1
s_den = s_frac_den // g   # 10
# 자계 s_den 주기 = 로터 (s_den - s_num) 주기로 루프
n_field_cycles = s_den  # 10주기

frames_per_cycle = int(2 * np.pi / omega_field)
total_frames = frames_per_cycle * n_field_cycles

ani = FuncAnimation(fig, update, frames=total_frames, interval=50, blit=False)

# # GIF 저장
# print(f"GIF 저장 중... (자계 {n_field_cycles}주기, 총 {total_frames}프레임)")
# ani.save('induction_motor.gif', writer='pillow', fps=20)
# print("GIF 저장 완료: induction_motor.gif")

plt.show()