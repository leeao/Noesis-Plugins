#By Allen

from inc_noesis import *

import math
def registerNoesisTypes():
    handle = noesis.register("XBOX360 .xb3t texture", ".xb3t")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        return 1	
        
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()


    pixelBuff = bs.readBytes(bs.getSize())
    size = bs.getSize()
    if size == 393216:
        width = 512
        height = 512
        texData = rapi.imageUntile360DXT(rapi.swapEndianArray(pixelBuff, 2), width, height, 16)     
        texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_DXT5)
        texList.append(texture) 
    elif size == 65536:
        width = 256
        height = 256
        texData = rapi.imageUntile360DXT(rapi.swapEndianArray(pixelBuff, 2), width, height, 8)     
        texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_DXT1)
        texList.append(texture) 
    
    return  1		


