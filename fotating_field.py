import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 1. 그래프 설정
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(-1.1, 1.1)
ax.set_ylim(-1.1, 1.1)
ax.set_aspect('equal')
ax.grid(True)
ax.axhline(y=0, color='k', linewidth=0.5)
ax.axvline(x=0, color='k', linewidth=0.5)
ax.set_title("Double Revolving Field Theory")

# 2. 파라미터
Bm = 1.0
omega = 0.1

# 3. 원점에서 시작하는 벡터들 (진한 색)
vec_fwd = ax.quiver(0, 0, Bm/2, 0, 
                    angles='xy', scale_units='xy', scale=1,
                    color='red', width=0.005,
                    label='Forward (Bm/2)')

vec_bwd = ax.quiver(0, 0, Bm/2, 0,
                    angles='xy', scale_units='xy', scale=1,
                    color='blue', width=0.005,
                    label='Backward (Bm/2)')

# 4. 평행사변형용 벡터들 (연한 색, 가는 화살표)
vec_fwd_shifted = ax.quiver(0, 0, Bm/2, 0,
                            angles='xy', scale_units='xy', scale=1,
                            color='red', alpha=0.4, width=0.003)

vec_bwd_shifted = ax.quiver(0, 0, Bm/2, 0,
                            angles='xy', scale_units='xy', scale=1,
                            color='blue', alpha=0.4, width=0.003)

# 5. 합성 벡터 (굵은 초록)
vec_sum = ax.quiver(0, 0, Bm, 0,
                    angles='xy', scale_units='xy', scale=1,
                    color='green', width=0.01,
                    label='Resultant (B)')

ax.legend(loc='upper right')

# 6. 업데이트 함수
def update(frame):
    theta = omega * frame
    
    # 정방향: +ωt (반시계)
    fwd_x = (Bm/2) * np.cos(theta)
    fwd_y = (Bm/2) * np.sin(theta)
    
    # 역방향: -ωt (시계)
    bwd_x = (Bm/2) * np.cos(-theta)
    bwd_y = (Bm/2) * np.sin(-theta)
    
    # 합성
    sum_x = fwd_x + bwd_x
    sum_y = fwd_y + bwd_y
    
    # 원점에서 시작하는 벡터들
    vec_fwd.set_UVC(fwd_x, fwd_y)
    vec_bwd.set_UVC(bwd_x, bwd_y)
    
    # 평행사변형: 정방향 끝점에서 역방향 벡터
    vec_bwd_shifted.set_offsets([fwd_x, fwd_y])
    vec_bwd_shifted.set_UVC(bwd_x, bwd_y)
    
    # 평행사변형: 역방향 끝점에서 정방향 벡터
    vec_fwd_shifted.set_offsets([bwd_x, bwd_y])
    vec_fwd_shifted.set_UVC(fwd_x, fwd_y)
    
    # 합성 벡터
    vec_sum.set_UVC(sum_x, sum_y)
    
    return vec_fwd, vec_bwd, vec_fwd_shifted, vec_bwd_shifted, vec_sum

# 7. 애니메이션 (정확히 1바퀴 = 2π/omega 프레임)
frames = int(2 * np.pi / omega)  # 1회전에 필요한 프레임 수
ani = FuncAnimation(fig, update, frames=frames, interval=50)

# 8. GIF로 저장 (pillow 필요: pip install pillow)
# ani.save('rotating_field.gif', writer='pillow', fps=20)
# print("GIF 저장 완료: rotating_field.gif")

plt.show()