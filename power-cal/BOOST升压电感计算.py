from decimal import Decimal, getcontext

def calculate_boost_inductance(VIN, VOUT, IOUTmax, FSW, gamma_min=Decimal('0.1'), gamma_max=Decimal('0.3')):
    """
    计算Boost升压电路的电感值(LMAX和LMIN)
    
    参数:
    VIN (float/str): 输入电压(V)
    VOUT (float/str): 输出电压(V)
    IOUTmax (float/str): 最大输出电流(A)
    FSW (float/str): 开关频率(MHz)
    gamma_min (Decimal): 最小电流纹波系数(默认0.1)
    gamma_max (Decimal): 最大电流纹波系数(默认0.3)
    
    返回:
    dict: 包含LMAX(μH)和LMIN(μH)的字典，精度为12位
    """
    # 设置12位精度
    getcontext().prec = 12
    
    # 转换所有输入为Decimal以确保精确计算
    VIN = Decimal(str(VIN))
    VOUT = Decimal(str(VOUT))
    IOUTmax = Decimal(str(IOUTmax))
    FSW_MHz = Decimal(str(FSW))
    
    # 转换频率为Hz (1MHz = 1e6 Hz)
    FSW_Hz = FSW_MHz * Decimal('1e6')
    
    # 计算LMAX (μH)
    numerator_LMAX = VIN * VIN * (VOUT - VIN)
    denominator_LMAX = gamma_min * IOUTmax * VOUT * VOUT * FSW_Hz
    LMAX = (numerator_LMAX / denominator_LMAX) * Decimal('1e6')  # 转换为μH
    
    # 计算LMIN (μH)
    numerator_LMIN = VIN * VIN * (VOUT - VIN)
    denominator_LMIN = gamma_max * IOUTmax * VOUT * VOUT * FSW_Hz
    LMIN = (numerator_LMIN / denominator_LMIN) * Decimal('1e6')  # 转换为μH
    
    return {
        float(LMAX.quantize(Decimal('1.00000000000'))),
        float(LMIN.quantize(Decimal('1.00000000000')))
    }

# 示例用法
if __name__ == "__main__":
    vin = 5.4      # 输入电压(V)
    vout = 7       # 输出电压(V)
    iout_max = 1.5   # 最大输出电流(A)
    fsw = 2.4        # 开关频率(MHz)
    
    lmax, lmin = calculate_boost_inductance(
        vin,vout,iout_max,fsw
    )
    print(f"LMAX: {lmax:.3f} μH")
    print(f"LMIN: {lmin:.3f} μH")

