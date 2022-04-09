#Call Of Duty XBOX360 .hi Format Noesis Importer / Exporter
#By Allen

from inc_noesis import *
from inc_xbox360_untile import *
import math
def registerNoesisTypes():
    handle = noesis.register("Call Of Duty XBOX360 .hi texture", ".hi")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    noesis.setHandlerWriteRGBA(handle, texWriteRGBA)
    return 1
def noepyCheckType(data):
        bs = NoeBitStream(data)
        return 1	
def noepyLoadRGBA(data, texList):
    bs = NoeBitStream(data)	
    ctx = rapi.rpgCreateContext()

    #The height and width can only be guessed and may not be correct.
    #Can be specified manually    
    info = getWidthHeight(bs.getSize())
    width = info[0]
    height = info[1]

    pixelBuff = bs.readBytes(bs.getSize())
    pixelBuff = rapi.swapEndianArray(pixelBuff, 2)
    texData = XGUntileSurfaceToLinearTexture(pixelBuff, width, height, "DXT1")        
         
    texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_DXT1)
    texList.append(texture) 
    

    
    return  1		
def texWriteRGBA(data, width, height, bs):
    DXT1Data = rapi.imageEncodeDXT(data,4,width,height,noesis.NOE_ENCODEDXT_BC1)
    DXT1Data = rapi.swapEndianArray(DXT1Data, 2)
    outData = XGTileSurfaceFromLinearTexture(DXT1Data,width, height,"DXT1") 
    bs.writeBytes(outData)
    return 1
    
widthList = (2,4,8,16,32,64,128,256,512,1024,2048)    

def getWidthHeight(buffSize):
    tWidth = int(math.sqrt(buffSize * 2))
    if tWidth not in widthList:
        sizeList = []
        for i in range(len(widthList)):
            index = len(widthList) - 1 - i
            tWidth = widthList[index]
            for j in range(len(widthList)):
                tHeight = widthList[j]
                size = tWidth * tHeight // 2
                sizeList.append((size,tWidth,tHeight))
        for i in range(len(sizeList)):
            info = sizeList[i]
            if info[0] == buffSize:
                width = info[1] 
                height = info[2]
                if (width // height) == 2 or (height // width) == 2:
                    return (info[1],info[2])
            
    
    return (tWidth,tWidth) 


