#by Allen
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("ParaParaParadise gcz", ".gcz")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1

def noepyCheckType(data):
    bs = decodeLZSS(data)
    idstring = noeStrFromBytes(bs.readBytes(2))
    if idstring != "GC":
        return 0
    return 1
def decodeLZSS(data):
    bs = NoeBitStream(data)
    decomSize = bs.readUInt() 
    comSize = bs.getSize() - 4
    comBuffer = bs.readBytes(comSize)
    deComBuffer = rapi.decompLZS01(comBuffer,decomSize)
    bs = NoeBitStream(deComBuffer)
    return bs
def noepyLoadRGBA(data, texList):
    bs = decodeLZSS(data)
    bs.setEndian(NOE_BIGENDIAN)
    idstring = noeStrFromBytes(bs.readBytes(2))
    bs.readShort()
    fileSize = bs.readInt()
    unk1 = bs.readInt()
    width = bs.readShort()
    height = bs.readShort()
    unk2 = bs.readInt()
    pixelDataSize = bs.readInt()
    textureData = bytearray(width * height * 4)
    for i in range(width*height):
        textureData[i*4:(i+1)*4] = rgb5a3(bs.readUShort())
    texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))   
    return 1
def rgb5a3(rawPixel):
    t = bytearray(4)
    if rawPixel & 0x8000 != 0:  # r5g5b5
        t[0] = (((rawPixel >> 10) & 0x1F) * 0xFF // 0x1F)
        t[1] = (((rawPixel >> 5)  & 0x1F) * 0xFF // 0x1F)
        t[2] = (((rawPixel >> 0)  & 0x1F) * 0xFF // 0x1F)
        t[3] = 0xFF
    else:  # r4g4b4a3
        t[0] = (((rawPixel >> 8)  & 0x0F) * 0xFF // 0x0F)
        t[1] = (((rawPixel >> 4)  & 0x0F) * 0xFF // 0x0F)
        t[2] = (((rawPixel >> 0)  & 0x0F) * 0xFF // 0x0F)
        t[3] = (((rawPixel >> 12) & 0x07) * 0xFF // 0x07)
    return t
