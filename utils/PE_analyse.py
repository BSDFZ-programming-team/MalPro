import pefile
from capstone import *
MACHINES = {
    0x014c: "I386",          # intel386处理器或后续兼容处理器
    0x0162: "R3000",         # MIPS little-endian, 0x160 big-endian
    0x0166: "R4000",         # MIPS小尾处理器
    0x0168: "R10000",        # MIPS little-endian
    0x0169: "WCEMIPSV2",     # MIPS小尾WCEv2处理器
    0x0184: "ALPHA",         # Alpha_AXP
    0x01a2: "SH3",           # Hitachi SH3处理器
    0x01a3: "SH3DSP",        # Hitachi SH3 DSP处理器
    0x01a4: "SH3E",          # SH3E little-endian
    0x01a6: "SH4",           # Hitachi SH4处理器
    0x01a8: "SH5",           # Hitachi SH5处理器
    0x01c0: "ARM",           # ARM小尾处理器
    0x01c2: "THUMB",         # ARM或Thumb处理器
    0x01c4: "ARMNT",         # ARMv7(或更高)处理器的Thumb模式
    0x01d3: "AM33",          # MatsushitaAM33处理器
    0x01f0: "POWERPC",       # PowerPC小尾处理器
    0x01f1: "POWERPCFP",     # 带浮点支持的PowerPC处理器
    0x0200: "IA64",          # Intel Itanium处理器系列
    0x0266: "MIPS16",        # MIPS16处理器
    0x0284: "ALPHA64",       # ALPHA64
    0x0366: "MIPSFPU",       # 带FPU的MIPS处理器
    0x0466: "MIPSFPU16",     # 带FPU的MIPS16处理器
    0x0520: "TRICORE",       # Infineon
    0x0CEF: "CEF",
    0x0EBC: "EBC",           # EFI字节码处理器
    0x8664: "AMD64",         # x64处理器
    0x9041: "M32R",          # MatsushitaM32R小尾处理器
    0xAA64: "ARM64",         # ARM64 Little-Endian
    0xC0EE: "CEE"
}
def check_avaliable(pe_file):
    try:
        pe = pefile.PE(pe_file)
        PE_file_PE = pe.NT_HEADERS
        PE_file_MZ = pe.DOS_HEADER
        assert hex(PE_file_MZ.e_magic) == '0x5a4d' and hex(PE_file_PE.Signature) == '0x4550'
    except Exception as e:
        if type(e) == AssertionError:
            result = 'Header broken'
        else:
            result = 'Load failed'
    else:
        result = pe
    return result
def analyze_machine(pe_obj):
    machine = pe_obj.FILE_HEADER.Machine
    if machine in MACHINES:
        return MACHINES[machine]
    else:
        return ''