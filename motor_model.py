"""
단상 유도전동기 등가회로 모델
이중 회전자계 이론 기반
"""

import numpy as np
from parameters import *


def forward_impedance(s):
    """
    정방향 회전자계에 의한 임피던스
    Z_f = (jX_m * (R_r/2s + jX_r/2)) / (R_r/2s + j(X_m + X_r/2))
    """
    if s == 0:
        s = 1e-6  # 0으로 나누기 방지
    
    R_f = R_r / (2 * s)
    X_f = X_r / 2
    
    # 병렬 연결: jX_m || (R_f + jX_f)
    Z_rotor = R_f + 1j * X_f
    Z_mag = 1j * X_m
    
    Z_forward = (Z_mag * Z_rotor) / (Z_mag + Z_rotor)
    return Z_forward


def backward_impedance(s):
    """
    역방향 회전자계에 의한 임피던스
    슬립 = 2-s (역방향 기준)
    """
    s_b = 2 - s
    if s_b == 0:
        s_b = 1e-6
    
    R_b = R_r / (2 * s_b)
    X_b = X_r / 2
    
    Z_rotor = R_b + 1j * X_b
    Z_mag = 1j * X_m
    
    Z_backward = (Z_mag * Z_rotor) / (Z_mag + Z_rotor)
    return Z_backward


def total_impedance(s):
    """전체 임피던스 = Z_s + Z_f + Z_b"""
    Z_s = R_s + 1j * X_s
    Z_f = forward_impedance(s)
    Z_b = backward_impedance(s)
    return Z_s + Z_f + Z_b


def stator_current(s):
    """스테이터 전류 (복소수)"""
    Z_total = total_impedance(s)
    I_s = V_s / Z_total
    return I_s


def forward_torque(s):
    """정방향 토크 (N·m)"""
    I_s = stator_current(s)
    Z_f = forward_impedance(s)
    
    # 정방향 자계에 전달되는 전력
    P_f = np.abs(I_s)**2 * np.real(Z_f)
    
    # 동기 각속도
    omega_sync = 2 * np.pi * n_sync / 60
    
    T_f = P_f / omega_sync
    return T_f


def backward_torque(s):
    """역방향 토크 (N·m) - 음의 방향"""
    I_s = stator_current(s)
    Z_b = backward_impedance(s)
    
    P_b = np.abs(I_s)**2 * np.real(Z_b)
    
    omega_sync = 2 * np.pi * n_sync / 60
    
    T_b = P_b / omega_sync
    return T_b  # 역방향이므로 빼야 함


def net_torque(s):
    """순 토크 = 정방향 - 역방향"""
    return forward_torque(s) - backward_torque(s)


def input_power(s):
    """입력 전력 (W)"""
    I_s = stator_current(s)
    Z_total = total_impedance(s)
    P_in = np.abs(I_s)**2 * np.real(Z_total)
    return P_in


def output_power(s):
    """출력 전력 (기계적 출력, W)"""
    T = net_torque(s)
    # 실제 회전 속도
    n_r = n_sync * (1 - s)
    omega_r = 2 * np.pi * n_r / 60
    P_out = T * omega_r
    return P_out


def efficiency(s):
    """효율 (%)"""
    P_in = input_power(s)
    P_out = output_power(s)
    if P_in == 0:
        return 0
    return (P_out / P_in) * 100


def rotor_speed(s):
    """로터 속도 (rpm)"""
    return n_sync * (1 - s)


# 테스트
if __name__ == "__main__":
    print("=== 단상 유도전동기 계산 테스트 ===")
    print(f"동기속도: {n_sync} rpm")
    print()
    
    for s in [0.05, 0.1, 0.2, 0.5, 1.0]:
        print(f"슬립 s={s}:")
        print(f"  순토크: {net_torque(s):.3f} N·m")
        print(f"  입력전력: {input_power(s):.1f} W")
        print(f"  출력전력: {output_power(s):.1f} W")
        print(f"  로터속도: {rotor_speed(s):.0f} rpm")
        print()
