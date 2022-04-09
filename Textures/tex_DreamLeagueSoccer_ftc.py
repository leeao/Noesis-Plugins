#By Allen
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Dream League Soccer ftc textures", ".ftc")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        idstring = bs.readBytes(4)
        if idstring != b'\x46\x54\x43\x33':
                return 0
        return 1	
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()

    idstring = bs.readBytes(4)
    decompSize = bs.readInt()
    unk = bs.readInt()
    width = bs.readShort()
    height = bs.readShort()
    texForamt = bs.readShort()
    unk2 = bs.readShort() #compression flag??
    zipData = bs.readBytes(bs.getSize()-20)	
    texData = rapi.decompInflate(zipData,decompSize)
    if texForamt == 2:
        texData = rapi.imageDecodeRaw(texData,width,height,"A4B4G4R4")
        texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_RGBA32)
        texList.append(texture)
    elif texForamt == 3:
        texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_RGBA32)
        texList.append(texture)
    else:
        print("Can't support format:",texForamt)
    
    return  1		
