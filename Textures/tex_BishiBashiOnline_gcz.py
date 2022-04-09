#by Allen
from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Bishi Bashi Online.gcz", ".gcz")
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
    pixel = bs.readBytes(pixelDataSize)
    #pixel = rapi.swapEndianArray(pixel,2) #only for ParaParaParadise .gcz (big endian)
    textureData = rapi.imageDecodeRaw(pixel,width,height,"b5g5r5a1")  
    
    #textureData = bytearray(width * height * 4)
    #for i in range(width*height):
    #    textureData[i*4:(i+1)*4] = rgba5551(bs.readUShort())
        
    texList.append(NoeTexture(rapi.getInputName(), width, height, textureData, noesis.NOESISTEX_RGBA32))   
    return 1

def rgba5551(rawPixel):
    t = bytearray(4)    
    t[0] = (((rawPixel >> 10) & 0x1F) << 3) #R
    t[1] = (((rawPixel >> 5)  & 0x1F) << 3) #G
    t[2] = ((rawPixel & 0x1F) << 3)         #B
    if rawPixel & 0x8000 > 0:
        t[3] = 0xFF                         #A
    else:
        t[3] = 0                            #A
    return t