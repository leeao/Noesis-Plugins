#Just Dance WII Textures Noesis plugin.
#Author: Allen

from inc_noesis import *

import math
def registerNoesisTypes():
    handle = noesis.register("Just Dance WII Textures",".s3")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadRGBA(handle, noepyLoadRGBA)
    noesis.logPopup()
    return 1
def noepyCheckType(data):
        return 1
def noepyLoadRGBA(data, texList):
        bs = NoeBitStream(data,NOE_BIGENDIAN)	
        ctx = rapi.rpgCreateContext()
        
        width = int(math.sqrt(bs.getSize() * 2))
        height = width
        pixelBuff = bs.readBytes(bs.getSize())
        
        texData = UnswizzleCMPR(pixelBuff,width,height)
        texData = rapi.imageDecodeDXT(texData,width,height,noesis.NOESISTEX_DXT1)
        texData = rapi.imageFlipRGBA32(texData,width,height,0,1)
        texture = NoeTexture(rapi.getInputName(), width, height, texData, noesis.NOESISTEX_RGBA32)
        texList.append(texture)          
                        
        return 1
        
        
def UnswizzleCMPR(pixel,width,height):

    Tile_Width = 2
    Tile_Height = 2
    DxtBlock_Width = 4
    DxtBlockSize = 8
    
    numBlockWidth = width // 8
    numBlockHeight = height // 8    
    
    tileSize = Tile_Width * Tile_Height * DxtBlockSize
    lineSize = Tile_Width * DxtBlockSize
    
    untileData = bytearray(len(pixel))  
    
    for y in range(0,numBlockHeight):            
        for x in range(0,numBlockWidth):                            
            dataPtr = (y * numBlockWidth + x ) * tileSize 
            for ty in range(0,Tile_Height):
                curHeight = y * Tile_Height +  ty             
                dstIndex = (curHeight * numBlockWidth + x) * lineSize
                srcIndex = dataPtr + ty * lineSize
                for p in range(Tile_Width):
                    untileData[dstIndex+p*DxtBlockSize] = pixel[srcIndex+p*DxtBlockSize+1]
                    untileData[dstIndex+p*DxtBlockSize+1] = pixel[srcIndex+p*DxtBlockSize]
                    untileData[dstIndex+p*DxtBlockSize+2] = pixel[srcIndex+p*DxtBlockSize+3]
                    untileData[dstIndex+p*DxtBlockSize+3] = pixel[srcIndex+p*DxtBlockSize+2]
                    for i in range(4,8):
                        index = pixel[srcIndex+p*DxtBlockSize+i]
                        swapIndex = (((index >> 6) & 0x3) | (((index >> 4) & 0x3) << 2)| (((index >> 2) & 0x3) << 4) | ((index & 0x3) << 6)) 
                        untileData[dstIndex+p*DxtBlockSize+i] = swapIndex
            
    return untileData