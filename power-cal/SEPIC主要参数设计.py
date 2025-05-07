from decimal import Decimal, getcontext
import math

def calculate_sepic_parameters(
    vin_min: Decimal,  # 输入最小电压(VDC)
    vin_nominal: Decimal,  # 额定输入电压(VDC)
    vin_max: Decimal,  # 输入最大电压(VDC)
    vout: Decimal,  # 输出电压(VDC)
    iout: Decimal,  # 输出电流(A)
    fsw_khz: Decimal,  # 开关频率(KHz)
    cs_uf: Decimal,  # 耦合电容Cs容量(uF)
    vd: Decimal = Decimal('0.35'),  # 输出整流二极管正向压降(VDC)
    mosfet_model: str = '8N60',  # MOSFET型号
    rds_on: Decimal = Decimal('0.11'),  # MOSFET开通内阻(Ω)
    qgd: Decimal = Decimal('0.000012'),  # MOSFET GD充电
    igate: Decimal = Decimal('0.2'),  # MOSFET驱动电流(A)
    output_ripple_voltage: Decimal = Decimal('0.06')  # 输出电容的纹波电压(Vp-p)
) -> dict:
    """
    计算SEPIC转换器的各项参数
    
    参数:
        vin_min: 输入最小电压(VDC)
        vin_nominal: 额定输入电压(VDC)
        vin_max: 输入最大电压(VDC)
        vout: 输出电压(VDC)
        iout: 输出电流(A)
        fsw_khz: 开关频率(KHz)
        cs_uf: 耦合电容Cs容量(uF)
        vd: 输出整流二极管正向压降(VDC) [默认: 0.35]
        mosfet_model: MOSFET型号 [默认: '8N60']
        rds_on: MOSFET开通内阻(Ω) [默认: 0.11]
        qgd: MOSFET GD充电 [默认: 0.000012]
        igate: MOSFET驱动电流(A) [默认: 0.2]
        output_ripple_voltage: 输出电容的纹波电压(Vp-p) [默认: 0.06]
    
    返回:
        包含所有计算参数的字典，带有明确单位
    """
    # 设置Decimal精度为12
    getcontext().prec = 12
    
    # 计算输入电流
    input_current = iout * (vout + vd) / vin_min  # 修正公式
    # input_current = iout * vout / vin_min
    
    # 计算占空比
    low_voltage_duty_cycle = (vout + vd) / (vin_min + vout + vd)
    high_voltage_duty_cycle = (vout + vd) / (vin_max + vout + vd)
    
    # 计算电感纹波电流(假设为输入电流的40%)
    inductor_ripple_current = input_current * Decimal('0.4')
    
    # 计算独立磁芯电感值(uH)
    inductor_value_separate = (vin_min * low_voltage_duty_cycle * Decimal('1e3')) / (inductor_ripple_current * fsw_khz) 
    
    # 计算电感峰值电流
    inductor1_peak_current = iout * vout * (Decimal('1') + Decimal('0.4') / Decimal('2')) / vin_min
    inductor2_peak_current = iout * (Decimal('1') + Decimal('0.4') / Decimal('2'))
    
    # 计算共用磁芯电感值(uH)
    inductor_value_shared = vin_min * low_voltage_duty_cycle * Decimal('1e3') / ( Decimal('2') * inductor_ripple_current * fsw_khz)
    
    # 计算MOSFET参数
    mosfet_peak_current = input_current / low_voltage_duty_cycle
    mosfet_rms_current = input_current / Decimal(math.sqrt(float(low_voltage_duty_cycle)))
    
    # 计算MOSFET消耗功率(W)
    conduction_loss = mosfet_rms_current ** Decimal('2') * rds_on * low_voltage_duty_cycle
    switching_loss = (vin_min + vout) * mosfet_peak_current * qgd * fsw_khz / (igate)
    mosfet_power_loss = conduction_loss + switching_loss
    
    # 计算二极管最小反向峰值电压(V)
    diode_reverse_voltage = vin_max + vout
    
    # 计算耦合电容参数
    cs_avg_current = iout * Decimal(math.sqrt(float((vout + vd) / vin_min)))
    # cs_avg_current = iout * Decimal(math.sqrt(float(vout / vin_min)))
    cs_ripple_voltage = (iout * low_voltage_duty_cycle ) / (cs_uf * fsw_khz)
    
    # 计算输出电容参数
    max_output_esr = output_ripple_voltage * Decimal('0.5') / (inductor1_peak_current + inductor2_peak_current)
    min_output_capacitance = (iout * low_voltage_duty_cycle)  / (output_ripple_voltage * fsw_khz * Decimal('0.5'))  # 转换为uF
    
    # 计算输入电容平均电流(A)
    input_cap_rms_current = inductor_ripple_current / Decimal(math.sqrt(12))
    
    # 返回带有明确单位的格式化结果
    return {
        '输入最小电压(VDC)Vin(min)': f"{vin_min} V",
        '额定输入电压(VDC)Vin': f"{vin_nominal} V",
        '输入最大电压(VDC)Vin(max)': f"{vin_max} V",
        '输入电流(A)Iin': f"{input_current:.3f} A",
        '输出电压(VDC)Vout': f"{vout} V",
        '输出电流(A)Iout': f"{iout} A",
        '输出整流二极管正向压降(VDC)VD': f"{vd} V",
        '低压占空比Dmax': f"{low_voltage_duty_cycle:.9f}",
        '高压占空比Dmin': f"{high_voltage_duty_cycle:.9f}",
        '电感纹波电流(A)△IL': f"{inductor_ripple_current:.3f} A",
        '开关频率(KHz)Fsw': f"{fsw_khz} kHz",
        'L1=L2感量(uH)L(独立磁芯)': f"{inductor_value_separate:.8f} uH",
        'L1电感峰值电流IL1(PEAK)': f"{inductor1_peak_current:.3f} A",
        'L2电感峰值电流IL2(PEAK)': f"{inductor2_peak_current:.3f} A",
        'L1=L2感量(uH)L(公用磁芯)': f"{inductor_value_shared:.8f} uH",
        'MOSFET IDS(PEAK)(A)': f"{mosfet_peak_current:.8f} A",
        'MOSFET IDS(RMS)(A)': f"{mosfet_rms_current:.8f} A",
        'MOSFET消耗功率PD(W)': f"{mosfet_power_loss:.8f} W",
        '二极管最小反向峰值电压VRD': f"{diode_reverse_voltage:.1f} V",
        'MOSFET型号': mosfet_model,
        'MOSFET开通内阻RDS(ON)': f"{rds_on} Ω",
        'MOSFET GD充电QGD': f"{qgd} C",
        'MOSFET驱动电流IGATE': f"{igate} A",
        '耦合电容的平均电流ICS(A)': f"{cs_avg_current:.8f} A",
        '耦合电容的纹波电压△VCS(V)': f"{cs_ripple_voltage:.8f} V",
        '耦合电容Cs容量': f"{cs_uf} uF",
        '输出电容的平均电流ICout(A)': f"{iout} A",
        '输出电容的纹波电压Vripple(Vp-p)': f"{output_ripple_voltage} V",
        '输出电容ESR(Ω)': f"≤ {max_output_esr:.8f} Ω",
        '输出电容容量Cout': f"≥ {min_output_capacitance:.8f} uF",
        '输入电容的平均电流Icin(RMS)(A)': f"{input_cap_rms_current:.8f} A"
    }


# 示例用法
if __name__ == "__main__":
    # 输入参数
    params = calculate_sepic_parameters(
        vin_min=Decimal('5'),
        vin_nominal=Decimal('7.4'),
        vin_max=Decimal('8.4'),
        vout=Decimal('12'),
        iout=Decimal('0.5'),
        fsw_khz=Decimal('400'),
        cs_uf=Decimal('22')
    )
    
    # 打印结果
    for key, value in params.items():
        print(f"{key.ljust(35)}: {value}")