#Double Dragon II Wander of the Dragons .bmp XBOX360 Textures Noesis Importer
#By Allen
from inc_noesis import *
import math
def registerNoesisTypes():
	handle = noesis.register("Double Dragon II Wander of the Dragons .bmp XBOX360 Textures", ".bmp")
	noesis.setHandlerTypeCheck(handle, noepyCheckType)
	noesis.setHandlerLoadRGBA(handle, txdLoadRGBA)    
	return 1
def noepyCheckType(data):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
    idstring = bs.readUInt()
    if idstring != 0x3:
            return 0
    return 1
def txdLoadRGBA(data, texList):
    bs = NoeBitStream(data, NOE_BIGENDIAN)
    idstring = bs.readUInt()

    bs.seek(0x20)
    texFormat = bs.readInt()
    bs.seek(0x30)
    texFlag = bs.readUInt() #Top Level Mipmap Data Size & Mipmap Count ??
    
    if texFormat == 0x52:
        width = int(math.sqrt((texFlag & 0xfffff0ff) * 2))
        height = width    
        
        data = bs.readBytes(int(width * height // 2))
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), width, height, 8)
        texList.append(NoeTexture(rapi.getInputName(), width, height, data, noesis.NOESISTEX_DXT1))
    elif texFormat == 0x71:
        width = int(math.sqrt(texFlag & 0xfffff0ff))
        height = width 
      
        data = bs.readBytes(width * height)
        data = rapi.imageUntile360DXT(rapi.swapEndianArray(data, 2), width, height, 16)
        data = rapi.imageDecodeDXT(data, width, height, noesis.FOURCC_ATI2)
        texList.append(NoeTexture(rapi.getInputName(), width, height, data, noesis.NOESISTEX_RGBA32))
        
    return 1
def texWriteRGBA(data, width, height, bs):
        bs.writeBytes(data)
        return 1    