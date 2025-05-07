from decimal import Decimal, getcontext

def calculate_buck_inductance(
    vin, vout, iout_max, fsw 
):
    """
    计算Buck电路的Lmax和Lmin电感值
    
    参数:
        vout: 输出电压(V)
        vin: 输入电压(V)
        iout_max: 最大输出电流(A)
        fsw: 开关频率(MHz) 
    返回:
        (Lmax, Lmin) 单位μH
    """
    # 设置计算精度
    getcontext().prec = 10 # 计算精度(小数位数)
    gamma_max = Decimal(str(0.4)) # 最大纹波系数
    gamma_min = Decimal(str(0.2)) # 最小纹波系数
    
    # 转换为Decimal类型
    vout = Decimal(str(vout))
    vin = Decimal(str(vin))
    iout_max = Decimal(str(iout_max))
    fsw_mhz = Decimal(str(fsw))
    
    # 将MHz转换为Hz
    fsw_hz = fsw_mhz * Decimal('1e6')
    
    # 计算占空比相关项 (1 - Vout/Vin)
    duty_term = (Decimal('1') - vout / vin)
    
    # 计算Lmax和Lmin
    lmax = (vout * duty_term) / (gamma_min * iout_max * fsw_hz)
    lmin = (vout * duty_term) / (gamma_max * iout_max * fsw_hz)
    
    # 转换为μH
    lmax_uh = lmax * Decimal('1e6')
    lmin_uh = lmin * Decimal('1e6')
    
    return float(lmax_uh), float(lmin_uh)

if __name__ == "__main__":
    vin = 12.0       # 输入电压(V)
    vout = 3.3       # 输出电压(V)
    iout_max = 2.0   # 最大输出电流(A)
    fsw = 1.0        # 开关频率(MHz)
    
    lmax, lmin = calculate_buck_inductance(
        vin, vout, iout_max, fsw
    )
    
    print(f"LMAX: {lmax:.3f} μH")
    print(f"LMIN: {lmin:.3f} μH")